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

1. use `uv tool install hcom` when `uv` exists; otherwise
2. create `$HOME/.local/share/hcom-venv` and link the executable into
   `$HOME/.local/bin/hcom`.

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

## Windows

The Bash installer is not the Windows installer. Follow
`docs/CONTROL_PLANE_SETUP.md` manually from PowerShell for now. The Python
runtime and smoke command remain portable once the virtual environment and
dependencies are installed.

## No legacy dependency

Fresh setup and smoke operate entirely from active `runtime/` code. They do not
read or execute `legacy/` or either migration snapshot.
