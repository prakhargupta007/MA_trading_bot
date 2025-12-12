"""
Runtime feature column resolution for ML pipelines.

Prefers an explicit environment variable (MA_TRADING_BOT_FEATURE_COLUMNS),
then config.DEFAULT_FEATURE_COLUMNS. Cache persists within process.
"""

import json
import os
from typing import Iterable, List, Optional, Sequence

ENV_VAR_NAME = "MA_TRADING_BOT_FEATURE_COLUMNS"
_cached_columns: Optional[List[str]] = None


def _ensure_valid_sequence(columns: Sequence[str]) -> List[str]:
    if columns is None:
        raise ValueError("feature_columns cannot be None.")
    normalized = [str(col) for col in columns if str(col).strip()]
    if not normalized:
        raise ValueError("feature_columns must contain at least one column name.")
    return normalized


def _parse_env_columns(raw_value: str) -> List[str]:
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {ENV_VAR_NAME}: {raw_value}"
        ) from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(
            f"{ENV_VAR_NAME} must be a JSON list of strings, got: {raw_value}"
        )
    return [item for item in parsed if item]


def _load_from_config() -> Optional[List[str]]:
    try:
        from config import DEFAULT_FEATURE_COLUMNS  # type: ignore
    except ImportError:
        DEFAULT_FEATURE_COLUMNS = None
    except AttributeError:
        DEFAULT_FEATURE_COLUMNS = None

    if DEFAULT_FEATURE_COLUMNS:
        return _ensure_valid_sequence(DEFAULT_FEATURE_COLUMNS)
    return None


def set_runtime_feature_columns(columns: Sequence[str]) -> List[str]:
    """
    Persist feature columns for the current process and any spawned subprocesses.
    """
    global _cached_columns
    normalized = _ensure_valid_sequence(columns)
    os.environ[ENV_VAR_NAME] = json.dumps(normalized)
    _cached_columns = list(normalized)
    return _cached_columns


def get_active_feature_columns(allow_empty: bool = False) -> List[str]:
    """
    Resolve the feature columns for the current runtime.
    Prefers an explicit environment variable, then config.DEFAULT_FEATURE_COLUMNS.
    """
    global _cached_columns

    if _cached_columns is not None:
        if not _cached_columns and not allow_empty:
            raise ValueError("feature_columns cache is empty.")
        return list(_cached_columns)

    env_value = os.environ.get(ENV_VAR_NAME)
    if env_value:
        columns = _parse_env_columns(env_value)
        _cached_columns = columns
        if columns or allow_empty:
            return list(columns)
        raise ValueError("Environment provided feature_columns is empty.")

    config_columns = _load_from_config()
    if config_columns is not None:
        _cached_columns = config_columns
        if config_columns or allow_empty:
            return list(config_columns)
        raise ValueError("config.DEFAULT_FEATURE_COLUMNS is empty.")

    if allow_empty:
        _cached_columns = []
        return []

    raise RuntimeError(
        "Feature columns are not configured. "
        f"Set {ENV_VAR_NAME} or define DEFAULT_FEATURE_COLUMNS in config.py."
    )


def resolve_feature_columns(feature_columns: Optional[Iterable[str]]) -> List[str]:
    """
    Utility helper for modules that accept an optional feature list.
    """
    if feature_columns is not None:
        return _ensure_valid_sequence(list(feature_columns))
    return get_active_feature_columns()
