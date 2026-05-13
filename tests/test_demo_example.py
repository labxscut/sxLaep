"""Demo-style smoke test: bundled model + repository FASTA fixtures.

Former `examples/*.fasta` inputs now live under ``tests/fixtures/``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
BUNDLED_UBJ = REPO_ROOT / "sxlaep" / "enzyme_xgb_model.ubj"


@pytest.mark.skipif(not BUNDLED_UBJ.is_file(), reason="bundled enzyme_xgb_model.ubj not in tree")
def test_demo_predict_on_fixture_fastas():
    from sxlaep.fasta import read_fasta_records
    from sxlaep.model import load_model, predict_sequences

    enzyme_fa = FIXTURES / "enzyme_example.fasta"
    noez_fa = FIXTURES / "noenzyme_example.fasta"
    assert enzyme_fa.is_file() and noez_fa.is_file()

    model = load_model(BUNDLED_UBJ)
    records = read_fasta_records(enzyme_fa) + read_fasta_records(noez_fa)
    seqs = [r.sequence for r in records]
    out = predict_sequences(model, seqs)

    assert len(out) == 2
    assert set(out["pred_label"].tolist()) <= {0, 1}
    assert (out["enzyme_probability"] >= 0).all() and (out["enzyme_probability"] <= 1).all()
