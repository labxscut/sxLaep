"""Basic smoke tests for sxRaep."""

import numpy as np

from sxraep.config import FeatureConfig
from sxraep.features import extract_features, feature_names, sanitize_sequence


def test_sanitize_sequence():
    assert sanitize_sequence("acdxBZ") == "ACD"


def test_feature_dimension_matches_names():
    config = FeatureConfig()
    values = extract_features("ACDEFGHIKLMNPQRSTVWY", config=config)
    assert isinstance(values, np.ndarray)
    assert values.shape[0] == len(feature_names(config))
