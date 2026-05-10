"""sxLaep: Rapid Enzyme/Non-Enzyme Prediction.

sxLaep is an efficient machine learning tool for predicting whether a protein
sequence is an enzyme or non-enzyme. It combines multi-physicochemical
sequence features (Pseudo-AAC, CTD, windowed AAC) with an XGBoost classifier.

Key features:
- Fast single-sequence and batch prediction (including FASTA files)
- Built-in parallelized feature extraction
- Simple Python API and command-line interface (CLI)
- End-to-end training pipeline for custom models
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

__version__ = "1.0.0"
