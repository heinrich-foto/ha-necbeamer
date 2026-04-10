"""Platform for light integration."""
from __future__ import annotations

import asyncio
import logging
from pprint import pformat
from typing import Any

import voluptuous as vol
from async_nec_beamer import Nec_Beamer

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_BRIGHTNESS_BLACK_LEVEL,
    CONF_BRIGHTNESS_FULL_THRESHOLD,
    CONF_STATE_VERIFY_DELAYS,
    DEFAULT_BRIGHTNESS_BLACK_LEVEL,
    DEFAULT_BRIGHTNESS_FULL_THRESHOLD,
    DEFAULT_STATE_VERIFY_DELAYS,
)

_LOGGER = logging.getLogger("necbeamer")

HA_BRIGHTNESS_MAX = 255

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional(
            CONF_STATE_VERIFY_DELAYS,
            default=list(DEFAULT_STATE_VERIFY_DELAYS),
        ): vol.All(
            cv.ensure_list,
            vol.Length(min=0, max=12),
            [vol.All(vol.Coerce(float), vol.Range(min=0, max=600))],
        ),
        vol.Optional(
            CONF_BRIGHTNESS_FULL_THRESHOLD,
            default=DEFAULT_BRIGHTNESS_FULL_THRESHOLD,
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=HA_BRIGHTNESS_MAX)),
        vol.Optional(
            CONF_BRIGHTNESS_BLACK_LEVEL,
            default=DEFAULT_BRIGHTNESS_BLACK_LEVEL,
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=HA_BRIGHTNESS_MAX - 1)),
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the NEC Beamer light platform."""
    _LOGGER.info(pformat(config))

    add_entities([NecBeamerLight(config)])


class NecBeamerLight(LightEntity):
    """Representation of an NEC Beamer as Light."""

    _attr_supported_color_modes: set[ColorMode] = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, config: ConfigType) -> None:
        """Initialize an NEC Beamer."""
        _LOGGER.info(pformat(dict(config)))
        name = config.get(CONF_NAME) or f"necbeamer_{config[CONF_IP_ADDRESS]}"
        self._light = Nec_Beamer(ip_address=config[CONF_IP_ADDRESS], name=name)
        self._name = name
        self._state: bool | None = None
        self._brightness = HA_BRIGHTNESS_MAX
        self._verify_task: asyncio.Task[None] | None = None
        delays = config[CONF_STATE_VERIFY_DELAYS]
        self._state_verify_delays: tuple[float, ...] = tuple(float(x) for x in delays)
        self._brightness_full_threshold: int = config[CONF_BRIGHTNESS_FULL_THRESHOLD]
        self._brightness_black_level: int = config[CONF_BRIGHTNESS_BLACK_LEVEL]
        if self._brightness_full_threshold <= self._brightness_black_level:
            _LOGGER.warning(
                "brightness_full_threshold (%s) should be greater than "
                "brightness_black_level (%s); picture on/off may not match the UI",
                self._brightness_full_threshold,
                self._brightness_black_level,
            )
        self._icons = {
            "off": "mdi:projector",
            "on": "mdi:projector-screen",
            "unavailable": "mdi:projector-off",
        }

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light (0 = off, else black vs. full picture)."""
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if the projector lamp is on."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if the projector web UI is reachable."""
        return self._light.is_available

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        if not self._light.is_available:
            return self._icons["unavailable"]
        if self._state:
            return self._icons["on"]
        return self._icons["off"]

    def _sync_attributes_from_device(self) -> None:
        """Copy lamp/picture state into entity attributes."""
        self._state = self._light.is_on
        if not self._light.is_on:
            self._brightness = 0
        elif self._light.picture_muted:
            self._brightness = self._brightness_black_level
        else:
            self._brightness = HA_BRIGHTNESS_MAX

    def _schedule_state_verification(self) -> None:
        """Re-fetch state after typical projector command delays."""

        if not self._state_verify_delays:
            return

        async def _verify() -> None:
            try:
                for delay in self._state_verify_delays:
                    await asyncio.sleep(delay)
                    await self._light.update()
                    self._sync_attributes_from_device()
                    self.async_write_ha_state()
            except asyncio.CancelledError:
                raise

        if self._verify_task and not self._verify_task.done():
            self._verify_task.cancel()
        if self.hass is not None:
            self._verify_task = self.hass.async_create_task(_verify())

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on: optional brightness maps to picture on vs. black (lamp stays on)."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        if brightness == 0:
            await self.async_turn_off()
            return

        await self._light.turn_on()

        if brightness is None or brightness >= self._brightness_full_threshold:
            await self._light.set_picture_mute(False)
        else:
            await self._light.set_picture_mute(True)

        self._sync_attributes_from_device()
        self.async_write_ha_state()
        self._schedule_state_verification()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off (power)."""
        await self._light.turn_off()
        self._sync_attributes_from_device()
        self.async_write_ha_state()
        self._schedule_state_verification()

    async def async_update(self) -> None:
        """Fetch new state from the projector."""
        await self._light.update()
        self._sync_attributes_from_device()
