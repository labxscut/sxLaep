#!/usr/bin/env bash
#
# Stand-alone helper: run from the tests/ directory (this script lives there).
#   cd tests && ./install.sh
#
# - Downloads sample FASTAs from GitHub raw if missing in this folder.
# - Installs or upgrades sxlaep with pipx from PyPI only (reliable wheels).
# - Runs sxlaep --help and sxlaep --input example.fasta (bundled model) after install (skip: SXLAEP_SKIP_CLI_SMOKE=1).
# No sudo. For unit tests: pytest tests/ from repo root.
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

REPO_ROOT="$(cd ".." && pwd)"
ORIG_PATH="${PATH}"

PIP_ARGS="${SXLAEP_PIP_ARGS:---prefer-binary -v --default-timeout=120}"
# Branch segment for raw.githubusercontent.com sample FASTA URLs (not used for pipx).
RAW_REF="${SXLAEP_RAW_REF:-main}"
RAW_BASE="${SXLAEP_RAW_BASE:-https://raw.githubusercontent.com/labxscut/sxLaep/${RAW_REF}/tests}"

FETCH_RETRIES="${SXLAEP_FETCH_RETRIES:-5}"
CURL_CONNECT_TIMEOUT="${SXLAEP_CURL_CONNECT_TIMEOUT:-60}"
CURL_MAX_TIME="${SXLAEP_CURL_MAX_TIME:-240}"
WGET_TIMEOUT="${SXLAEP_WGET_TIMEOUT:-60}"

export PATH="${HOME}/.local/bin:${PATH}"

usage() {
  cat <<'EOF'
Usage (run from tests/):

  cd tests && ./install.sh

Installs or upgrades sxlaep via pipx from PyPI. Sample FASTAs are downloaded
from GitHub raw into this directory if missing. After install, runs
sxlaep --help then sxlaep --input example.fasta (copy of enzyme_example.fasta
in a temp dir) and shows a short CSV preview (set SXLAEP_SKIP_CLI_SMOKE=1 to skip).

Environment (optional):
  SXLAEP_RAW_BASE       Override raw URL prefix (must end at .../tests)
  SXLAEP_RAW_REF        Branch for default RAW_BASE (default: main)
  SXLAEP_PIP_ARGS       Extra args for pip inside pipx (shlex-split string)
  PIP_DEFAULT_TIMEOUT   Seconds for pip (default: 120)
  SXLAEP_FETCH_RETRIES, SXLAEP_CURL_CONNECT_TIMEOUT, SXLAEP_CURL_MAX_TIME, SXLAEP_WGET_TIMEOUT
  SXLAEP_SKIP_CLI_SMOKE   set to 1 to skip post-install sxlaep --help and --input smoke tests
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    *) echo "[ERROR]: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

info_stream() {
  echo "[INFO]: --- $(printf '%q ' "$@")---"
  local _st
  if command -v stdbuf >/dev/null 2>&1; then
    PYTHONUNBUFFERED=1 stdbuf -oL -eL "$@" 2>&1 | stdbuf -oL sed -u 's/^/[INFO]: /'
  else
    PYTHONUNBUFFERED=1 "$@" 2>&1 | sed -u 's/^/[INFO]: /'
  fi
  _st="${PIPESTATUS[0]:-0}"
  return "${_st}"
}

