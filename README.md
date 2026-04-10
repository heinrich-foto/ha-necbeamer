# NEC Beamer

Activate via `configuration.yaml`; configuration flow is not supported.

## Minimal configuration

```yaml
light:
  - platform: necbeamer
    name: "NEC Beamer"
    ip_address: "192.168.0.175"
```

## Optional YAML options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `state_verify_delays` | list of seconds | `[2, 6]` | After `turn_on` / `turn_off`, the integration polls the projector again after each delay (empty list = no extra polls). |
| `brightness_full_threshold` | int 1–255 | `255` | When turning on with `brightness` **≥** this value (or no brightness), the picture is **unmuted**. Below = picture muted (black screen). Use e.g. `250` if the UI sends slightly less than 255 for “100%”. |
| `brightness_black_level` | int 1–254 | `1` | HA **reported** brightness when the lamp is on and the picture is muted (black). Lets you tune how the slider looks when the image is blanked. |

### Example with all options

```yaml
light:
  - platform: necbeamer
    name: "NEC Beamer"
    ip_address: "192.168.0.175"
    state_verify_delays:
      - 3
      - 8
      - 15
    brightness_full_threshold: 250
    brightness_black_level: 64
```

If `brightness_full_threshold` is not greater than `brightness_black_level`, a warning is logged; behaviour may not match the UI.

---

NEC Beamer NP2000 is tested with this integration. It uses the projector web UI over HTTP.

## Behaviour (summary)

- **Brightness ≥ full threshold (or turn on without brightness):** lamp on, picture on.
- **Brightness between 1 and (full threshold − 1):** lamp on, picture muted (black), lamp stays on.
- **Brightness 0 or turn off:** projector **power off**.
- Requires Python package `async_nec_beamer` (see `manifest.json`; **0.2.3** on PyPI or manual install in the HA environment).
