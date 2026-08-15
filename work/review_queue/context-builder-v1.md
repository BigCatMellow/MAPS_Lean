# Review packet: Context Builder v1

- Status: `QUEUED`
- PR: `#19`
- Task record: `work/tasks/context-builder-v1.md`
- CI evidence: Runtime stack tests run `31886431884` passed with the context
  builder and `tests/test_context_builder.py` present.

## Review scope

Inspect:

- `runtime/context_builder.py`
- `runtime/cli.py`
- `tests/test_context_builder.py`
- `runtime/README.md`

## Intended behavior

- derive context only from canonical task relationships and current exact files;
- include root `AGENTS.md` as repository authority when present;
- hash referenced files and report repo-relative path/size/role;
- preserve descriptive/external references without pretending they are files;
- report missing, outside-repo, and directory references explicitly;
- include dependency state and task boundaries;
- never scan unrelated repository files;
- never include file contents in v1;
- explicitly report that semantic retrieval is not used.

## Review questions

1. Does any path handling permit reading through/outside `repo_root`?
2. Are descriptive references safely distinguished from probable file paths?
3. Is automatically including root `AGENTS.md` the correct minimal authority
   rule without expanding into a hidden policy-discovery system?
4. Does the plan preserve enough task boundary/acceptance information to guide a
   fresh agent without becoming a second task record?
5. Is the absence of semantic retrieval/scanning explicit enough that callers
   cannot mistake this for complete repository discovery?
6. Are hashes/current file metadata sufficient evidence for this first version?

## Intentionally deferred

- no file-content materialization;
- no embeddings/vector database;
- no lexical claim-card retriever;
- no semantic query expansion;
- no persistent context cache/index;
- no inferred relationships;
- no knowledge graph.

Future retrieval work should be evaluated on frozen paraphrase/vocabulary-shift
queries, hard negatives, abstention, exact evidence anchors, and source drift
before promotion.