run_cli_post_install_smoke() {
  local td out ex
  echo "[INFO]: post-install CLI smoke (1/2): sxlaep --help"
  info_stream sxlaep --help
  echo "[INFO]: CLI smoke (1/2) OK — sxlaep --help succeeded."

  if [[ ! -f "${PWD}/enzyme_example.fasta" ]]; then
    echo "[ERROR]: enzyme_example.fasta missing; cannot run --input smoke" >&2
    exit 1
  fi
  td="$(mktemp -d)" || {
    echo "[ERROR]: mktemp -d failed" >&2
    exit 1
  }
  ex="${td}/example.fasta"
  out="${td}/predictions.csv"
  cp -f "${PWD}/enzyme_example.fasta" "${ex}"
  echo "[INFO]: post-install CLI smoke (2/2): sxlaep --input example.fasta --output predictions.csv (cwd=${td})"
  if ! (cd "${td}" && info_stream sxlaep --input example.fasta --output predictions.csv); then
    rm -rf "${td}"
    echo "[ERROR]: sxlaep --input example.fasta smoke command failed" >&2
    exit 1
  fi
  if [[ ! -f "${out}" ]]; then
    rm -rf "${td}"
    echo "[ERROR]: expected output CSV missing: ${out}" >&2
    exit 1
  fi
  if ! grep -q pred_label "${out}"; then
    rm -rf "${td}"
    echo "[ERROR]: --input run produced CSV without pred_label column" >&2
    exit 1
  fi
  echo "[INFO]: --input smoke CSV preview (first 8 lines):"
  if ! info_stream head -n 8 "${out}"; then
    rm -rf "${td}"
    echo "[ERROR]: failed to preview smoke CSV" >&2
    exit 1
  fi
  rm -rf "${td}"
  echo "[INFO]: CLI smoke test PASSED — sxlaep --help and --input example.fasta checks completed."
}

_fetch_one_curl() {
  local dest="$1" url="$2"
  local curl_cmd=(curl -fSL
    --connect-timeout "${CURL_CONNECT_TIMEOUT}"
    --max-time "${CURL_MAX_TIME}"
    --retry 4
    --retry-delay 4
    --retry-connrefused
    -o "${dest}"
    "${url}")
  if command -v stdbuf >/dev/null 2>&1; then
    stdbuf -oL -eL "${curl_cmd[@]}" 2>&1 | stdbuf -oL sed -u 's/^/[INFO]: /'
  else
    "${curl_cmd[@]}" 2>&1 | sed -u 's/^/[INFO]: /'
  fi
  return "${PIPESTATUS[0]:-0}"
}

fetch_if_missing() {
  local relpath="$1"
  local dest="${PWD}/${relpath}"
  local url _st _tmp _attempt
  if [[ -f "${dest}" ]]; then
    echo "[INFO]: already present: ${relpath}"
    return 0
  fi
  mkdir -p "$(dirname "${dest}")"
  url="${RAW_BASE}/${relpath}"
  echo "[INFO]: downloading ${relpath} from ${url}"
  if command -v curl >/dev/null 2>&1; then
    _tmp="${dest}.part.$$"
    rm -f "${_tmp}"
    _attempt=1
    while [[ "${_attempt}" -le "${FETCH_RETRIES}" ]]; do
      echo "[INFO]: curl attempt ${_attempt}/${FETCH_RETRIES} (connect=${CURL_CONNECT_TIMEOUT}s max=${CURL_MAX_TIME}s per attempt)"
      set +e
      _fetch_one_curl "${_tmp}" "${url}"
      _st=$?
      set -e
      if [[ "${_st}" -eq 0 && -s "${_tmp}" ]]; then
        mv -f "${_tmp}" "${dest}"
        echo "[INFO]: fetch complete: ${relpath}"
        return 0
      fi
      rm -f "${_tmp}"
      echo "[WARN]: download failed (curl exit ${_st}), relpath=${relpath}"
      if [[ "${_attempt}" -lt "${FETCH_RETRIES}" ]]; then
        sleep $((_attempt * 4))
      fi
      ((_attempt += 1))
    done
    echo "[ERROR]: gave up after ${FETCH_RETRIES} attempts: ${url}" >&2
    return 1
  elif command -v wget >/dev/null 2>&1; then
    _attempt=1
    while [[ "${_attempt}" -le "${FETCH_RETRIES}" ]]; do
      echo "[INFO]: wget attempt ${_attempt}/${FETCH_RETRIES} (timeout=${WGET_TIMEOUT}s tries=4)"
      set +e
      if wget --help 2>&1 | grep -q -- '--show-progress'; then
        info_stream wget --timeout="${WGET_TIMEOUT}" --tries=4 --show-progress -O "${dest}" "${url}"
      else
        info_stream wget --timeout="${WGET_TIMEOUT}" --tries=4 -nv -O "${dest}" "${url}"
      fi
      _st=$?
      set -e
      if [[ "${_st}" -eq 0 && -s "${dest}" ]]; then
        echo "[INFO]: fetch complete: ${relpath}"
        return 0
      fi
      rm -f "${dest}"
      echo "[WARN]: download failed (wget exit ${_st})"
      if [[ "${_attempt}" -lt "${FETCH_RETRIES}" ]]; then
        sleep $((_attempt * 4))
      fi
      ((_attempt += 1))
    done
    echo "[ERROR]: gave up after ${FETCH_RETRIES} attempts: ${url}" >&2
    return 1
  else
    echo "[ERROR]: need curl or wget to fetch ${url}" >&2
    exit 1
  fi
}

