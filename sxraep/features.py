"""Protein sequence feature extraction for sxRaep."""

from __future__ import annotations

import re
from typing import Mapping, Sequence

import numpy as np

from .config import AA20, CTD_GROUPS, FeatureConfig, PROPERTIES

_VALID_AA_RE = re.compile("[^ACDEFGHIKLMNPQRSTVWY]")


def sanitize_sequence(sequence: str) -> str:
    """Return an uppercase protein sequence containing only the 20 standard amino acids."""

    return _VALID_AA_RE.sub("", sequence.upper())


def pse_aac_multi(
    sequence: str,
    lam: int = 10,
    weight: float = 0.05,
    properties: Mapping[str, Mapping[str, float]] = PROPERTIES,
    add_length: bool = True,
) -> np.ndarray:
    """Compute multi-property pseudo-amino acid composition features.

    The output contains standard amino acid composition, property-specific
    sequence-order correlation terms, and optionally sequence length.

    Parameters
    ----------
    sequence:
        Input protein sequence.
    lam:
        Maximum correlation lag.
    weight:
        Weight applied to sequence-order terms.
    properties:
        Mapping from property name to amino-acid property values.
    add_length:
        Whether to append sequence length as the last feature.

    Returns
    -------
    numpy.ndarray
        Feature vector with length ``20 + lam * n_properties + int(add_length)``.
    """

    seq = sanitize_sequence(sequence)
    length = len(seq)
    n_prop = len(properties)
    if length == 0:
        base = np.zeros(20 + lam * n_prop, dtype=float)
        return np.concatenate([base, [0.0]]) if add_length else base

    aac = np.array([seq.count(aa) / length for aa in AA20], dtype=float)

    theta_values = []
    for _, prop in properties.items():
        theta = np.zeros(lam, dtype=float)
        for k in range(1, lam + 1):
            if length <= k:
                break
            diffs = [(prop[seq[i]] - prop[seq[i + k]]) ** 2 for i in range(length - k)]
            theta[k - 1] = float(np.mean(diffs)) if diffs else 0.0
        theta_values.append(theta)

    thetas = np.concatenate(theta_values) if theta_values else np.array([], dtype=float)
    denom = 1.0 + weight * float(thetas.sum())
    features = np.concatenate([aac, weight * thetas]) / denom

    if add_length:
        features = np.concatenate([features, [float(length)]])
    return features


def ctd_features(sequence: str) -> np.ndarray:
    """Compute composition-transition-distribution features.

    Seven physicochemical group systems are used. For each system, the function
    returns 3 composition values, 3 transition values, and 15 distribution
    values, yielding 147 features in total.
    """

    seq = sanitize_sequence(sequence)
    length = len(seq)
    if length == 0:
        return np.zeros(len(CTD_GROUPS) * 21, dtype=float)

    all_features = []
    for _, groups in CTD_GROUPS.items():
        group_sequence = []
        for aa in seq:
            if aa in groups[0]:
                group_sequence.append(1)
            elif aa in groups[1]:
                group_sequence.append(2)
            elif aa in groups[2]:
                group_sequence.append(3)
            else:
                group_sequence.append(0)
        group_sequence = np.asarray(group_sequence)

        composition = [float(np.sum(group_sequence == g) / length) for g in (1, 2, 3)]

        transitions = []
        denom = max(length - 1, 1)
        for g1 in (1, 2, 3):
            for g2 in (1, 2, 3):
                if g1 < g2:
                    count = np.sum((group_sequence[:-1] == g1) & (group_sequence[1:] == g2))
                    count += np.sum((group_sequence[:-1] == g2) & (group_sequence[1:] == g1))
                    transitions.append(float(count / denom))

        distribution = []
        for g in (1, 2, 3):
            idx = np.where(group_sequence == g)[0]
            if len(idx) == 0:
                distribution.extend([0.0, 0.0, 0.0, 0.0, 0.0])
            else:
                distribution.extend(
                    [
                        float(idx[0] / length),
                        float(idx[int(0.25 * len(idx))] / length),
                        float(idx[int(0.50 * len(idx))] / length),
                        float(idx[int(0.75 * len(idx))] / length),
                        float(idx[-1] / length),
                    ]
                )
        all_features.extend(composition + transitions + distribution)

    return np.asarray(all_features, dtype=float)


def window_aac(sequence: str, n_segments: int = 3) -> np.ndarray:
    """Compute windowed amino acid composition over N-to-C sequence segments."""

    seq = sanitize_sequence(sequence)
    length = len(seq)
    if length == 0:
        return np.zeros(n_segments * 20, dtype=float)

    segment_size = max(1, length // n_segments)
    features = []
    for i in range(n_segments):
        start = i * segment_size
        end = length if i == n_segments - 1 else (i + 1) * segment_size
        subseq = seq[start:end]
        if not subseq:
            features.extend([0.0] * 20)
        else:
            features.extend([subseq.count(aa) / len(subseq) for aa in AA20])
    return np.asarray(features, dtype=float)


def extract_features(sequence: str, config: FeatureConfig | None = None) -> np.ndarray:
    """Extract the full sxRaep feature vector for one protein sequence."""

    config = config or FeatureConfig()
    pse = pse_aac_multi(
        sequence,
        lam=config.lag,
        weight=config.weight,
        properties=config.properties,
        add_length=config.add_length,
    )
    ctd = ctd_features(sequence)
    win = window_aac(sequence, n_segments=config.n_segments)
    return np.concatenate([pse, ctd, win])


def extract_feature_matrix(
    sequences: Sequence[str],
    config: FeatureConfig | None = None,
    n_jobs: int = 1,
) -> np.ndarray:
    """Extract a feature matrix from a sequence collection.

    Parameters
    ----------
    sequences:
        Protein sequences.
    config:
        Feature extraction configuration.
    n_jobs:
        Number of parallel workers. Values less than or equal to one run in a
        single process.
    """

    config = config or FeatureConfig()
    if n_jobs is None or n_jobs <= 1:
        rows = [extract_features(seq, config=config) for seq in sequences]
    else:
        from joblib import Parallel, delayed

        rows = Parallel(n_jobs=n_jobs)(delayed(extract_features)(seq, config=config) for seq in sequences)
    if not rows:
        return np.empty((0, len(feature_names(config))), dtype=float)
    return np.vstack(rows)


def feature_names(config: FeatureConfig | None = None) -> list[str]:
    """Return names for all extracted sxRaep features."""

    config = config or FeatureConfig()
    names = [f"aac_{aa}" for aa in AA20]
    for property_name in config.properties:
        names.extend([f"pseaac_{property_name}_lag{k}" for k in range(1, config.lag + 1)])
    if config.add_length:
        names.append("sequence_length")
    for ctd_name in CTD_GROUPS:
        names.extend([f"ctd_{ctd_name}_composition_g{g}" for g in (1, 2, 3)])
        names.extend([f"ctd_{ctd_name}_transition_{a}{b}" for a, b in ((1, 2), (1, 3), (2, 3))])
        for group in (1, 2, 3):
            names.extend([f"ctd_{ctd_name}_distribution_g{group}_q{q}" for q in (0, 25, 50, 75, 100)])
    for segment in range(1, config.n_segments + 1):
        names.extend([f"window{segment}_aac_{aa}" for aa in AA20])
    return names
