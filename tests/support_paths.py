"""Shared helpers for tests (not pytest plugins)."""

from __future__ import annotations

from pathlib import Path


def bundled_ubj_path() -> Path | None:
    """Return path to packaged ``enzyme_xgb_model.ubj`` (wheel / pipx) or editable tree."""

    import sxlaep

    p = Path(sxlaep.__file__).resolve().parent / "enzyme_xgb_model.ubj"
    return p if p.is_file() else None
