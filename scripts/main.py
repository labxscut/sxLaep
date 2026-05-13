"""Repository-level CLI entry for sxLaep (run from repo root).

Example::

    python scripts/main.py train --help
    python scripts/main.py predict --help

Requires the package importable (e.g. ``pip install -e .`` from this repo).
"""

from sxlaep.cli import main


if __name__ == "__main__":
    main()
