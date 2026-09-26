"""Resolve GALAHAD_HOME for standalone skill scripts.

Skill scripts may run outside the Galahad process (system Python, nix env,
CI) where ``galahad_constants`` is not importable.  This module provides the
same ``get_galahad_home()`` contract without requiring it on ``sys.path``.

When ``galahad_constants`` IS available it is used directly so profile
resolution and any future enhancements are picked up automatically.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from galahad_constants import get_galahad_home as get_galahad_home
except (ModuleNotFoundError, ImportError):

    def get_galahad_home() -> Path:
        """Return the Galahad home directory (default: ``~/.galahad``)."""
        val = os.environ.get("GALAHAD_HOME", "").strip()
        return Path(val) if val else Path.home() / ".galahad"
