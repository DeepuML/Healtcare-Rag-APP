"""
Utilities subpackage.

Provides shared helper utilities used across the application.

Exports:
    get_logger - Returns a configured :class:`logging.Logger` instance
                 with a console handler pre-attached, using the log
                 level defined in ``settings.LOG_LEVEL``.
"""

from .logger import get_logger

__all__ = ["get_logger"]
