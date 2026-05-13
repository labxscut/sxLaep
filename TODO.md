# Summary of Modification Requests for the sxLaep Repository

## Original requests (status)

### 1. Expose feature extraction parameters to the command line

- **Location**: `Feature Extraction Parameters` under `REFERENCE PARAMETERS` in `README.md`
- **Requirement**: Expose window size, amino acid property selection, and related knobs on the CLI without editing source.
- **Status**: **Not done** — still pending implementation in `sxlaep/cli.py` (and wiring into predict/train paths).

### 2. Quick links adjustment and performance fix

- **Issue**: `Workflow Documentation` under `QUICK LINKS` is slow to open.
- **Requirements**: Fix slow loading; rename link to **`cmdline workflow example`**; align `docs/WORKFLOW.md` with that focus.
- **Status**: **Not done** — README still says “Workflow Documentation”; no perf work on that link yet.

### 3. Installation and self-test enhancement

- **Original ask**: Prefer `pipx install sxlaep`; add a post-install **self-test** so users can verify the install.
- **Status**: **Largely done** (see changelog). README recommends **pipx**; end users can run **`cd tests && ./install.sh`** (GitHub `main` vs PyPI, optional raw fetch of sample FASTAs). **Self-test** is implemented as **`pytest tests/`** (and demo test against bundled **`.ubj`**) rather than `unittest` — same intent, standard for this repo.

---

## Change log (recent work)

The following was implemented and should appear in the next commit to `main`:

### End-user install (`tests/install.sh`)

- Script lives under **`tests/`**; it **`cd`s** to its directory so the working root is always **`tests/`**.
- **`pipx`**: interactive **GitHub (`SXLAEP_GIT_REF`, default `main`)** vs **PyPI**, or **`--git` / `--pypi`**; env **`SXLAEP_INSTALL_SOURCE`**, **`CI=true`** for non-interactive defaults.
- **Git install**: requires **`git`** on `PATH`; uses PEP **`sxlaep @ git+…`** spec; exports **`PIP_DEFAULT_TIMEOUT`** and default pip args include **`--default-timeout=120`** to reduce PyPI timeouts during dependency install.
- **Sample FASTAs**: **`enzyme_example.fasta`** and **`noenzyme_example.fasta`** are both under **`tests/`** (no `fixtures/` path). If missing locally, they are downloaded from **`SXLAEP_RAW_BASE`** (default `raw.githubusercontent.com/.../${GIT_REF}/tests`).
- **Network robustness**: curl uses **`--connect-timeout`**, **`--max-time`**, built-in **`--retry`**, plus an outer loop (**`SXLAEP_FETCH_RETRIES`**) with backoff; wget uses **`--timeout`** and **`--tries`** with the same outer loop. Optional env: **`SXLAEP_CURL_CONNECT_TIMEOUT`**, **`SXLAEP_CURL_MAX_TIME`**, **`SXLAEP_WGET_TIMEOUT`**.
- **Logging**: subprocess output for **`pipx`** / **`wget`** is streamed with an **`[INFO]:`** prefix where applicable.

### Tests and layout

- **`tests/noenzyme_example.fasta`** added at repo root of `tests/`; **`tests/fixtures/noenzyme_example.fasta`** (and fixtures README) removed.
- **`tests/test_demo_example.py`** reads both FASTAs from **`tests/`**.
- **`tests/support_paths.py`**: **`bundled_ubj_path()`** resolves packaged **`.ubj`** for **pipx** installs or editable tree.
- **`tests/test_model_load.py`** uses **`bundled_ubj_path()`** so skips are correct when the model is only inside the wheel.
- Removed root **`test.sh`** in favor of **`tests/install.sh`** for install-only flow.

### Docs

- **`README.md`**: pipx-first install narrative; **`EXECUTABLES`** bullet documents **`cd tests && ./install.sh`**, example FASTA paths, raw **`SXLAEP_RAW_BASE`**, and **`pytest tests/`** for developers.

---

## Checklist (quick view)

- [ ] **§1** — CLI flags for all feature-extraction parameters documented in README and implemented in code.
- [ ] **§2** — Quick link rename + `WORKFLOW.md` refresh + slow-load fix.
- [x] **§3** — pipx-first install docs; post-install verification via **`pytest tests/`** and **`tests/install.sh`**; bundled **`.ubj`** test path fixed for pipx layouts.
