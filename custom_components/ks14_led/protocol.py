"""KS14~ BLE protocol (AlfoLive d3.b / E3xx).

Ported from the Universal BLE LED Controller project (ks14.rs / led_menu.py).
Same GATT as KS03~ (AFD0/AFD1) but a different command set — not 5A/5B.
"""

from __future__ import annotations

from .const import DEFAULT_EFFECT_CLASS, DEFAULT_EFFECT_SPEED

# Curated dream-scene mode numbers from AlfoLive
EFFECT_CATALOG: list[tuple[int, str]] = [
    (0, "Static / soft"),
    (1, "Breathe"),
    (2, "Pulse"),
    (3, "Flash"),
    (4, "Strobe"),
    (5, "Jump RGB"),
    (6, "Jump rainbow"),
    (10, "Fade RGB"),
    (15, "Fade rainbow"),
    (23, "Tail chase"),
    (28, "Comet"),
    (39, "Flow left"),
    (45, "Flow right"),
    (57, "Open / close"),
    (65, "Meet in middle"),
    (89, "Forward chase"),
    (101, "Forward wave"),
    (90, "Backward chase"),
    (143, "Sparkle"),
    (150, "Twinkle"),
    (181, "Rainbow cycle"),
    (190, "Rainbow chase"),
    (200, "Party mix"),
]

EFFECT_NAMES = [name for _, name in EFFECT_CATALOG]
EFFECT_BY_NAME = {name: mode_id for mode_id, name in EFFECT_CATALOG}


def effect_level(level: int) -> int:
    """Highest brightness that still lets hardware modes animate (1–99)."""
    return max(1, min(99, level))


def power(on: bool) -> bytes:
    flag = "F0" if on else "0F"
    return bytes.fromhex(f"E300{flag}FFFFFFFFFF3E")


def brightness(level: int) -> bytes:
    """Brightness packet; level is 1–100."""
    level = max(1, min(100, level))
    return bytes.fromhex(f"E100{level:02X}FFFFFFFFFF1E")


def color(r: int, g: int, b: int) -> bytes:
    return bytes.fromhex(f"E401{r:02X}{g:02X}{b:02X}FFFFFF4E")


def mode(
    number: int,
    speed: int = DEFAULT_EFFECT_SPEED,
    class_: int = DEFAULT_EFFECT_CLASS,
) -> bytes:
    """Built-in effect: class (usually 2), mode number, speed 0–100."""
    speed = max(0, min(100, speed))
    return bytes.fromhex(f"E200{class_:02X}{number:02X}{speed:02X}FFFFFF2E")


def ha_brightness_to_ks14(ha_brightness: int) -> int:
    """Map Home Assistant 0–255 brightness to KS14 1–100."""
    return max(1, min(100, round(ha_brightness / 255 * 100)))


def ks14_brightness_to_ha(level: int) -> int:
    """Map KS14 1–100 brightness to Home Assistant 0–255."""
    return max(1, min(255, round(level / 100 * 255)))
