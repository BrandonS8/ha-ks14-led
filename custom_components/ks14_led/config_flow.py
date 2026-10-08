"""Config flow for KS14 LED."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant

from .ble import KS14BleDevice
from .const import DOMAIN, LOCAL_NAME_PREFIX

_LOGGER = logging.getLogger(__name__)


def _is_ks14(name: str | None) -> bool:
    return bool(name and name.startswith(LOCAL_NAME_PREFIX))


async def _async_probe(hass: HomeAssistant, address: str, name: str) -> None:
    device = KS14BleDevice(hass, address, name)
    await device.async_probe()


class KS14LedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KS14 LED."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle Bluetooth discovery."""
        if not _is_ks14(discovery_info.name):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a discovered device."""
        assert self._discovery_info is not None
        if user_input is not None:
            return await self._async_create_from_discovery(self._discovery_info)

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovery_info.name or self._discovery_info.address
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user pick a discovered KS14 device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery = self._discovered[address]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            try:
                await _async_probe(
                    self.hass, address, discovery.name or "KS14~"
                )
            except Exception:  # noqa: BLE001 — surface as cannot_connect
                _LOGGER.exception("Failed to connect to %s", address)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=discovery.name or address,
                    data={CONF_ADDRESS: address},
                )

        current = self._async_current_ids(include_ignore=False)
        for discovery in async_discovered_service_info(self.hass, connectable=True):
            if (
                discovery.address in current
                or discovery.address in self._discovered
                or not _is_ks14(discovery.name)
            ):
                continue
            self._discovered[discovery.address] = discovery

        if not self._discovered:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            addr: f"{info.name} ({addr})"
                            for addr, info in self._discovered.items()
                        }
                    )
                }
            ),
            errors=errors,
        )

    async def _async_create_from_discovery(
        self, discovery: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        try:
            await _async_probe(
                self.hass, discovery.address, discovery.name or "KS14~"
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to connect to %s", discovery.address)
            return self.async_abort(reason="cannot_connect")

        return self.async_create_entry(
            title=discovery.name or discovery.address,
            data={CONF_ADDRESS: discovery.address},
        )
