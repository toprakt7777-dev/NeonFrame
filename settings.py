"""Persistent user settings."""
import json
import os

DEFAULTS = {"overlay_enabled": True, "detection_enabled": True, "opacity": 85,
            "confidence": 50, "box_color": "#00ffd2", "sampling": 0}


def settings_path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    return os.path.join(base, "NeonFrame", "settings.json")


def load_settings(path=None):
    try:
        with open(path or settings_path(), encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
    except (OSError, ValueError, TypeError):
        return DEFAULTS.copy()


def save_settings(values, path=None):
    target = path or settings_path()
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump({**DEFAULTS, **values}, f, indent=2)
