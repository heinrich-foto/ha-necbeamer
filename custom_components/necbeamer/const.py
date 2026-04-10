"""Constants for the NEC Beamer LAN integration."""

DOMAIN = "necbeamer"

CONF_STATE_VERIFY_DELAYS = "state_verify_delays"
CONF_BRIGHTNESS_FULL_THRESHOLD = "brightness_full_threshold"
CONF_BRIGHTNESS_BLACK_LEVEL = "brightness_black_level"

DEFAULT_STATE_VERIFY_DELAYS: list[float] = [2.0, 6.0]
DEFAULT_BRIGHTNESS_FULL_THRESHOLD = 255
DEFAULT_BRIGHTNESS_BLACK_LEVEL = 1
