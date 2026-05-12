# sxLaep: a Lightweight and Accurate Enzyme Predictor
sxLaep is an efficient machine learning tool for predicting whether a protein sequence is an enzyme or non-enzyme. It combines multi-physicochemical sequence features with an XGBoost classifier for fast and accurate binary classification.

## QUICK LINKS

[![Live API docs](https://img.shields.io/badge/docs-GitHub_Pages-0366d6?logo=github)](https://labxscut.github.io/sxLaep/)

[Live API documentation](https://labxscut.github.io/sxLaep/) (PyDoc module tree)

[GitHub Repository](https://github.com/labxscut/sxLaep)

[API Reference](docs/API_REFERENCE.md)

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

> sxLaep (Rapid Enzyme/Non-Enzyme Prediction)
>
> The package is available for Python 3.7+ on Windows, Linux, and macOS.
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

> (1). # for use #
>
> First, install prerequisites: Python 3.7+, numpy, pandas, scikit-learn, xgboost, and joblib as specified in requirements.txt.
>
> Same for Linux, Mac OS, Windows, with a Conda-like Virtual Env.
>
> Then, install the package from PyPI:
>
> ```{.python .input}
> pip install sxlaep                              
> ```
>
> Import in Python:
>
> ```{.python .input}
> from sxlaep import sxlaep
> predictor = sxlaep()
> ```
>
> (2). # for development #
>
> sxLaep is open source and your contributions are greatly welcome.
>
> First, use git to clone a copy of sxLaep:
>
> ```{.python .input}
> user> git clone https://github.com/labxscut/sxLaep
> cd sxLaep
> user> pip install -e .
> ```

## QUICK START

> # Python API Usage #
>
> ```{.python .input}
> from sxlaep import sxlaep
>
> # Initialize predictor
> predictor = sxlaep()
>
> # Single sequence prediction
> pred = predictor.predict("MKVLW...")           # Returns: 0 (Non-Enzyme) or 1 (Enzyme)
> prob = predictor.predict_proba("MKVLW...")       # Returns: float (0.0 ~ 1.0)
>
> # FASTA file prediction
> results = predictor.predict_fasta("sequences.fasta")
> # Returns: {seq_id: {'prediction': int, 'probability': float}}
> ```

> # Command Line Usage #
>
> ```{.python .input}
> sxlaep --input sequences.fasta --output predictions.json
> ```

## EXECUTABLES

 1. The following command-line tools are available after installation:
 2. Use '--help' flag to see detailed usage for each command.
3. Examples are available in 'examples/' directory.
>
> ```{.python .input}
> sxlaep                           # main command-line tool for enzyme prediction
>                                # Usage: sxlaep --input <fasta> --output <json>
> ```

## REFERENCE PARAMETERS

### Feature Extraction Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lag` | int | 10 | Maximum correlation lag for pseudo-AAC. Controls the length of sequence-order correlation terms. Higher values capture longer-range dependencies but increase feature dimensionality. |
| `weight` | float | 0.05 | Weight applied to sequence-order correlation terms in pseudo-AAC. Balances between standard amino acid composition and sequence-order information. |
| `n_segments` | int | 3 | Number of N-to-C sequence windows for windowed AAC. Divides the sequence into equal segments for local composition analysis. |
| `add_length` | bool | True | Whether to append raw sequence length to the feature vector. Provides additional size information that may be correlated with enzyme function. |
| `properties` | dict | PROPERTIES | Amino-acid physicochemical property tables used by pseudo-AAC. Default includes: hydrophobicity (HYDRO), polarity (POLAR), and charge (CHARGE). |

### Command Line Arguments

#### `sxlaep` Command

| Argument | Required | Description |
|----------|----------|-------------|
| `--input`, `-i` | Yes | Input FASTA file path containing protein sequences to predict. |
| `--output`, `-o` | Yes | Output JSON file path for prediction results. |

### Output File Formats

#### JSON Output
```json
{
  "seq_id_1": {
    "prediction": 1,
    "probability": 0.876
  },
  "seq_id_2": {
    "prediction": 0,
    "probability": 0.234
  }
}
```

Where:
- `prediction`: 0 = Non-Enzyme, 1 = Enzyme
- `probability`: Enzyme probability score (0.0 ~ 1.0)

## EXAMPLES


> # Batch FASTA Processing #
>
> ```{.python .input}
> from sxlaep import sxlaep
>
> predictor = sxlaep()
> results = predictor.predict_fasta("proteins.fasta")
>
> for seq_id, result in results.items():
>     print(f"{seq_id}: {'Enzyme' if result['prediction'] == 1 else 'Non-Enzyme'} (p={result['probability']:.3f})")
> ```
>
> # Command Line Usage #
>
> ```{.python .input}
> sxlaep --input proteins.fasta --output predictions.json
> ```

## NOTES

> - The pre-trained model (`enzyme_xgb_model.pkl`) is included in the package.
> - The Python package name for installation is `sxlaep`: `pip install sxlaep`
> - Sequences containing non-standard amino acids are automatically sanitized (only the 20 standard amino acids are used).
> - Short sequences (< 10 amino acids) may yield less reliable predictions.
> - For large-scale predictions (>10,000 sequences), consider processing in batches or using a high-performance computing environment.

## CONTACT

> labxscut: labx2025@gmail.com

> GitHub: https://github.com/labxscut

## CITATIONS

Please cite sxLaep if you use it in your research:

> labxscut. sxLaep: a Lightweight and Accurate Enzyme Predictor for High-throughput Mining of Metagenomic Sequences. (2026).


