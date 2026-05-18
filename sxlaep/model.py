"""Model loading and prediction utilities."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from .config import FeatureConfig
from .fasta import read_fasta_records
from .features import extract_feature_matrix

_NATIVE_MODEL_SUFFIXES = frozenset({".json", ".ubj", ".txt"})


def load_model(model_path: str | Path) -> Any:
    """Load an XGBoost classifier from native JSON/UBJSON or legacy joblib pickle."""

    import joblib
    import xgboost as xgb

    path = Path(model_path)
    if path.suffix.lower() in _NATIVE_MODEL_SUFFIXES:
        clf = xgb.XGBClassifier()
        clf.load_model(str(path))
        return clf
    native = path.with_suffix(".ubj")
    if native.is_file():
        clf = xgb.XGBClassifier()
        clf.load_model(str(native))
        return clf
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="pickle")
        return joblib.load(path)


def predict_sequences(
    model: Any,
    sequences: Sequence[str],
    config: FeatureConfig | None = None,
    n_jobs: int = 1,
) -> pd.DataFrame:
    """Predict enzyme probabilities for a list of protein sequences."""

    feature_matrix = extract_feature_matrix(sequences, config=config, n_jobs=n_jobs)
    labels = model.predict(feature_matrix)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(feature_matrix)[:, 1]
    else:
        probabilities = np.asarray(labels, dtype=float)
    return pd.DataFrame({"pred_label": labels.astype(int), "enzyme_probability": probabilities})


def predict_fasta(
    model_path: str | Path,
    fasta_path: str | Path,
    output_csv: str | Path,
    config: FeatureConfig | None = None,
    n_jobs: int = 1,
) -> pd.DataFrame:
    """Load a model, predict a FASTA file, and write predictions to CSV."""

    model = load_model(model_path)
    records = read_fasta_records(fasta_path)
    result = predict_sequences(model, [r.sequence for r in records], config=config, n_jobs=n_jobs)
    result.insert(0, "description", [r.description for r in records])
    result.insert(0, "sequence_id", [r.identifier for r in records])
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)
    return result


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