echo "[INFO]: working directory (tests): ${PWD}"
echo "[INFO]: repo root (parent): ${REPO_ROOT}"

fetch_if_missing "enzyme_example.fasta"
fetch_if_missing "noenzyme_example.fasta"

command -v pipx >/dev/null 2>&1 || {
  echo "[ERROR]: pipx not found — https://pypa.github.io/pipx/" >&2
  exit 1
}

PIPX_HOME="${PIPX_HOME:-${HOME}/.local/share/pipx}"
echo "[INFO]: PIPX_HOME=${PIPX_HOME}  (install source: PyPI only)"

export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"

echo "[INFO]: checking existing pipx installs (pipx list --short)"
PIPX_LIST_OUT="$(pipx list --short 2>&1 || true)"
if [[ -n "${PIPX_LIST_OUT}" ]]; then
  printf '%s\n' "${PIPX_LIST_OUT}" | sed -u 's/^/[INFO]: /'
else
  echo "[INFO]: (pipx list --short produced no output)"
fi
if printf '%s\n' "${PIPX_LIST_OUT}" | awk '{print $1}' | grep -qx sxlaep; then
  echo "[INFO]: sxlaep already listed; upgrading from PyPI"
  info_stream pipx upgrade --verbose sxlaep --pip-args "${PIP_ARGS}" || info_stream pipx install --verbose sxlaep --pip-args "${PIP_ARGS}"
else
  echo "[INFO]: sxlaep not listed; installing from PyPI"
  info_stream pipx install --verbose sxlaep --pip-args "${PIP_ARGS}"
fi

hash -r 2>/dev/null || true
command -v sxlaep >/dev/null 2>&1 || {
  echo "[ERROR]: sxlaep not found even with ~/.local/bin prepended — check pipx install output" >&2
  exit 1
}

SXLAEP_ABS="$(command -v sxlaep)"
BIN_DIR="$(dirname "${SXLAEP_ABS}")"
echo "[INFO]: sxlaep → ${SXLAEP_ABS}"

if [[ "${SXLAEP_SKIP_CLI_SMOKE:-}" == "1" ]]; then
  echo "[INFO]: skipping CLI smoke test (SXLAEP_SKIP_CLI_SMOKE=1)"
else
  run_cli_post_install_smoke
fi

if PATH="${ORIG_PATH}" command -v sxlaep >/dev/null 2>&1; then
  echo "[INFO]: sxlaep is already on your default PATH (no shell config change needed)."
else
  echo "[WARN]: sxlaep is installed under ${BIN_DIR} but that directory is not on your default PATH."
  echo "      New terminals may not find 'sxlaep' until you fix this."
  echo
  echo "Recommended (pipx will update your shell startup when possible):"
  echo "  pipx ensurepath"
  echo "  # then close and reopen the terminal (or: exec \$SHELL -l)"
  echo
  echo "Or add this line permanently to ~/.bashrc and/or ~/.zshrc:"
  echo "  export PATH=\"${BIN_DIR}:\$PATH\""
  echo
  echo "For Fish, add to ~/.config/fish/config.fish:"
  echo "  fish_add_path ${BIN_DIR}"
fi

echo "[INFO]: done. Try: sxlaep --help   (sample FASTAs are in ${PWD})"
