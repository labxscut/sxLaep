"""Tests for sxlaep --input / --output shorthand (bundled model)."""

from __future__ import annotations

from pathlib import Path

import pytest

from support_paths import bundled_ubj_path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS = REPO_ROOT / "tests"
ENZ = TESTS / "enzyme_example.fasta"
BUNDLED_UBJ = bundled_ubj_path()


@pytest.mark.skipif(BUNDLED_UBJ is None, reason="bundled enzyme_xgb_model.ubj not in tree/package")
def test_cli_shorthand_input_writes_csv(tmp_path: Path) -> None:
    from sxlaep.cli import main

    out = tmp_path / "out.csv"
    main(["--input", str(ENZ), "--output", str(out)])
    assert out.is_file()
    text = out.read_text()
    assert "pred_label" in text
    assert "enzyme_probability" in text


def test_cli_shorthand_rejects_combine_with_predict() -> None:
    from sxlaep.cli import main

    with pytest.raises(SystemExit):
        main(["--input", str(ENZ), "predict", "--model", "x", "--fasta", str(ENZ)])
