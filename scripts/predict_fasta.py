#!/usr/bin/env python3
"""Predict enzyme probabilities from a FASTA file with a trained sxLaep model."""

from sxlaep.cli import main


if __name__ == "__main__":
    main(["predict"])
