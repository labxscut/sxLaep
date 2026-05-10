"""Training and evaluation routines for sxLaep."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .config import FeatureConfig, TrainingConfig
from .fasta import read_fasta
from .features import extract_feature_matrix, feature_names
from .model import build_xgb_classifier, save_model


def load_labeled_fastas(noenzyme_fasta: str | Path, enzyme_fasta: str | Path) -> tuple[list[str], np.ndarray]:
    """Load non-enzyme and enzyme FASTA files into sequences and binary labels."""

    noenzyme_sequences = read_fasta(noenzyme_fasta)
    enzyme_sequences = read_fasta(enzyme_fasta)
    sequences = noenzyme_sequences + enzyme_sequences
    labels = np.asarray([0] * len(noenzyme_sequences) + [1] * len(enzyme_sequences), dtype=int)
    return sequences, labels


def compute_scale_pos_weight(labels: np.ndarray) -> float:
    """Compute XGBoost positive-class weighting from binary labels."""

    labels = np.asarray(labels)
    positives = int(labels.sum())
    negatives = int(len(labels) - positives)
    return float(negatives / positives) if positives > 0 else 1.0


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """Return standard binary classification metrics and report objects."""

    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    report = classification_report(
        y_true,
        y_pred,
        target_names=["NoEnzyme", "Enzyme"],
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": report,
    }


def train_enzyme_classifier(
    noenzyme_fasta: str | Path,
    enzyme_fasta: str | Path,
    output_dir: str | Path = "results/sxlaep_training",
    feature_config: FeatureConfig | None = None,
    training_config: TrainingConfig | None = None,
    xgb_params: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Train an enzyme/non-enzyme classifier from two FASTA files.

    Parameters
    ----------
    noenzyme_fasta:
        FASTA file containing negative-class protein sequences.
    enzyme_fasta:
        FASTA file containing positive-class enzyme sequences.
    output_dir:
        Directory for model and evaluation outputs.
    feature_config:
        Feature extraction configuration.
    training_config:
        Train/test split and output naming configuration.
    xgb_params:
        Optional overrides for XGBoost hyperparameters.
    """

    from sklearn.model_selection import train_test_split

    feature_config = feature_config or FeatureConfig()
    training_config = training_config or TrainingConfig()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sequences, labels = load_labeled_fastas(noenzyme_fasta, enzyme_fasta)
    features = extract_feature_matrix(sequences, config=feature_config, n_jobs=training_config.n_jobs)

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=training_config.test_size,
        random_state=training_config.random_state,
        stratify=labels,
    )

    model = build_xgb_classifier(scale_pos_weight=compute_scale_pos_weight(y_train), params=xgb_params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
    metrics = evaluate_predictions(y_test, y_pred)

    model_path = output_dir / training_config.model_path
    report_path = output_dir / training_config.report_path
    predictions_path = output_dir / training_config.predictions_path
    feature_names_path = output_dir / "feature_names.txt"

    save_model(model, model_path)

    with report_path.open("w", encoding="utf-8") as handle:
        handle.write(f"Accuracy: {metrics['accuracy']:.6f}\n")
        handle.write(f"Confusion matrix: {metrics['confusion_matrix']}\n")
        handle.write(pd.DataFrame(metrics["classification_report"]).to_string())

    pd.DataFrame(
        {
            "y_true": y_test.astype(int),
            "y_pred": np.asarray(y_pred).astype(int),
            "enzyme_probability": np.asarray(y_proba, dtype=float),
        }
    ).to_csv(predictions_path, index=False)

    feature_names_path.write_text("\n".join(feature_names(feature_config)) + "\n", encoding="utf-8")

    return {
        "model": model,
        "model_path": str(model_path),
        "report_path": str(report_path),
        "predictions_path": str(predictions_path),
        "feature_names_path": str(feature_names_path),
        "n_sequences": int(len(sequences)),
        "n_features": int(features.shape[1]),
        "metrics": metrics,
    }
