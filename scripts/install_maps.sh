#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPLY=0
INSTALL_HCOM=0
RUN_SMOKE=0

usage() {
  cat <<'EOF'
Usage: scripts/install_maps.sh [--apply] [--install-hcom] [--run-smoke]

Default is preview only. Nothing is written unless --apply is supplied.

  --apply         Perform the displayed project-local/user-local writes.
  --install-hcom  Install hcom separately (uv tool preferred, fallback venv).
  --run-smoke     Run the active runtime smoke suite after setup.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --install-hcom) INSTALL_HCOM=1 ;;
    --run-smoke) RUN_SMOKE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

command -v python3 >/dev/null 2>&1 || { echo "error: python3 is required" >&2; exit 1; }

show_cmd() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
}

run() {
  show_cmd "$@"
  if [[ "$APPLY" -eq 1 ]]; then
    "$@"
  fi
}

VENV="$ROOT/.venv"
PY="$VENV/bin/python"

echo "MAPS Lean setup root: $ROOT"
if [[ "$APPLY" -eq 0 ]]; then
  echo "Mode: PREVIEW (use --apply to write)"
else
  echo "Mode: APPLY"
fi

echo
echo "Project-local runtime setup:"
run mkdir -p "$ROOT/.maps/state" "$ROOT/.hcom"
if [[ ! -x "$PY" ]]; then
  run python3 -m venv "$VENV"
else
  echo "+ existing virtualenv: $VENV"
fi

if [[ "$APPLY" -eq 1 ]]; then
  run "$PY" -m pip install --upgrade pip
  run "$PY" -m pip install -r "$ROOT/runtime/requirements.txt"
else
  show_cmd "$PY" -m pip install --upgrade pip
  show_cmd "$PY" -m pip install -r "$ROOT/runtime/requirements.txt"
fi

if [[ "$INSTALL_HCOM" -eq 1 ]]; then
  echo
echo "Separate hcom installation:"
  if command -v hcom >/dev/null 2>&1; then
    echo "+ hcom already available: $(command -v hcom)"
  elif command -v uv >/dev/null 2>&1; then
    run uv tool install hcom
  else
    HCOM_VENV="$HOME/.local/share/hcom-venv"
    HCOM_BIN="$HOME/.local/bin/hcom"
    run mkdir -p "$HOME/.local/share" "$HOME/.local/bin"
    if [[ ! -x "$HCOM_VENV/bin/python" ]]; then
      run python3 -m venv "$HCOM_VENV"
    fi
    if [[ "$APPLY" -eq 1 ]]; then
      run "$HCOM_VENV/bin/python" -m pip install --upgrade pip
      run "$HCOM_VENV/bin/python" -m pip install -U hcom
      run ln -sfn "$HCOM_VENV/bin/hcom" "$HCOM_BIN"
    else
      show_cmd "$HCOM_VENV/bin/python" -m pip install --upgrade pip
      show_cmd "$HCOM_VENV/bin/python" -m pip install -U hcom
      show_cmd ln -sfn "$HCOM_VENV/bin/hcom" "$HCOM_BIN"
    fi
  fi
fi

if [[ "$RUN_SMOKE" -eq 1 ]]; then
  echo
echo "Smoke verification:"
  smoke=("$PY" -m runtime.smoke --with-langgraph)
  if command -v hcom >/dev/null 2>&1; then
    smoke+=(--with-hcom)
  fi
  if [[ "$APPLY" -eq 1 ]]; then
    (cd "$ROOT" && "${smoke[@]}")
  else
    printf '+ cd %q &&' "$ROOT"
    printf ' %q' "${smoke[@]}"
    printf '\n'
  fi
fi

echo
if [[ "$APPLY" -eq 0 ]]; then
  echo "Preview complete. Re-run with --apply when the commands look correct."
else
  echo "Setup complete. No credentials or API keys were created or changed."
fi
