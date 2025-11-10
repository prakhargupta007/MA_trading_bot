import importlib
from contextlib import contextmanager
from pathlib import Path

import config as config_module

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config.py"


def patch_config_values(updates: dict):
    """
    Safely update simple top-level assignments in config.py.
    """
    lines = CONFIG_PATH.read_text().splitlines(keepends=True)
    new_lines = []
    for line in lines:
        stripped = line.strip()
        replaced = False
        for key, value in updates.items():
            if stripped.startswith(f"{key} =") or stripped.startswith(f"{key}="):
                indent = len(line) - len(line.lstrip(" "))
                new_lines.append(" " * indent + f"{key} = {value}\n")
                replaced = True
                break
        if not replaced:
            new_lines.append(line)

    CONFIG_PATH.write_text("".join(new_lines))


def reload_config():
    return importlib.reload(config_module)


def get_training_mode() -> bool:
    return bool(getattr(config_module, "TRAINING_MODE", False))


def set_training_mode(enabled: bool):
    patch_config_values({"TRAINING_MODE": "True" if enabled else "False"})
    reload_config()


@contextmanager
def temporary_training_mode(force_enabled: bool = True):
    previous = get_training_mode()
    changed = previous != force_enabled
    if changed:
        set_training_mode(force_enabled)
    try:
        yield
    finally:
        if changed:
            set_training_mode(previous)
