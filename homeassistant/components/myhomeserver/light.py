from __future__ import annotations

from typing import Any

from myhome._gen.model.object_value_dimmer import ObjectValueDimmer
from myhome._gen.model.object_value_light import ObjectValueLight
import myhome.object
import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, LOGGER

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME, default="admin"): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up MyHomeSERVER lights from a config entry."""

    hub = hass.data[DOMAIN][config_entry.entry_id]

    server_serial = await hass.async_add_executor_job(hub.get_server_serial)
    lights = [
        MyHomeServerLight(server_serial, light)
        for light in await hass.async_add_executor_job(hub.lights)
    ]
    LOGGER.debug("Found %d lights" % (len(lights),))
    LOGGER.debug(f"Lights: {lights!r},")

    if len(lights) > 0:
        async_add_entities(lights)

    return True


def myhomeserver_brightness_to_hass(value: int):
    """Convert MyHomeSERVER brightness (0..100) to hass format (0..255)"""
    return int((value / 100.0) * 255)


class MyHomeServerLight(LightEntity):
    def __init__(self, server_serial: str, light: myhome.object.Light):
        self._light = light
        self._server_serial = server_serial
        self._value: ObjectValueLight | ObjectValueDimmer | None = None

    @property
    def name(self) -> str | None:
        return self._light.name

    @property
    def supported_features(self) -> int:
        if isinstance(self._light, myhome.object.Dimmer):
            return SUPPORT_BRIGHTNESS
        return 0

    @property
    def unique_id(self) -> str | None:
        return "%s_%d" % (self._server_serial, self._light.id)

    @property
    def is_on(self) -> bool:
        if isinstance(self._light, myhome.object.Dimmer):
            return self._value is not None and self._value.dimmer > 0
        return self._value is not None and self._value.power

    def brightness(self) -> int | None:
        if isinstance(self._light, myhome.object.Dimmer):
            return myhomeserver_brightness_to_hass(self._value.dimmer)
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._light.switch_on)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._light.switch_off)

    async def async_update(self):
        LOGGER.debug(f"async_update called for {self.unique_id}")
        self._value = await self.hass.async_add_executor_job(self._light.get_value)
