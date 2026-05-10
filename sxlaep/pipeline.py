"""End-to-end workflows for sxLaep training and prediction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .config import FeatureConfig, TrainingConfig
from .model import predict_fasta
from .training import train_enzyme_classifier


def run_training_pipeline(
    noenzyme_fasta: str | Path,
    enzyme_fasta: str | Path,
    output_dir: str | Path = "results/sxlaep_training",
    feature_config: FeatureConfig | None = None,
    training_config: TrainingConfig | None = None,
    xgb_params: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the complete FASTA-to-model sxLaep training workflow."""

    return train_enzyme_classifier(
        noenzyme_fasta=noenzyme_fasta,
        enzyme_fasta=enzyme_fasta,
        output_dir=output_dir,
        feature_config=feature_config,
        training_config=training_config,
        xgb_params=xgb_params,
    )


def run_prediction_pipeline(
    model_path: str | Path,
    fasta_path: str | Path,
    output_csv: str | Path = "results/predictions.csv",
    feature_config: FeatureConfig | None = None,
    n_jobs: int = 1,
):
    """Run the complete FASTA-to-prediction sxLaep workflow."""

    return predict_fasta(
        model_path=model_path,
        fasta_path=fasta_path,
        output_csv=output_csv,
        config=feature_config,
        n_jobs=n_jobs,
    )
