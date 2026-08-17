"""Evaluation-only local-embedding retrieval candidate for Context Builder Stage 2.

This module is NOT part of the core runtime and is NOT imported by
`runtime/context_builder.py` or any production path. It exists only to submit
one externally produced source-ranking candidate to the frozen, evaluation-only
Stage-2 evaluator in `runtime/context_retrieval_eval.py`, exactly the way that
module's own docstring/design invites ("future semantic/vector or other
candidates submit source rankings to evaluate_source_rankings against the same
frozen corpus/overlay").

Design constraints (see work/tasks/context-retrieval-semantic-wave4.md):

- No network embedding API is called per query. Embeddings are produced by a
  local, CPU-only ONNX model via the optional `fastembed` package. The model
  weights are fetched once (cached on disk) the first time an embedding model
  is constructed in a given environment; there is no per-query network call.
- `fastembed` is intentionally NOT added to `runtime/requirements.txt` (core
  runtime dependency list). It lives in `runtime/requirements-context-eval.txt`
  instead, and is imported lazily here so importing this module (and running
  the rest of the test suite) never requires it to be installed.
- The frozen explicit-source prefix from the Stage-2 overlay is preserved
  exactly the same way `explicit_only_rankings` / `same_path_drift_rankings`
  preserve it in `runtime/context_retrieval_eval.py`.
"""

from __future__ import annotations

import math
from typing import Mapping, Sequence

from .context_retrieval_eval import _prediction, _validate_overlay

try:  # pragma: no cover - exercised indirectly by presence/absence tests
    from fastembed import TextEmbedding

    _FASTEMBED_IMPORT_ERROR: Exception | None = None
except ImportError as exc:  # pragma: no cover - exercised when dep absent
    TextEmbedding = None  # type: ignore[assignment]
    _FASTEMBED_IMPORT_ERROR = exc


_DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Lazily constructed, process-wide model cache so repeated calls within one
# process (e.g. once per test run) do not reload the ONNX model per case.
_MODEL_CACHE: dict[str, "TextEmbedding"] = {}


def _require_fastembed() -> None:
    if TextEmbedding is None:
        raise RuntimeError(
            "runtime/context_retrieval_semantic.py requires the optional "
            "'fastembed' dependency, which is intentionally kept out of "
            "runtime/requirements.txt. Install it with:\n"
            "    pip install -r runtime/requirements-context-eval.txt"
        ) from _FASTEMBED_IMPORT_ERROR


def _get_model(model_name: str) -> "TextEmbedding":
    _require_fastembed()
    model = _MODEL_CACHE.get(model_name)
    if model is None:
        model = TextEmbedding(model_name=model_name)
        _MODEL_CACHE[model_name] = model
    return model


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_embedding_rankings(
    corpus: Mapping[str, object],
    overlay: Mapping[str, object],
    *,
    top_k: int = 1,
    minimum_similarity: float = 0.0,
    model_name: str = _DEFAULT_MODEL_NAME,
) -> list[dict[str, object]]:
    """Rank candidate sources per case by local embedding cosine similarity.

    For every case, the frozen `explicit_source_ids` prefix from the Stage-2
    overlay is preserved first (same contract as `explicit_only_rankings` /
    `same_path_drift_rankings` in `runtime/context_retrieval_eval.py`). Then,
    up to `top_k` additional sources not already in that prefix are appended,
    ordered by cosine similarity between a local embedding of the case's
    `query` text and a local embedding of each source's `path + content`
    text, provided that similarity is at least `minimum_similarity`.

    This performs real embedding-based ranking; it does not read or consult
    any expected-answer/ground-truth field of the corpus.
    """

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative int")

    sources, cases, order, explicit, _, _, _ = _validate_overlay(corpus, overlay)
    model = _get_model(model_name)

    source_ids = list(sources.keys())
    source_texts = [
        f"{sources[source_id]['path']}\n{sources[source_id]['content']}"
        for source_id in source_ids
    ]
    source_vectors = {
        source_id: vector
        for source_id, vector in zip(source_ids, model.embed(source_texts))
    }

    output: list[dict[str, object]] = []
    for case_id in order:
        prefix = list(explicit[case_id])
        selected = list(prefix)

        if top_k > 0:
            query_text = str(cases[case_id]["query"])
            query_vector = next(iter(model.embed([query_text])))

            scored = [
                (
                    source_id,
                    _cosine_similarity(query_vector, source_vectors[source_id]),
                )
                for source_id in source_ids
                if source_id not in prefix
            ]
            scored.sort(key=lambda item: (-item[1], item[0]))

            for source_id, similarity in scored:
                if similarity < minimum_similarity:
                    continue
                selected.append(source_id)
                if len(selected) >= len(prefix) + top_k:
                    break

        output.append(_prediction(case_id, selected))
    return output
