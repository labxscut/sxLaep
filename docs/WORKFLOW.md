# Command-Line Workflow Examples

## Overview

`sxlaep` provides a full command-line pipeline for enzyme/non-enzyme prediction. All feature extraction parameters are exposed on the CLI.

## Quick prediction (bundled model)

```bash
sxlaep --input proteins.fasta --output predictions.csv
```

## Training a custom model

```bash
sxlaep train \
    --enzyme-fasta enzyme.fasta \
    --noenzyme-fasta noenzyme.fasta \
    --outdir results/sxlaep_training \
    --lag 10 \
    --weight 0.05 \
    --segments 3 \
    --add-length \
    --properties hydro polar charge \
    --test-size 0.1 \
    --seed 42 \
    --n-jobs -1
```

### Feature parameter reference

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--lag` | int | `10` | Maximum correlation lag for pseudo-AAC |
| `--weight` | float | `0.05` | Weight on sequence-order correlation terms |
| `--segments` | int | `3` | Number of N-to-C windows for windowed AAC |
| `--add-length` / `--no-add-length` | flag | enabled | Append raw sequence length to feature vector |
| `--properties` | list | `hydro polar charge` | Physicochemical properties for pseudo-AAC |

## Prediction with a trained model

```bash
sxlaep predict \
    --model results/sxlaep_training/enzyme_xgb_model.ubj \
    --fasta query.fasta \
    --output results/query_predictions.csv \
    --lag 10 \
    --weight 0.05 \
    --segments 3 \
    --add-length \
    --properties hydro polar charge \
    --n-jobs 1
```

**Important:** The feature parameters must match those used during training.

## Verifying installation

```bash
pytest tests/
```
