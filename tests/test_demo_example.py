"""Demo-style smoke test: bundled model + repository FASTA inputs.

Both ``enzyme_example.fasta`` and ``noenzyme_example.fasta`` live under ``tests/``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from support_paths import bundled_ubj_path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS = REPO_ROOT / "tests"
BUNDLED_UBJ = bundled_ubj_path()


@pytest.mark.skipif(BUNDLED_UBJ is None, reason="bundled enzyme_xgb_model.ubj not in installed package")
def test_demo_predict_on_fixture_fastas():
    from sxlaep.fasta import read_fasta_records
    from sxlaep.model import load_model, predict_sequences

    enzyme_fa = TESTS / "enzyme_example.fasta"
    noez_fa = TESTS / "noenzyme_example.fasta"
    assert enzyme_fa.is_file() and noez_fa.is_file()

    model = load_model(BUNDLED_UBJ)
    records = read_fasta_records(enzyme_fa) + read_fasta_records(noez_fa)
    seqs = [r.sequence for r in records]
    out = predict_sequences(model, seqs)

    assert len(out) == 2
    assert set(out["pred_label"].tolist()) <= {0, 1}
    assert (out["enzyme_probability"] >= 0).all() and (out["enzyme_probability"] <= 1).all()
