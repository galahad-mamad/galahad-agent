"""Tests for the Galahad-Galahad-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"galahad"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``galahad-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "galahad" tag namespace.

``is_galahad_galahad_non_agentic`` should only match the actual Galahad
Galahad-3 / Galahad-4 chat family.
"""

from __future__ import annotations

import pytest

from galahad_cli.model_switch import (
    _GALAHAD_MODEL_WARNING,
    _check_galahad_model_warning,
    is_galahad_galahad_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "galahad-mamad/Galahad-3-Llama-3.1-70B",
        "galahad-mamad/Galahad-3-Llama-3.1-405B",
        "galahad-3",
        "Galahad-3",
        "galahad-4",
        "galahad-4-405b",
        "galahad_4_70b",
        "openrouter/galahad3:70b",
        "openrouter/galahad/galahad-4-405b",
        "galahad-mamad/Galahad3",
        "galahad-3.1",
    ],
)
def test_matches_real_galahad_galahad_chat_models(model_name: str) -> None:
    assert is_galahad_galahad_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Galahad Galahad 3/4"
    )
    assert _check_galahad_model_warning(model_name) == _GALAHAD_MODEL_WARNING


