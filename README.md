# KS14 LED for Home Assistant

Control KeepSmile **KS14~** LED controllers over Bluetooth Low Energy — on/off, RGB color, brightness, and built-in hardware effects. No cloud, no phone app required once set up.

Protocol reverse-engineered from the AlfoLive / KeepSmile app (E3xx packets on GATT `AFD0` / `AFD1`). Packet builders were ported from the Universal BLE LED Controller desktop/CLI work (`ks14.rs` / `led_menu.py`).

## Requirements

- Home Assistant 2024.1 or newer
- Bluetooth adapter on the HA host **or** an [ESPHome / Shelly Bluetooth Proxy](https://www.home-assistant.io/integrations/bluetooth/) near the light
- The KS14~ must be powered and advertising as `KS14…`

**Important:** These controllers usually allow only **one** BLE connection. Close the KeepSmile / AlfoLive phone app and any desktop KS14 controller before using Home Assistant.

## Install with HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add this repository URL as category **Integration**
3. Install **KS14 LED**
4. Restart Home Assistant
5. Settings → Devices & services → Add integration → **KS14 LED**

## Manual install

1. Copy `custom_components/ks14_led` into your Home Assistant `config/custom_components/` folder
2. Restart Home Assistant
3. Settings → Devices & services → Add integration → **KS14 LED**

## Features

| Control | Notes |
|---------|--------|
| On / Off | `E300` power packets |
| RGB color | Sends power-on, then color |
| Brightness | Device scale 1–100 (mapped from HA 0–255) |
| Effects | Hardware dream scenes (breathe, chase, rainbow, …) |

When an effect is active, brightness is capped at 99% — at 100% the firmware ignores mode packets.

**Not supported (yet):** mic / rhythm modes, LED bead count config, Wi‑Fi / Tuya / Monster controllers.

## Troubleshooting

- **No devices found** — Confirm Bluetooth or a proxy is active, the light is on, and nothing else is connected to it.
- **Cannot connect** — Move a proxy closer; power-cycle the strip; forget the light in the phone app so it stops reconnecting.
- **Entity state wrong after phone use** — State is optimistic (last command from HA). Toggle once from HA to resync.

## License

MIT — see [LICENSE](LICENSE).
