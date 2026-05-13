# Summary of Modification Requests for the sxLaep Repository

## Please apply the following changes to `README.md` and the project configuration:

## 1. Expose Feature Extraction Parameters to Command Line

- **Location**: `Feature Extraction Parameters` under the `REFERENCE PARAMETERS` section in `README.md`
- **Requirement**: Make all these feature extraction parameters (e.g., window size, amino acid property selection, etc.) accessible via the command-line interface (CLI). Users must be able to specify them directly from the command line without modifying the source code.

## 2. Quick Links Adjustment & Performance Fix

- **Issue**: The `Workflow Documentation` link under `QUICK LINKS` loads very slowly.
- **Requirements**:
  - Diagnose and fix the slow loading issue to ensure fast page access.
  - Change the link name from `Workflow Documentation` to **`cmdline workflow example`**.
  - Update the content of the linked document to match the new title, focusing on command-line workflow examples.

## 3. Installation and Self-Test Enhancement

- **Original installation command**: `pip install sxlaep`
- **New installation command**: Use `pipx` for installation – `pipx install sxlaep` – to provide better environment isolation and clean command-line application support.
- **Additional self-test step**: After the installation instructions, add a standard Python `unittest` self-test procedure to verify that the tool works correctly. This allows users to confirm the installation is successful and the tool is ready for use.
