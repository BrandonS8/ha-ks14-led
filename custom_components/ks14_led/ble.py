"""Persistent BLE client for KS14~ controllers."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import WRITE_CHAR_UUID
from . import protocol

_LOGGER = logging.getLogger(__name__)


class KS14BleDevice:
    """Maintain a GATT connection and send E3 protocol writes."""

    def __init__(self, hass: HomeAssistant, address: str, name: str) -> None:
        self.hass = hass
        self.address = address.upper()
        self.name = name
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()
        self._disconnect_callbacks: list[Callable[[], None]] = []

    def register_disconnect_callback(self, callback: Callable[[], None]) -> None:
        self._disconnect_callbacks.append(callback)

    def _on_disconnected(self, client: BleakClient) -> None:
        _LOGGER.debug("%s disconnected", self.address)
        self._client = None
        for callback in self._disconnect_callbacks:
            callback()

    async def async_connect(self) -> None:
        """Ensure a live connection (idempotent)."""
        async with self._lock:
            await self._ensure_connected()

    async def async_disconnect(self) -> None:
        async with self._lock:
            if self._client and self._client.is_connected:
                await self._client.disconnect()
            self._client = None

    async def _ensure_connected(self) -> None:
        if self._client and self._client.is_connected:
            return

        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if not ble_device:
            raise RuntimeError(
                f"Device {self.address} not found — is Bluetooth/proxy in range?"
            )

        _LOGGER.debug("Connecting to %s (%s)", self.name, self.address)
        self._client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            self.name,
            disconnected_callback=self._on_disconnected,
        )

    async def _write(self, payload: bytes) -> None:
        async with self._lock:
            await self._ensure_connected()
            assert self._client is not None
            await self._client.write_gatt_char(
                WRITE_CHAR_UUID, payload, response=False
            )

    async def async_set_power(self, on: bool) -> None:
        await self._write(protocol.power(on))

    async def async_set_brightness(self, level: int) -> None:
        await self._write(protocol.brightness(level))

    async def async_set_color(self, r: int, g: int, b: int, *, turn_on: bool = True) -> None:
        if turn_on:
            await self._write(protocol.power(True))
            await asyncio.sleep(0.05)
        await self._write(protocol.color(r, g, b))

    async def async_set_effect(self, mode_number: int, speed: int, level: int) -> None:
        # Firmware ignores mode packets when brightness is at 100.
        await self._write(protocol.brightness(protocol.effect_level(level)))
        await asyncio.sleep(0.05)
        await self._write(protocol.mode(mode_number, speed=speed))

    async def async_probe(self) -> None:
        """Connect briefly to verify the device is reachable."""
        await self.async_connect()
        await self.async_disconnect()
