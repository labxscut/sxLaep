"""FASTA reading utilities for protein sequence experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class FastaRecord:
    """A single FASTA record.

    Attributes
    ----------
    identifier:
        Header identifier without the leading ``>`` symbol. The first token is
        used when the header contains whitespace.
    description:
        Full FASTA header without the leading ``>`` symbol.
    sequence:
        Concatenated protein sequence string.
    """

    identifier: str
    description: str
    sequence: str


def read_fasta_records(fasta_path: str | Path) -> List[FastaRecord]:
    """Read a FASTA file and return records with identifiers and sequences.

    Parameters
    ----------
    fasta_path:
        Path to the input FASTA file.

    Returns
    -------
    list of FastaRecord
        Parsed FASTA records in file order.
    """

    fasta_path = Path(fasta_path)
    records: List[FastaRecord] = []
    header: str | None = None
    seq_parts: List[str] = []

    with fasta_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    identifier = header.split()[0] if header.split() else header
                    records.append(FastaRecord(identifier, header, "".join(seq_parts)))
                header = line[1:].strip()
                seq_parts = []
            else:
                seq_parts.append(line)

    if header is not None:
        identifier = header.split()[0] if header.split() else header
        records.append(FastaRecord(identifier, header, "".join(seq_parts)))

    return records


def read_fasta(fasta_path: str | Path) -> List[str]:
    """Read a FASTA file and return only sequence strings."""

    return [record.sequence for record in read_fasta_records(fasta_path)]


def write_fasta_records(records: Iterable[FastaRecord], output_path: str | Path) -> None:
    """Write FASTA records to disk."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(f">{record.description}\n")
            seq = record.sequence
            for i in range(0, len(seq), 80):
                handle.write(seq[i : i + 80] + "\n")
