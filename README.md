# sxLaep: a Lightweight and Accurate Enzyme Predictor
sxLaep is an efficient machine learning tool for predicting whether a protein sequence is an enzyme or non-enzyme. It combines multi-physicochemical sequence features with an XGBoost classifier for fast and accurate binary classification.

## QUICK LINKS

[GitHub Repository](https://github.com/labxscut/sxLaep)

[API Reference](https://labxscut.github.io/sxLaep/)

[Workflow Documentation](docs/WORKFLOW.md)

## INTRODUCTION

In bioinformatics, accurate identification of enzymes from protein sequences is crucial for understanding metabolic pathways, drug target discovery, and functional annotation of novel proteins. Traditional experimental methods for enzyme classification are time-consuming and expensive, making computational prediction approaches highly valuable.

sxLaep provides a machine learning-based solution for enzyme/non-enzyme classification from protein sequences. The tool extracts comprehensive sequence-derived features that capture various physicochemical properties and structural characteristics of proteins:

- **Multi-property Pseudo-Amino Acid Composition (Pse-AAC)**: Captures sequence-order information through hydrophobicity, polarity, and charge properties
- **Composition-Transition-Distribution (CTD)**: Describes amino acid distribution across different physicochemical groups
- **Windowed Amino Acid Composition**: Captures local sequence patterns by dividing sequences into N-to-C segments
- **Sequence Length**: Raw protein length as a complementary feature

These features are fed into a pre-trained XGBoost classifier that has been optimized for performance on enzyme classification tasks. The model achieves high accuracy while maintaining fast inference speed, making it suitable for large-scale protein annotation projects.

sxLaep supports both single-sequence prediction and batch processing of FASTA files, with built-in parallelization for efficient feature extraction. The package provides both a simple Python API and a command-line interface for flexible integration into various bioinformatics workflows.

## METHODS


![pipeline](https://raw.githubusercontent.com/CirinMok/Picture_Raep/main/pipeline.png)

Figure 1. The sxLaep pre-screening workflow. The framework acts as a lightweight ”gatekeeper” for massive protein datasets. It extracts alignment-free
physicochemical features and utilizes a machine learning classifier to rapidly filter out non-enzymatic sequences. This process significantly reduces
computational load for downstream analysis while effectively retaining potential enzymes, including remote homologs (”Functional Dark Matter”)

## SOFTWARE

> sxLaep (Lightweight and Accurate Enzyme Predictor)
>
> The package is available for Python 3.9+ on Windows, Linux, and macOS.
>
> Latest updates and source code are available at:
> https://github.com/labxscut/sxLaep


## DOCKER
A pre-configured Docker image is provided to run `sxLaep` in an isolated environment with Python 3.11 and all required dependencies.

### Quick Start
Pull the official image directly:
```bash
docker pull labxscut/sxlaep:python3.11
```
### Running the Container
Mount your local data directory to the container's working directory (/workspace) and start an interactive shell:
```bash
docker run --rm -it -v $(pwd):/workspace labxscut/sxlaep:python3.11 bash
```
Once inside the container, the sxlaep CLI is ready to use (the sxlaep conda environment is auto-activated).

### Build Locally (Optional)
If you prefer to build the image from the provided Dockerfile:
```bash
docker build --no-cache -t labxscut/sxlaep:python3.11 .
```
Then run it using the docker run command above.

## INSTALL

Requires **Python 3.9+**. Dependencies (`numpy`, `pandas`, `scikit-learn`, `xgboost`, `joblib`) are pulled in automatically when you install the package.

### Recommended: `pipx` (CLI on your PATH, no project venv)

[`pipx`](https://pypa.github.io/pipx/) installs the app into its own isolated environment and links the `sxlaep` executable onto your PATH—**you do not need to create or activate a virtualenv** for normal command-line use.

Install `pipx` once (if needed), then:

```bash
pipx install sxlaep --pip-args="--prefer-binary -v"
```

If downloads are slow, add an index URL inside `--pip-args`, for example:

```bash
pipx install sxlaep --pip-args="-i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --prefer-binary -v"
```

Upgrade or reinstall:

```bash
pipx upgrade sxlaep
# or: pipx reinstall sxlaep
```

### Optional: `pipx` install from GitHub (latest `main`)

Use this when you need **commits not yet published to PyPI**. You must have **`git`** installed and on your **`PATH`** (pip clones the repository).

This path is **more fragile** than PyPI: pipx may appear to hang on **determining package name** while it installs into a **temporary** virtual environment to discover the distribution name, then installs again into the real pipx venv. Dependency resolution and **xgboost** wheels or source builds can take **many minutes**. Use **`--verbose`** so you can see progress.

```bash
export PIP_DEFAULT_TIMEOUT=120
pipx install --verbose --force "sxlaep @ git+https://github.com/labxscut/sxLaep.git@main" \
  --pip-args="--prefer-binary -v --default-timeout=120"
```

To track a **different branch or tag**, change the trailing **`@main`** (for example **`@develop`** or **`@v1.0.0`**).

Equivalent VCS URL form (some users prefer this):

```bash
pipx install --verbose --force "git+https://github.com/labxscut/sxLaep.git@main" \
  --pip-args="--prefer-binary -v --default-timeout=120"
```

To **refresh** an existing git-based install, re-run the same command with **`--force`**. To go back to the **PyPI** build, use **`pipx uninstall sxlaep`** then **`pipx install sxlaep`** as in the recommended section above.

**Development from a clone** (editable install, still isolated like other `pipx` apps):

```bash
git clone https://github.com/labxscut/sxLaep.git
cd sxLaep
pipx install -e . --pip-args="--prefer-binary -v"
```

### Alternative: `pip` in a virtual environment (library / notebooks)

Use this when you import `sxlaep` inside your own project or Jupyter and want dependencies in **your** venv—not required for the standalone CLI if you used `pipx` above.

Use a recent `pip`, then install with binary preference:

```bash
python3 -m pip install -U "pip>=24" setuptools wheel
python3 -m pip install --prefer-binary sxlaep
```

Run the same commands after activating whichever venv you use for that project.

**Editable install** (optional, for development without `pipx`):

```bash
git clone https://github.com/labxscut/sxLaep.git
cd sxLaep
python3 -m pip install -U "pip>=24" setuptools wheel
python3 -m pip install --prefer-binary -e .
```

### If install is slow or hangs

- First-time resolution and wheel download can take **several minutes**; keep `-v` so you see progress.
- **`pipx install … @ git+https://…`** (GitHub method above): pipx may sit on **determining package name** while it **clones** the repo and runs **pip** in a temporary venv, then repeats work in the final venv—use **`--verbose`** and a generous **`PIP_DEFAULT_TIMEOUT`** / **`--default-timeout`** (as in the examples).
- **Prefer wheels** with `--prefer-binary` (commands above) to avoid long **source builds** of `xgboost`.
- On Debian/Ubuntu, if `xgboost` still builds from source, install compilers and CMake, then retry:  
  `sudo apt-get install -y build-essential cmake ninja-build`

### Python API (after install)

See **Quick start** below for `load_model` / `predict_sequences` and `run_prediction_pipeline`.

## QUICK START

### Python API

```python
from pathlib import Path

import sxlaep
from sxlaep.model import load_model, predict_sequences

ubj = Path(sxlaep.__file__).resolve().parent / "enzyme_xgb_model.ubj"
model = load_model(ubj)
df = predict_sequences(model, ["MKVLWALIFLLKSAF"])
# columns: pred_label, enzyme_probability
```

FASTA to CSV in one call:

```python
from sxlaep import run_prediction_pipeline

run_prediction_pipeline(
    model_path="path/to/model.pkl",  # or .ubj / .joblib
    fasta_path="sequences.fasta",
    output_csv="predictions.csv",
)
```

### Command line

Training:

```bash
sxlaep train --noenzyme-fasta neg.fasta --enzyme-fasta pos.fasta --outdir results/sxlaep_training
```

Prediction (writes a CSV):

```bash
sxlaep predict --model path/to/model.pkl --fasta sequences.fasta --output predictions.csv
```

Help:

```bash
sxlaep --help
sxlaep train --help
sxlaep predict --help
```

## EXECUTABLES

- **`sxlaep`** — CLI with subcommands **`train`** and **`predict`** (see **Quick start** above). Use **`--help`** on each subcommand for options.

From a **clone**, optional end-user helper:

- Example FASTAs: **`tests/enzyme_example.fasta`**, **`tests/noenzyme_example.fasta`**.
- Run **`cd tests && ./install.sh`**: the script **anchors to `tests/`**, **downloads** missing FASTAs from **GitHub raw** when needed, then **`pipx install`** or **`pipx upgrade`** **`sxlaep`** from **PyPI** only, then runs **`sxlaep predict`** on both example FASTAs and **validates CSV output** (set **`SXLAEP_SKIP_CLI_SMOKE=1`** to skip that check). **No sudo.** Override the raw URL prefix with **`SXLAEP_RAW_BASE`** or branch with **`SXLAEP_RAW_REF`** (default **`main`**; path must end at the `tests/` segment on raw.githubusercontent.com).
- **Developers:** from repo root, run **`pytest tests/`**.

## REFERENCE PARAMETERS

### Feature Extraction Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lag` | int | 10 | Maximum correlation lag for pseudo-AAC. Controls the length of sequence-order correlation terms. Higher values capture longer-range dependencies but increase feature dimensionality. |
| `weight` | float | 0.05 | Weight applied to sequence-order correlation terms in pseudo-AAC. Balances between standard amino acid composition and sequence-order information. |
| `n_segments` | int | 3 | Number of N-to-C sequence windows for windowed AAC. Divides the sequence into equal segments for local composition analysis. |
| `add_length` | bool | True | Whether to append raw sequence length to the feature vector. Provides additional size information that may be correlated with enzyme function. |
| `properties` | dict | PROPERTIES | Amino-acid physicochemical property tables used by pseudo-AAC. Default includes: hydrophobicity (HYDRO), polarity (POLAR), and charge (CHARGE). |

### Command line arguments

#### `sxlaep train`

| Argument | Required | Description |
|----------|----------|-------------|
| `--noenzyme-fasta` | Yes | FASTA path for non-enzyme (negative) sequences. |
| `--enzyme-fasta` | Yes | FASTA path for enzyme (positive) sequences. |
| `--outdir` | No | Training output directory (default `results/sxlaep_training`). |
| `--lag`, `--weight`, `--segments` | No | Feature knobs (pseudo-AAC lag/weight, window-AAC segments). |
| `--test-size`, `--seed`, `--n-jobs` | No | Holdout fraction, RNG seed, parallelism. |

#### `sxlaep predict`

| Argument | Required | Description |
|----------|----------|-------------|
| `--model` | Yes | Trained model path (`.pkl` / `.joblib` / native `.ubj` as supported by `load_model`). |
| `--fasta` | Yes | Input FASTA path. |
| `--output` | No | Output CSV path (default `results/predictions.csv`). |
| `--n-jobs` | No | Parallel workers for feature extraction (default `1`). |

### Output file formats

#### CSV output (`sxlaep predict`)

The prediction CSV includes (among others) identifier columns plus scores:

| Column | Description |
|--------|-------------|
| `sequence_id` | FASTA record id (first token of the header). |
| `description` | Full header line after `>`. |
| `pred_label` | `0` = non-enzyme, `1` = enzyme. |
| `enzyme_probability` | Estimated probability of enzyme class (when available from the model). |

## EXAMPLES

### Batch FASTA processing (Python)

```python
from sxlaep import run_prediction_pipeline

df = run_prediction_pipeline(
    model_path="enzyme_xgb_model.pkl",
    fasta_path="proteins.fasta",
    output_csv="predictions.csv",
)
print(df[["sequence_id", "pred_label", "enzyme_probability"]].head())
```

### Same task from the shell

```bash
sxlaep predict --model enzyme_xgb_model.pkl --fasta proteins.fasta --output predictions.csv
```

## NOTES

> - The pre-trained model is shipped as `enzyme_xgb_model.ubj` (XGBoost native format). Training still writes a sibling `.ubj` when you save `*.pkl` for backward compatibility.
> - The Python package name for installation is `sxlaep` (for example: `python3 -m pip install --prefer-binary sxlaep`).
> - Sequences containing non-standard amino acids are automatically sanitized (only the 20 standard amino acids are used).
> - Short sequences (< 10 amino acids) may yield less reliable predictions.
> - For large-scale predictions (>10,000 sequences), consider processing in batches or using a high-performance computing environment.

## CONTACT

> lcxia@scut.edu.cn 
> dhy.scut@outlook.com
> GitHub: https://github.com/labxscut

## CITATIONS

Please cite sxLaep if you use it in your research:

> labxscut. sxLaep: a Lightweight and Accurate Enzyme Predictor for High-throughput Mining of Metagenomic Sequences. (2026).


