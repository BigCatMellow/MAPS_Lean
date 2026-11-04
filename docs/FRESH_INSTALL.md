# Fresh Clone Setup

For Linux/macOS, use the preview-first installer from the repository root:

```bash
bash scripts/install_maps.sh
```

That command **does not write anything**. It prints the actions it would take.

When the preview is correct:

```bash
bash scripts/install_maps.sh --apply --run-smoke
```

To install hcom as well:

```bash
bash scripts/install_maps.sh --apply --install-hcom --run-smoke
```

## What it creates

Project-local:

```text
.venv/
.maps/state/
.hcom/
```

It installs `runtime/requirements.txt` into `.venv`.

If `--install-hcom` is requested, hcom stays separate from the project Python
environment:

1. use `uv tool install "$HCOM_SOURCE"` when `uv` exists; otherwise
2. create `$HOME/.local/share/hcom-venv`, `pip install -U "$HCOM_SOURCE"`
   there, and link the executable into `$HOME/.local/bin/hcom`.

`HCOM_SOURCE` is temporarily pinned (in `scripts/install_maps.sh`) to the
`BigCatMellow/hcom` fork branch that adds `--json` output to `hcom send`
(upstream [PR #107](https://github.com/aannoo/hcom/pull/107), open and
unreviewed as of 2026-08-17). Revert the pin to plain `hcom` (PyPI) once #107
merges upstream, or override it for one run without editing the script:

```bash
HCOM_SOURCE=hcom bash scripts/install_maps.sh --apply --install-hcom --run-smoke
```

hcom is a Rust binary; installing from source (the fork) builds it locally
with `cargo`/`rustc`, which is slower than the prebuilt PyPI wheel -- expect
the install step to take noticeably longer while this pin is in effect.

It does not use `sudo`, install a terminal multiplexer, or create/change API
keys and credentials.

## Smoke verification

The smoke command can also be run directly:

```bash
.venv/bin/python -m runtime.smoke --with-langgraph
```

If hcom is installed:

```bash
.venv/bin/python -m runtime.smoke --with-langgraph --with-hcom
```

The smoke uses a temporary directory. It verifies:

- SQLite foreign keys, WAL, and busy timeout;
- task creation/shaping;
- structural AGI `READY` promotion;
- atomic claim path;
- submission evidence;
- independent review;
- final `DONE` state;
- optional LangGraph checkpoint DB separation;
- optional `hcom --version` only.

It does **not** send messages, launch/kill agents, run Ollama/Aider, or touch the
real project task database.

## External Git project: portable Markdown convention (candidate)

From the MAPS_L clone, point both commands at **existing, distinct Git roots**.
Paths must be canonical, with no symlinked roots. This portable-v1 path is
independent of the MAPS runtime installer above and does **not** set up SQLite,
hcom, dependencies, Git hooks, CI, or target-project code execution.

Read-only inspection:

```bash
python3 scripts/portable_target_preflight.py --maps-root /path/to/MAPS_Lean --target-repo /path/to/project
```

Preview initialization (also read-only):

```bash
python3 scripts/portable_target_init.py --maps-root /path/to/MAPS_Lean --target-repo /path/to/project
```

Explicitly initialize missing `.maps/` Markdown and task/review/handoff
directories only after inspecting the preview:

```bash
python3 scripts/portable_target_init.py --maps-root /path/to/MAPS_Lean --target-repo /path/to/project --apply
```

Existing target files are never overwritten. Inspect generated files and
commit them under **the target project's own authority**. An empty portable
convention does not mean a task is ready, reviewed, authorized, or finished.
The first real external-project pilot (Roadmap D3) remains a separate gate.

## Windows

The Bash installer is not the Windows installer. Follow
`docs/CONTROL_PLANE_SETUP.md` manually from PowerShell for now. The Python
runtime and smoke command remain portable once the virtual environment and
dependencies are installed.

## No legacy dependency

Fresh setup and smoke operate entirely from active `runtime/` code. They do not
read or execute `legacy/` or either migration snapshot.
