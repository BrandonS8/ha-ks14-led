"""The KS14 LED integration."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .ble import KS14BleDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KS14 LED from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    name = entry.title or (ble_device.name if ble_device else "KS14~")

    device = KS14BleDevice(hass, address, name)

    try:
        await device.async_connect()
    except Exception as err:
        raise ConfigEntryNotReady(
            f"Unable to connect to {name} ({address}): {err}"
        ) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_stop(_event: Event) -> None:
        await device.async_disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        device: KS14BleDevice = hass.data[DOMAIN].pop(entry.entry_id)
        await device.async_disconnect()
    return unload_ok
