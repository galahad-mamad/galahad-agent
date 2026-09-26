"""Resolve GALAHAD_HOME for standalone skill scripts.

Skill scripts may run outside the Galahad process (e.g. system Python,
nix env, CI) where ``galahad_constants`` is not importable.  This module
provides the same ``get_galahad_home()`` and ``display_galahad_home()``
contracts as ``galahad_constants`` without requiring it on ``sys.path``.

When ``galahad_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``galahad_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``GALAHAD_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from galahad_constants import display_galahad_home as display_galahad_home
    from galahad_constants import get_galahad_home as get_galahad_home
except (ModuleNotFoundError, ImportError):

    def get_galahad_home() -> Path:
        """Return the Galahad home directory (default: ~/.galahad).

        Mirrors ``galahad_constants.get_galahad_home()``."""
        val = os.environ.get("GALAHAD_HOME", "").strip()
        return Path(val) if val else Path.home() / ".galahad"

    def display_galahad_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``galahad_constants.display_galahad_home()``."""
        home = get_galahad_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
