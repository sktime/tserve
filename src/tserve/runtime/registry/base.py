"""Shared type alias for model catalogs.

A registry maps a catalog id to a nested metadata dict. Nothing in a
catalog is loaded until ``bootstrap(model)`` / ``--model``.
"""

from typing import Any

BASE_REGISTRY_TYPE = dict[str, dict[str, Any]]
"""Type alias for a catalog: model id → nested metadata dict."""
