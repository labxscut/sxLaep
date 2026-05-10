"""sxRaep: feature-based enzyme/non-enzyme classification utilities.

The package provides reusable components for reading protein FASTA files,
extracting sequence-derived features, training an XGBoost classifier, and
running prediction workflows.
"""

from .config import FeatureConfig, TrainingConfig
from .fasta import FastaRecord, read_fasta, read_fasta_records
from .features import (
    ctd_features,
    extract_feature_matrix,
    extract_features,
    feature_names,
    pse_aac_multi,
    sanitize_sequence,
    window_aac,
)
from .pipeline import run_prediction_pipeline, run_training_pipeline

__all__ = [
    "FeatureConfig",
    "TrainingConfig",
    "FastaRecord",
    "read_fasta",
    "read_fasta_records",
    "sanitize_sequence",
    "pse_aac_multi",
    "ctd_features",
    "window_aac",
    "extract_features",
    "extract_feature_matrix",
    "feature_names",
    "run_training_pipeline",
    "run_prediction_pipeline",
]

__version__ = "0.1.0"
