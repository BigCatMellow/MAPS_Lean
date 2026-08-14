#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
RUNTIME="$ROOT/runtime"
HCOM_JSON="$RUNTIME/hcom-live.json"
RECON_JSON="$RUNTIME/agent-reconciliation.json"
LIVENESS_JSON="$RUNTIME/liveness-check.json"

mkdir -p "$RUNTIME"
tmp_hcom="$HCOM_JSON.tmp"
tmp_recon="$RECON_JSON.tmp"
tmp_liveness="$LIVENESS_JSON.tmp"
trap 'rm -f "$tmp_hcom" "$tmp_recon" "$tmp_liveness"' EXIT HUP INT TERM

hcom list --json > "$tmp_hcom"
python3 "$ROOT/scripts/reconcile_agents.py" \
  --hcom-json "$tmp_hcom" --json > "$tmp_recon"
python3 "$ROOT/scripts/liveness_reaper.py" \
  --hcom-json "$tmp_hcom" \
  --snapshot-out "$ROOT/shared/liveness-state.md" \
  --json > "$tmp_liveness"

mv "$tmp_hcom" "$HCOM_JSON"
mv "$tmp_recon" "$RECON_JSON"
mv "$tmp_liveness" "$LIVENESS_JSON"
trap - EXIT HUP INT TERM
