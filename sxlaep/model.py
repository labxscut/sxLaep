"""Model construction, persistence, and prediction utilities."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from .config import DEFAULT_XGB_PARAMS, FeatureConfig
from .fasta import read_fasta_records
from .features import extract_feature_matrix

_NATIVE_MODEL_SUFFIXES = frozenset({".json", ".ubj", ".txt"})


def build_xgb_classifier(
    scale_pos_weight: float | None = None,
    params: Mapping[str, Any] | None = None,
):
    """Build an XGBoost binary classifier for enzyme prediction."""

    import xgboost as xgb

    xgb_params = dict(DEFAULT_XGB_PARAMS)
    if params:
        xgb_params.update(params)
    if scale_pos_weight is not None:
        xgb_params["scale_pos_weight"] = scale_pos_weight
    return xgb.XGBClassifier(**xgb_params)


def save_model(model: Any, model_path: str | Path) -> None:
    """Persist a trained XGBoost classifier.

    Paths ending in ``.json`` or ``.ubj`` use XGBoost's native format
    (``Booster.save_model``), which loads without version-skew pickle warnings.
    For ``.pkl`` / ``.joblib``, the sklearn wrapper is saved with joblib and a
    sibling ``.ubj`` is written when ``save_model`` is available.
    """

    import joblib

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    save_native = getattr(model, "save_model", None)
    suffix = model_path.suffix.lower()
    if save_native is not None and suffix in _NATIVE_MODEL_SUFFIXES:
        save_native(str(model_path))
        return
    joblib.dump(model, model_path)
    if save_native is not None and suffix in {".pkl", ".joblib"}:
        save_native(str(model_path.with_suffix(".ubj")))


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
