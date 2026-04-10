"""The NEC Beamer LAN integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

# Preload light platform with package import so the module is not first loaded
# via import_module on the event loop (Home Assistant 2024.7+).
from . import light as _necbeamer_light  # noqa: F401


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the necbeamer integration (YAML platforms)."""
    return True
