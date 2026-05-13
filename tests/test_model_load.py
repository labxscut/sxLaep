"""Tests for model load path (native UBJ vs legacy pickle)."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_UBJ = REPO_ROOT / "sxlaep" / "enzyme_xgb_model.ubj"


@pytest.mark.skipif(not BUNDLED_UBJ.is_file(), reason="bundled enzyme_xgb_model.ubj not in tree")
def test_load_native_ubj_no_warning():
    import warnings

    from sxlaep.model import load_model, predict_sequences

    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        model = load_model(BUNDLED_UBJ)
        predict_sequences(model, ["ACDEFGHIKLMNPQRSTVWY"])
    xgb_pickle_msgs = [
        w
        for w in rec
        if "serialized model" in str(w.message).lower() or "booster.save_model" in str(w.message).lower()
    ]
    assert not xgb_pickle_msgs
