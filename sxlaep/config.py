"""Configuration objects and biochemical constants used by sxLaep."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Sequence, Set

AA20 = "ACDEFGHIKLMNPQRSTVWY"

HYDRO = {
    "A": 1.8, "C": 2.5, "D": -3.5, "E": -3.5, "F": 2.8,
    "G": -0.4, "H": -3.2, "I": 4.5, "K": -3.9, "L": 3.8,
    "M": 1.9, "N": -3.5, "P": -1.6, "Q": -3.5, "R": -4.5,
    "S": -0.8, "T": -0.7, "V": 4.2, "W": -0.9, "Y": -1.3,
}

POLAR = {
    "A": 8.1, "C": 5.5, "D": 13.0, "E": 12.3, "F": 5.2,
    "G": 9.0, "H": 10.4, "I": 5.2, "K": 11.3, "L": 4.9,
    "M": 5.7, "N": 11.6, "P": 8.0, "Q": 10.5, "R": 10.5,
    "S": 9.2, "T": 8.6, "V": 5.9, "W": 5.4, "Y": 6.2,
}

CHARGE = {
    "A": 0, "C": 0, "D": -1, "E": -1, "F": 0,
    "G": 0, "H": 0.5, "I": 0, "K": 1, "L": 0,
    "M": 0, "N": 0, "P": 0, "Q": 0, "R": 1,
    "S": 0, "T": 0, "V": 0, "W": 0, "Y": 0,
}

PROPERTIES: Dict[str, Dict[str, float]] = {
    "hydro": HYDRO,
    "polar": POLAR,
    "charge": CHARGE,
}

CTD_GROUPS: Dict[str, Sequence[Set[str]]] = {
    "hydrophobicity": [set("RKEDQN"), set("GASTPHY"), set("CLVIMFW")],
    "normalized_vdw": [set("GASTPD"), set("NVEQIL"), set("MHKFRYW")],
    "polarizability": [set("GASDT"), set("CPNVEQIL"), set("KMHFRYW")],
    "secondary": [set("NDEQST"), set("AILMV"), set("CFGHKPRYW")],
    "solvent_access": [set("ALFCGIVW"), set("RKQEND"), set("MPSTHY")],
    "polarity": [set("LIFWCMVY"), set("PATGS"), set("HQRKNED")],
    "charge": [set("KR"), set("ANCQGHILMFPSTWYV"), set("DE")],
}

DEFAULT_XGB_PARAMS = {
    "n_estimators": 799,
    "max_depth": 9,
    "learning_rate": 0.11107207866102274,
    "subsample": 0.8205356041339127,
    "colsample_bytree": 0.7865743071602549,
    "gamma": 0.6350739428156533,
    "min_child_weight": 3,
    "random_state": 42,
    "n_jobs": -1,
    "eval_metric": "logloss",
}


@dataclass(frozen=True)
class FeatureConfig:
    """Feature extraction configuration.

    Parameters
    ----------
    lag:
        Maximum correlation lag used by multi-property pseudo-AAC.
    weight:
        Weight applied to sequence-order correlation terms.
    n_segments:
        Number of N-to-C sequence windows used by windowed AAC.
    add_length:
        Whether to append raw sequence length to the pseudo-AAC vector.
    properties:
        Amino-acid physicochemical property tables used by pseudo-AAC.
    """

    lag: int = 10
    weight: float = 0.05
    n_segments: int = 3
    add_length: bool = True
    properties: Mapping[str, Mapping[str, float]] = field(default_factory=lambda: PROPERTIES)


@dataclass(frozen=True)
class TrainingConfig:
    """Training configuration for enzyme/non-enzyme classification."""

    test_size: float = 0.1
    random_state: int = 42
    n_jobs: int = -1
    model_path: str = "enzyme_xgb_model.pkl"
    report_path: str = "classification_report.txt"
    predictions_path: str = "test_predictions.csv"
