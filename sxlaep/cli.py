"""Command-line interface for sxLaep."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import FeatureConfig, PROPERTIES
from .model import run_prediction_pipeline


def _bundled_ubj_path() -> Path:
    """Path to packaged native XGBoost model (wheel / pipx layout)."""

    import sxlaep

    p = Path(sxlaep.__file__).resolve().parent / "enzyme_xgb_model.ubj"
    if not p.is_file():
        raise SystemExit(f"Bundled model not found at {p} (expected pip/wheel install).")
    return p


def build_parser() -> argparse.ArgumentParser:
    """Build the sxLaep command-line argument parser."""

    parser = argparse.ArgumentParser(description="sxLaep enzyme/non-enzyme classifier")
    parser.add_argument(
        "-i",
        "--input",
        dest="simple_fasta",
        metavar="FASTA",
        default=None,
        help="Shorthand: predict with the bundled model on this FASTA (no predict subcommand).",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="simple_output",
        metavar="CSV",
        default=None,
        help="With --input only: output CSV path (default: sxlaep_predictions.csv in the current directory).",
    )
    # Feature extraction params — informational in shorthand mode (fixed for bundled model).
    parser.add_argument(
        "--lag", type=int, default=argparse.SUPPRESS,
        help="pseudo-AAC lag (fixed to 10 for bundled model; use `sxlaep predict` to customize)",
    )
    parser.add_argument(
        "--weight", type=float, default=argparse.SUPPRESS,
        help="pseudo-AAC weight (fixed to 0.05 for bundled model; use `sxlaep predict` to customize)",
    )
    parser.add_argument(
        "--segments", type=int, default=argparse.SUPPRESS,
        help="number of window-AAC segments (fixed to 3 for bundled model; use `sxlaep predict` to customize)",
    )
    parser.add_argument(
        "--add-length", dest="simple_add_length", action="store_true", default=argparse.SUPPRESS,
        help="append sequence length (fixed for bundled model; use `sxlaep predict` to customize)",
    )
    parser.add_argument(
        "--no-add-length", dest="simple_add_length", action="store_false", default=argparse.SUPPRESS,
        help="do not append sequence length (fixed for bundled model; use `sxlaep predict` to customize)",
    )
    parser.add_argument(
        "--properties", nargs="*", choices=list(PROPERTIES.keys()), default=argparse.SUPPRESS,
        help="physicochemical properties (fixed to hydro polar charge for bundled model; use `sxlaep predict` to customize)",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    predict = subparsers.add_parser("predict", help="predict enzyme probabilities for FASTA sequences")
    predict.add_argument("--model", required=True, help="trained joblib model path")
    predict.add_argument("--fasta", required=True, help="input FASTA file")
    predict.add_argument("--output", default="results/predictions.csv", help="output CSV path")
    predict.add_argument("--lag", type=int, default=10, help="pseudo-AAC lag (must match training)")
    predict.add_argument("--weight", type=float, default=0.05, help="pseudo-AAC weight (must match training)")
    predict.add_argument("--segments", type=int, default=3, help="number of window-AAC segments (must match training)")
    predict.add_argument("--add-length", dest="add_length", action="store_true", default=True,
                         help="append raw sequence length to feature vector (must match training)")
    predict.add_argument("--no-add-length", dest="add_length", action="store_false",
                         help="do not append sequence length to feature vector")
    predict.add_argument("--properties", nargs="*", choices=list(PROPERTIES.keys()),
                         default=list(PROPERTIES.keys()),
                         help="physicochemical properties for pseudo-AAC (must match training; default: hydro polar charge)")
    predict.add_argument("--n-jobs", type=int, default=1, help="number of parallel workers")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the sxLaep command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.simple_fasta is not None:
        if args.command is not None:
            parser.error("Do not combine --input/--output with predict; use one style only.")
        # Check for feature param overrides in shorthand mode.
        overrides = []
        for attr, name in [("lag", "--lag"), ("weight", "--weight"), ("segments", "--segments"),
                           ("simple_add_length", "--add-length/--no-add-length"),
                           ("properties", "--properties")]:
            if hasattr(args, attr):
                overrides.append(name)
        if overrides:
            print(
                "Warning: feature parameters cannot be changed when using the bundled model "
                "(--input shorthand).\n"
                "The following flags were ignored: " + ", ".join(overrides) + ".\n"
                "Use `sxlaep predict --model <your-model>` to customize feature extraction."
            )
        fasta = Path(args.simple_fasta)
        if not fasta.is_file():
            raise SystemExit(f"Input FASTA not found: {fasta}")
        out = Path(args.simple_output) if args.simple_output else Path.cwd() / "sxlaep_predictions.csv"
        model = _bundled_ubj_path()
        result = run_prediction_pipeline(
            model_path=model,
            fasta_path=fasta,
            output_csv=out,
            n_jobs=1,
        )
        print(f"Predictions saved to {out}. Rows: {len(result)}")
        return

    if args.command is None:
        parser.print_help()
        raise SystemExit(2)

    if args.command == "predict":
        selected_props = {k: PROPERTIES[k] for k in args.properties}
        feature_config = FeatureConfig(
            lag=args.lag, weight=args.weight, n_segments=args.segments,
            add_length=args.add_length, properties=selected_props,
        )
        result = run_prediction_pipeline(
            model_path=args.model,
            fasta_path=args.fasta,
            output_csv=args.output,
            feature_config=feature_config,
            n_jobs=args.n_jobs,
        )
        print(f"Predictions saved to {args.output}. Rows: {len(result)}")
    else:  # pragma: no cover
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
