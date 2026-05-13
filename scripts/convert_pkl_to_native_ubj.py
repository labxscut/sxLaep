#!/usr/bin/env python3
"""Export a joblib-pickled XGBClassifier to native UBJSON (no pickle/XGBoost skew warnings)."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pkl", type=Path, help="joblib-serialized XGBClassifier (.pkl)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output path (.ubj); default: same basename as input",
    )
    args = parser.parse_args()
    inp = args.input_pkl.resolve()
    out = (args.output or inp.with_suffix(".ubj")).resolve()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="pickle")
        import joblib

        model = joblib.load(inp)
    if not hasattr(model, "save_model"):
        raise SystemExit(f"Loaded object has no save_model: {type(model)}")
    out.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(out))
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
