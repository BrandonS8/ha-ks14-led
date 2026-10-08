# KS14 LED for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/BrandonS8/ha-ks14-led?style=for-the-badge)](https://github.com/BrandonS8/ha-ks14-led/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Control KeepSmile **KS14~** LED controllers over Bluetooth Low Energy from Home Assistant — on/off, RGB color, brightness, and built-in hardware effects. No cloud account required.

---

## Quick install

### 1. Add with HACS (recommended)

If you already have [HACS](https://hacs.xyz/) installed, click:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=BrandonS8&repository=ha-ks14-led&category=integration)

Or add it manually:

1. Open **HACS** → **Integrations**
2. Tap the three dots (⋮) → **Custom repositories**
3. Repository: `https://github.com/BrandonS8/ha-ks14-led`
4. Category: **Integration**
5. Click **Add**, then install **KS14 LED**
6. **Restart** Home Assistant

### 2. Add the integration

After the restart, click:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ks14_led)

Or go to **Settings → Devices & services → Add integration → KS14 LED**, pick your light, and finish the setup.

---

## Before you start

| Need | Details |
|------|---------|
| Home Assistant | 2024.1 or newer |
| Bluetooth | USB adapter on the HA host, **or** an [ESPHome / Shelly Bluetooth Proxy](https://www.home-assistant.io/integrations/bluetooth/) near the strip |
| Device | Powered on and advertising as `KS14…` |

**One connection only.** KS14~ controllers usually allow a single BLE client. Close the KeepSmile / AlfoLive phone app and any desktop KS14 controller before Home Assistant connects.

---

## Manual install (without HACS)

1. Download this repo (Code → Download ZIP) or clone it
2. Copy the folder `custom_components/ks14_led` into your Home Assistant `config/custom_components/` directory  
   Final path should look like: `config/custom_components/ks14_led/manifest.json`
3. Restart Home Assistant
4. **Settings → Devices & services → Add integration → KS14 LED**

---

## Setup guide

1. Put the light in range of HA Bluetooth or a Bluetooth Proxy
2. Disconnect any phone/desktop apps from the light
3. Install this integration (HACS button above, or manual steps)
4. Restart Home Assistant
5. Add **KS14 LED** from the integrations UI (or use the config-flow button)
6. Select your `KS14~` device from the list
7. Control it like any other light entity (color, brightness, effects)

### What you get

| Control | Behavior |
|---------|----------|
| On / Off | Power packets over BLE |
| RGB color | Turns on, then sets color |
| Brightness | Device scale 1–100 (mapped from HA 0–255) |
| Effects | Hardware scenes (breathe, chase, rainbow, flash, …) |

When an effect is running, brightness is capped at **99%**. At 100% the firmware ignores mode packets.

**Not in v1:** mic / rhythm modes, LED bead count, Wi‑Fi / Tuya / Monster controllers.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| No devices found | Enable Bluetooth or a proxy; power the light; close other apps |
| Cannot connect | Move a proxy closer; power-cycle the strip; forget the light in the phone app |
| Entity state looks wrong | State is optimistic (last HA command). Toggle once from HA to resync |
| Works then drops | Something else reconnected (phone app). Disable auto-connect there |

---

## Protocol notes

Commands are AlfoLive / KeepSmile **E3xx** packets on GATT service `AFD0`, write characteristic `AFD1`. Packet builders were ported from the Universal BLE LED Controller project (`ks14.rs` / `led_menu.py`).

---

## Support

- Issues: [github.com/BrandonS8/ha-ks14-led/issues](https://github.com/BrandonS8/ha-ks14-led/issues)
- License: [MIT](LICENSE)
