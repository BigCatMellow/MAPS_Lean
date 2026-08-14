# MAPS hcom Adapter

hcom is MAPS Lean's live cross-provider communication/session transport.

It is **not** task authority.

```text
hcom
messages / sessions / process control
        │
        ▼
runtime/communication/hcom_adapter.py
        │
        │ facts and explicit side effects only
        ▼
MAPS caller

SQLite task state is separate.
```

## Project isolation

Every adapter command sets:

```text
HCOM_DIR=<configured project-local directory>
```

Default:

```text
.hcom/
```

This prevents one clone's hcom sessions/messages from becoming another clone's
transport state.

## Supported operations

```text
version()
status()
list_sessions()
read_events()
send()
spawn()
resume()
stop()
```

Machine-readable reads use upstream-supported forms:

```bash
hcom list --json
hcom events --last N [filters]
```

`list_sessions()` requires a JSON array. `read_events()` requires JSON event
records. Invalid machine output fails with `HcomProtocolError`; MAPS does not
scrape the TUI/human display as a fallback.

## Side-effect boundary

`send`, `spawn`, `resume`, and `stop` are explicit side-effecting operations.
The adapter:

- constructs an argv list;
- invokes hcom with `shell=False`;
- never interpolates a shell command;
- rejects broad `kill all` / `tag:*` fan-out in `stop()`;
- does not choose a WezTerm terminal by default;
- supports headless launch/resume.

A caller still needs MAPS authority to decide that one of those operations
should happen.

## What hcom state cannot prove

These are **not** valid inferences:

```text
message sent       != task assigned
message received   != task accepted
session active     != task owned
agent says "done"  != task DONE
message intent     != decision authority
session stopped    != claim abandoned
```

Canonical lifecycle changes still require guarded MAPS operations and their
normal evidence/review rules.

## Durable outcomes

A useful message may lead to a durable MAPS update, but promotion is separate:

```text
hcom conversation
      ↓
result matters beyond the conversation?
      ↓ yes
separate authorized MAPS operation
      ↓
task / decision / review / handoff / evidence
```

Do not mirror hcom's whole event/message database into MAPS.

## Tests

`tests/test_hcom_adapter.py` creates a temporary fake `hcom` executable and
checks argv, `HCOM_DIR`, JSON parsing, typed failures, no-WezTerm behavior, and
the no-task-store dependency boundary. It performs no real hcom side effects.
