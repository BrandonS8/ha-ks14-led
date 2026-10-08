"""KS14 LED light entity."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .ble import KS14BleDevice
from .const import DEFAULT_EFFECT_SPEED, DOMAIN
from . import protocol

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KS14 light from a config entry."""
    device: KS14BleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KS14LightEntity(device, entry)])


class KS14LightEntity(LightEntity, RestoreEntity):
    """Optimistic RGB light for a KS14~ controller."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, device: KS14BleDevice, entry: ConfigEntry) -> None:
        self._device = device
        self._attr_unique_id = device.address
        self._attr_device_info = DeviceInfo(
            name=entry.title or device.name,
            manufacturer="KeepSmile",
            model="KS14~",
            connections={(dr.CONNECTION_BLUETOOTH, device.address)},
        )
        self._attr_is_on = False
        self._attr_brightness = 255
        self._attr_rgb_color = (255, 255, 255)
        self._attr_effect_list = protocol.EFFECT_NAMES
        self._attr_effect = None
        self._ks14_level = 100

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is None:
            return
        self._attr_is_on = last.state == "on"
        if (bri := last.attributes.get("brightness")) is not None:
            self._attr_brightness = int(bri)
            self._ks14_level = protocol.ha_brightness_to_ks14(int(bri))
        if (rgb := last.attributes.get("rgb_color")) is not None:
            self._attr_rgb_color = tuple(rgb)  # type: ignore[assignment]
        if (effect := last.attributes.get("effect")) is not None:
            self._attr_effect = effect
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS, self._attr_brightness or 255)
        self._attr_brightness = brightness
        self._ks14_level = protocol.ha_brightness_to_ks14(brightness)

        if effect := kwargs.get(ATTR_EFFECT):
            mode_id = protocol.EFFECT_BY_NAME.get(effect)
            if mode_id is None:
                _LOGGER.warning("Unknown effect: %s", effect)
            else:
                await self._device.async_set_power(True)
                await self._device.async_set_effect(
                    mode_id, DEFAULT_EFFECT_SPEED, self._ks14_level
                )
                self._attr_effect = effect
                self._attr_is_on = True
                # Reflect clamped brightness used for effects
                clamped = protocol.effect_level(self._ks14_level)
                self._ks14_level = clamped
                self._attr_brightness = protocol.ks14_brightness_to_ha(clamped)
                self.async_write_ha_state()
                return

        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            self._attr_rgb_color = rgb
            await self._device.async_set_color(*rgb, turn_on=True)
            await self._device.async_set_brightness(self._ks14_level)
            self._attr_effect = None
            self._attr_is_on = True
            self.async_write_ha_state()
            return

        if ATTR_BRIGHTNESS in kwargs:
            if not self._attr_is_on:
                await self._device.async_set_power(True)
            await self._device.async_set_brightness(self._ks14_level)
            self._attr_is_on = True
            self.async_write_ha_state()
            return

        await self._device.async_set_power(True)
        if self._attr_rgb_color:
            await self._device.async_set_color(*self._attr_rgb_color, turn_on=False)
        await self._device.async_set_brightness(self._ks14_level)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.async_set_power(False)
        self._attr_is_on = False
        self.async_write_ha_state()
