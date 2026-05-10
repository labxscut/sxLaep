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
python main.py train   --noenzyme-fasta data/noenzyme.fasta   --enzyme-fasta data/enzyme.fasta   --outdir results/sxlaep_training
```

## Prediction example

```bash
python main.py predict   --model results/sxlaep_training/enzyme_xgb_model.pkl   --fasta data/query.fasta   --output results/query_predictions.csv
```
