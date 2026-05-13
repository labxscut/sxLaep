"""Command-line interface for sxLaep."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import FeatureConfig, TrainingConfig
from .pipeline import run_prediction_pipeline, run_training_pipeline


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
        help="Shorthand: predict with the bundled model on this FASTA (no train/predict subcommand).",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="simple_output",
        metavar="CSV",
        default=None,
        help="With --input only: output CSV path (default: sxlaep_predictions.csv in the current directory).",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    train = subparsers.add_parser("train", help="train an sxLaep classifier")
    train.add_argument("--noenzyme-fasta", required=True, help="FASTA file for non-enzyme proteins")
    train.add_argument("--enzyme-fasta", required=True, help="FASTA file for enzyme proteins")
    train.add_argument("--outdir", default="results/sxlaep_training", help="output directory")
    train.add_argument("--lag", type=int, default=10, help="pseudo-AAC lag")
    train.add_argument("--weight", type=float, default=0.05, help="pseudo-AAC weight")
    train.add_argument("--segments", type=int, default=3, help="number of window-AAC segments")
    train.add_argument("--test-size", type=float, default=0.1, help="held-out test fraction")
    train.add_argument("--seed", type=int, default=42, help="random seed")
    train.add_argument("--n-jobs", type=int, default=-1, help="number of parallel workers")

    predict = subparsers.add_parser("predict", help="predict enzyme probabilities for FASTA sequences")
    predict.add_argument("--model", required=True, help="trained joblib model path")
    predict.add_argument("--fasta", required=True, help="input FASTA file")
    predict.add_argument("--output", default="results/predictions.csv", help="output CSV path")
    predict.add_argument("--n-jobs", type=int, default=1, help="number of parallel workers")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the sxLaep command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.simple_fasta is not None:
        if args.command is not None:
            parser.error("Do not combine --input/--output with train or predict; use one style only.")
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

    if args.command == "train":
        feature_config = FeatureConfig(lag=args.lag, weight=args.weight, n_segments=args.segments)
        training_config = TrainingConfig(test_size=args.test_size, random_state=args.seed, n_jobs=args.n_jobs)
        result = run_training_pipeline(
            noenzyme_fasta=args.noenzyme_fasta,
            enzyme_fasta=args.enzyme_fasta,
            output_dir=args.outdir,
            feature_config=feature_config,
            training_config=training_config,
        )
        print(f"Training finished. Model: {result['model_path']}")
        print(f"Accuracy: {result['metrics']['accuracy']:.4f}")
    elif args.command == "predict":
        result = run_prediction_pipeline(
            model_path=args.model,
            fasta_path=args.fasta,
            output_csv=args.output,
            n_jobs=args.n_jobs,
        )
        print(f"Predictions saved to {args.output}. Rows: {len(result)}")
    else:  # pragma: no cover
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
