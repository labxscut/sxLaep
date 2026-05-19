# Command-Line Workflow Examples

## Overview

This page is a practical command-line workflow guide for **sxLaep** (enzyme / non-enzyme prediction).

### Input format (FASTA)

Please make sure your input FASTA is well-formed before running predictions. Transferring text files among macOS, Linux, and Windows may change newline characters and break parsers, so if you see unexpected errors, re-save the file with **UTF-8** encoding and **LF** newlines.

Minimal example:

```fasta
>seq1 some description
MKVLWALIFLLKSAF
>seq2
GAVLKVLTTGLPALISWIKRKRQQ
```

Notes:
- Only the 20 standard amino acids are used; non-standard characters are sanitized automatically.
- Very short sequences (< 10 aa) may yield less reliable predictions.

### Quick prediction (bundled model)

```bash
sxlaep --input proteins.fasta --output predictions.csv
```

This shorthand uses the **bundled model** shipped inside the installed `sxlaep` package (e.g. installed via `pip` / `pipx`).

CLI help:

```text
usage: sxlaep [-h] [-i FASTA] [-o CSV] {predict} ...
```

### Prediction with a custom model (`sxlaep predict`)

If you have your own trained model (native `.ubj`/`.json` or legacy joblib/pickle), use the `predict` subcommand:

```bash
sxlaep predict \
    --model enzyme_xgb_model.ubj \
    --fasta query.fasta \
    --output results/query_predictions.csv \
    --lag 10 \
    --weight 0.05 \
    --segments 3 \
    --add-length \
    --properties hydro polar charge \
    --n-jobs 1
```

**Important:** the feature parameters must match those used during training.

CLI help:

```text
usage: sxlaep predict [-h] --model MODEL --fasta FASTA [--output OUTPUT] ...
```

### Output (CSV)

The output CSV includes identifier columns plus prediction scores:

| Column | Description |
|---|---|
| `sequence_id` | FASTA record id (first token of the header). |
| `description` | Full header line after `>`. |
| `pred_label` | `0` = non-enzyme, `1` = enzyme. |
| `enzyme_probability` | Estimated probability of enzyme class (when available from the model). |

### Speed up (parallel feature extraction)

Use `--n-jobs` in `sxlaep predict` to parallelize feature extraction.

For large-scale runs (10k+ sequences), also consider splitting FASTA files and running multiple `sxlaep predict` processes.

### FAQ / Troubleshooting

- **Bundled model not found**: the shorthand `--input` expects a wheel/pip install layout. Install with `pipx install sxlaep` (recommended) or `pip install sxlaep`.
- **Wrong results / errors after training your own model**: ensure the feature flags (`--lag`, `--weight`, `--segments`, `--add-length`, `--properties`) match training exactly.
- **Input parsing issues**: re-check FASTA formatting and newline style (LF recommended).

### Verifying installation

```bash
sxlaep --help
sxlaep predict --help
```
