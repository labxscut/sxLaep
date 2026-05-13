# sxLaep Workflow

```text
Input FASTA files
    ↓
Read sequences and assign labels
    ↓
Extract multi-property pseudo-AAC, sequence length, CTD, and windowed AAC features
    ↓
Split train/test data
    ↓
Train XGBoost enzyme/non-enzyme classifier
    ↓
Evaluate accuracy, classification report, and confusion matrix
    ↓
Save model, predictions, report, and feature names
```

## Training example

```bash
python scripts/main.py train   --noenzyme-fasta data/noenzyme.fasta   --enzyme-fasta data/enzyme.fasta   --outdir results/raep_training
```

## Prediction example

```bash
python scripts/main.py predict   --model results/raep_training/enzyme_xgb_model.ubj   --fasta data/query.fasta   --output results/query_predictions.csv
```
