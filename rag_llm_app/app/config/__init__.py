"""
Configuration subpackage.

Exposes the global ``settings`` singleton which is pre-populated from
environment variables (and an optional ``.env`` file) at import time.

Usage::

    from app.config import settings
    print(settings.MODEL_BACKEND)
"""

from .settings import settings

__all__ = ["settings"]
