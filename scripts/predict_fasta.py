#!/usr/bin/env python3
"""Predict enzyme probabilities from a FASTA file with a trained sxRaep model."""

from sxraep.cli import main


if __name__ == "__main__":
    main(["predict"])
