"""Platform for light integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from async_nec_beamer import Nec_Beamer

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    SUPPORT_BRIGHTNESS,
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    LightEntity,
)
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger("necbeamer")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Required(CONF_IP_ADDRESS): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Godox Light platform."""
    # Add devices
    _LOGGER.info(pformat(config))

    light = {"name": config[CONF_NAME], "ip_address": config[CONF_IP_ADDRESS]}

    add_entities([NecBeamerLight(light)])


class NecBeamerLight(LightEntity):
    """Representation of an Godox Light."""

    def __init__(self, light) -> None:
        """Initialize an GodoxLight."""
        _LOGGER.info(pformat(light))
        self._light = Nec_Beamer(ip_address=light["ip_address"], name=light["name"])
        self._name = light["name"]
        self._state = None
        self._brightness = 255

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        self._state = self._light.is_on
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""

        # if ATTR_BRIGHTNESS in kwargs:
        #    await self._light.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))

        # result = await self.hass.async_add_executor_job(self._light.turn_on)
        # _LOGGER.info(pformat(result))
        self.hass.async_run_job(self._light.turn_on)
        # await self._light.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""

        # await self.hass.async_add_executor_job(self._light.turn_off)
        self.hass.async_run_job(self._light.turn_off)
        # await self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.hass.async_run_job(self._light.update)

        self._state = self._light.is_on
        # self._brightness = self._light.brightness
