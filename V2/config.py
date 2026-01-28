# -*- coding: utf-8 -*-
"""Config management for ENVI Auto Fill Fields.

Robust config persistence for both:
- numeric add-on IDs (e.g. addons21/1826463337)
- folder-based installs (e.g. addons21/anki_auto_fill_addon)

Why this exists:
Some users copied a custom 'meta.json' into the add-on folder (or installed as a folder),
which can cause Anki's addon manager to not resolve the correct key reliably.
This module therefore:
1) Resolves the correct ADDON_KEY via addonFromModule()
2) Uses Anki's writeConfig/getConfig
3) Also falls back to reading/writing addons21/<addon>/config.json directly to guarantee persistence.
"""

from __future__ import annotations

from aqt import mw
from typing import Dict, Any, Optional
import json
import os


def _resolve_addon_key() -> str:
    """Resolve the add-on key Anki uses to store config."""
    try:
        key = mw.addonManager.addonFromModule(__name__)
        if key:
            return key
    except Exception:
        pass

    # Folder-based fallback (package name == folder name)
    return (__package__ or __name__).split(".")[0]


ADDON_KEY: str = _resolve_addon_key()


DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "overwrite": True,
    "show_pos_in_meanings": True,
    "note_type": "",
    "field_mapping": {
        "word": "",
        "definition": "",
        "pronunciation": "",
        "pos": "",
        "meanings": "",
        "examples": ""
    },
}


def _config_file_path() -> Optional[str]:
    """Return absolute path to addons21/<addon>/config.json if possible."""
    try:
        folder = mw.addonManager.addonFolder(ADDON_KEY)
        return os.path.join(folder, "config.json")
    except Exception:
        return None


def _read_config_file() -> Optional[Dict[str, Any]]:
    path = _config_file_path()
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_config_file(cfg: Dict[str, Any]) -> None:
    path = _config_file_path()
    if not path:
        return
    try:
        # ensure folder exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        # last resort: ignore
        pass


def get_config() -> Dict[str, Any]:
    """Get addon configuration."""
    cfg = None
    try:
        cfg = mw.addonManager.getConfig(ADDON_KEY)
    except Exception:
        cfg = None

    # If Anki doesn't return config yet, try reading config.json directly.
    if cfg is None:
        cfg = _read_config_file()

    if cfg is None:
        cfg = DEFAULT_CONFIG.copy()
        save_config(cfg)

    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    """Save addon configuration (Anki + direct-file fallback)."""
    try:
        mw.addonManager.writeConfig(ADDON_KEY, cfg)
    except Exception:
        # ignore and fall back to direct file
        pass

    # Always also persist directly to config.json to guarantee it exists.
    _write_config_file(cfg)


def is_configured() -> bool:
    """Check if addon is properly configured."""
    cfg = get_config()
    if not cfg.get("note_type"):
        return False
    field_mapping = cfg.get("field_mapping", {}) or {}
    if not field_mapping.get("word"):
        return False
    return True


def get_note_type_name() -> Optional[str]:
    cfg = get_config()
    return cfg.get("note_type") or None


def get_field_mapping() -> Dict[str, str]:
    cfg = get_config()
    return cfg.get("field_mapping", {}) or {}


def is_enabled() -> bool:
    cfg = get_config()
    return bool(cfg.get("enabled", True))


def should_overwrite() -> bool:
    cfg = get_config()
    return bool(cfg.get("overwrite", True))


def show_pos_in_meanings() -> bool:
    cfg = get_config()
    return bool(cfg.get("show_pos_in_meanings", True))
