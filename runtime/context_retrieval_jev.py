"""Evaluation-only Jev context-relevance candidate.

This module is intentionally not imported by runtime/context_builder.py. It may
send source bodies to an external provider, so callers must explicitly enable
DecisionConfig.allow_content. Passing the frozen evaluation is evidence for a
future proposal only; it never promotes itself into production retrieval.
"""

from __future__ import annotations

from typing import Mapping

from runtime.decision import DecisionBroker

from .context_retrieval_eval import _prediction, _validate_overlay


def jev_context_rankings(
    corpus: Mapping[str, object],
    overlay: Mapping[str, object],
    *,
    broker: DecisionBroker,
    top_k: int = 1,
) -> list[dict[str, object]]:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative int")
    if not broker.config.allow_content:
        raise ValueError(
            "Jev context evaluation requires allow_content=true because source "
            "bodies are sent to the configured decision provider"
        )

    sources, cases, order, explicit, _, _, _ = _validate_overlay(corpus, overlay)
    output: list[dict[str, object]] = []

    for case_id in order:
        selected = list(explicit[case_id])
        for rank in range(top_k):
            remaining = [
                source_id
                for source_id in sources
                if source_id not in selected
            ]
            if not remaining:
                break
            choices = {
                "__NONE__": "No remaining source is relevant enough to add."
            }
            for source_id in remaining:
                source = sources[source_id]
                choices[source_id] = (
                    f"path={source['path']}\ncontent={source['content']}"
                )

            decision = broker.choose(
                decision_type=f"context_relevance:{case_id}:{rank}",
                state={
                    "query": cases[case_id]["query"],
                    "explicit_source_ids": list(explicit[case_id]),
                    "already_selected": list(selected),
                },
                question=(
                    "Which remaining source is most relevant to the query? "
                    "Choose __NONE__ for hard negatives or when no source adds "
                    "useful evidence. Do not infer authority from relevance."
                ),
                choices=choices,
                deterministic_choice="__NONE__",
            )
            if decision.selected == "__NONE__":
                break
            selected.append(decision.selected)

        output.append(_prediction(case_id, selected))
    return output
