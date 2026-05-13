#!/usr/bin/env bash
#
# Stand-alone installer: run from the tests/ directory (this script lives there).
#   cd tests && ./install.sh
#
# - Downloads sample FASTAs from GitHub raw if missing in this folder.
# - Installs sxlaep with pipx (default: GitHub main; optional PyPI).
# No sudo. For unit tests: pytest .  (from repo root) or pytest tests/
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
# From here on, the invoking / working root is tests/

REPO_ROOT="$(cd ".." && pwd)"
ORIG_PATH="${PATH}"

# pipx passes these to pip (shlex-split). Include a longer default timeout for slow networks.
PIP_ARGS="${SXLAEP_PIP_ARGS:---prefer-binary -v --default-timeout=120}"
GIT_URL="${SXLAEP_GIT_URL:-https://github.com/labxscut/sxLaep.git}"
# Branch or tag for git installs (default matches GitHub default_branch).
GIT_REF="${SXLAEP_GIT_REF:-main}"
# Base URL for files under tests/ on GitHub (override branch or whole tree).
RAW_BASE="${SXLAEP_RAW_BASE:-https://raw.githubusercontent.com/labxscut/sxLaep/${GIT_REF}/tests}"

# Sample FASTA fetch (curl): slow networks / flaky DNS (curl exit 28).
FETCH_RETRIES="${SXLAEP_FETCH_RETRIES:-5}"
CURL_CONNECT_TIMEOUT="${SXLAEP_CURL_CONNECT_TIMEOUT:-60}"
CURL_MAX_TIME="${SXLAEP_CURL_MAX_TIME:-240}"
WGET_TIMEOUT="${SXLAEP_WGET_TIMEOUT:-60}"

SOURCE="${SXLAEP_INSTALL_SOURCE:-${SXLAEP_TEST_SOURCE:-}}"
SOURCE_FROM_ENV=0
if [[ -n "${SXLAEP_INSTALL_SOURCE:-}" || -n "${SXLAEP_TEST_SOURCE:-}" ]]; then
  SOURCE_FROM_ENV=1
fi
if [[ -z "${SOURCE}" ]]; then
  SOURCE=git
fi

SOURCE_FROM_CLI=0
export PATH="${HOME}/.local/bin:${PATH}"

usage() {
  cat <<'EOF'
Usage (run from tests/):

  cd tests && ./install.sh [--pypi | --git]

  (no flags)   Interactive: GitHub main (default) vs PyPI.
  --git        pipx from git main (no prompt; default when non-interactive).
  --pypi       pipx from PyPI (no prompt).

Sample FASTAs: fetched into this directory from GitHub raw if missing.
  Override base URL: SXLAEP_RAW_BASE (must point at .../tests on raw.githubusercontent.com)

Other env:
  SXLAEP_GIT_URL, SXLAEP_GIT_REF (default main), SXLAEP_PIP_ARGS, SXLAEP_INSTALL_SOURCE, CI=true
  PIP_DEFAULT_TIMEOUT  seconds for pip (default 120 if unset; pip also honors this env)
  SXLAEP_FETCH_RETRIES, SXLAEP_CURL_CONNECT_TIMEOUT, SXLAEP_CURL_MAX_TIME, SXLAEP_WGET_TIMEOUT
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pypi) SOURCE=pypi; SOURCE_FROM_CLI=1 ;;
    --git) SOURCE=git; SOURCE_FROM_CLI=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[ERROR]: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

# Run a command with merged stdout/stderr; each line is echoed as "[INFO]: …".
# Preserves the command's exit status (first stage of pipeline) under pipefail.
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

_fetch_one_curl() {
  # Logged download: long connect/data limits, curl-level retries, then [INFO]: prefixes.
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

choose_source_interactive() {
  echo
  echo "Where should pipx install sxlaep from?"
  echo "  1) GitHub — latest ${GIT_REF} (default)"
  echo "       ${GIT_URL}@${GIT_REF}"
  echo "  2) PyPI   — stable release"
  echo
  echo -n "Press Enter for [1], or type 1 / 2: "
  read -r _choice || true
  case "${_choice:-1}" in
    1|git|Git|GIT|""|y|Y|yes|Yes) SOURCE=git ;;
    2|pypi|Pypi|PYPI) SOURCE=pypi ;;
    *)
      echo "[WARN]: Unrecognized choice '${_choice}', using GitHub main (1)."
      SOURCE=git
      ;;
  esac
  echo "[INFO]: Selected source: ${SOURCE}"
}

if [[ "${SOURCE_FROM_CLI}" -eq 0 && "${SOURCE_FROM_ENV}" -eq 0 ]]; then
  if [[ -t 0 ]] && [[ "${CI:-}" != "true" ]]; then
    choose_source_interactive
  else
    echo "[INFO]: Non-interactive shell (or CI); using default: git (GitHub ${GIT_REF})"
    SOURCE=git
  fi
fi

command -v pipx >/dev/null 2>&1 || {
  echo "[ERROR]: pipx not found — https://pypa.github.io/pipx/" >&2
  exit 1
}

PIPX_HOME="${PIPX_HOME:-${HOME}/.local/share/pipx}"
echo "[INFO]: PIPX_HOME=${PIPX_HOME}  source=${SOURCE}"

# pip subprocesses (dependency wheels from PyPI) honor this even when not in PIP_ARGS.
export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"

if [[ "${SOURCE}" == "git" ]]; then
  command -v git >/dev/null 2>&1 || {
    echo "[ERROR]: pipx install from GitHub needs the 'git' command on PATH (pip clones the repo). Install git and retry." >&2
    exit 1
  }
  # PEP 508 name + URL avoids ambiguous VCS resolution and matches pyproject name.
  _git_url="${GIT_URL#git+}"
  GIT_PIP_SPEC="sxlaep @ git+${_git_url}@${GIT_REF}"
  echo "[INFO]: pip spec: ${GIT_PIP_SPEC}"
  echo "[INFO]: pipx may sit on 'determining package name' for several minutes: it clones the repo and runs pip in a temporary venv (deps, wheels). Not frozen unless CPU/network are idle for 20+ min."
  info_stream pipx install --verbose --force "${GIT_PIP_SPEC}" --pip-args "${PIP_ARGS}"
else
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
fi

hash -r 2>/dev/null || true
command -v sxlaep >/dev/null 2>&1 || {
  echo "[ERROR]: sxlaep not found even with ~/.local/bin prepended — check pipx install output" >&2
  exit 1
}

SXLAEP_ABS="$(command -v sxlaep)"
BIN_DIR="$(dirname "${SXLAEP_ABS}")"
echo "[INFO]: sxlaep → ${SXLAEP_ABS}"

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
