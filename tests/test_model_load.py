"""Tests for model load path (native UBJ vs legacy pickle)."""

import pytest

from support_paths import bundled_ubj_path

BUNDLED_UBJ = bundled_ubj_path()


@pytest.mark.skipif(BUNDLED_UBJ is None, reason="bundled enzyme_xgb_model.ubj not in installed package")
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
