import json
from pathlib import Path
import unittest

from runtime.context_retrieval_jev import jev_context_rankings
from runtime.decision import ChoiceDecision, DecisionBroker, DecisionConfig


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "work" / "evals" / "context-builder-evidence-integrity-v1.json"
OVERLAY_PATH = ROOT / "work" / "evals" / "context-builder-retrieval-stage2-v1.json"


class FirstSourceProvider:
    provider_name = "fake"

    def choose(self, *, state, question, choices):
        pick = next(key for key in choices if key != "__NONE__")
        return ChoiceDecision(
            choice=pick,
            confidence=0.99,
            probabilities={key: (0.99 if key == pick else 0.0) for key in choices},
            provider="fake",
            model="fake-v1",
        )


def make_broker(*, allow_content):
    return DecisionBroker(
        DecisionConfig(
            provider="jev",
            mode="active",
            model="test",
            min_confidence=0.8,
            allow_content=allow_content,
        ),
        provider=FirstSourceProvider(),
    )


class JevContextRetrievalCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))

    def test_content_opt_in_is_required(self):
        with self.assertRaises(ValueError):
            jev_context_rankings(
                self.corpus,
                self.overlay,
                broker=make_broker(allow_content=False),
                top_k=1,
            )

    def test_candidate_preserves_explicit_prefix_and_adds_at_most_top_k(self):
        predictions = jev_context_rankings(
            self.corpus,
            self.overlay,
            broker=make_broker(allow_content=True),
            top_k=1,
        )
        explicit = {
            item["case_id"]: item["explicit_source_ids"]
            for item in self.overlay["cases"]
        }
        self.assertEqual(len(predictions), len(self.corpus["cases"]))
        for item in predictions:
            prefix = explicit[item["case_id"]]
            self.assertEqual(item["source_ids"][:len(prefix)], prefix)
            self.assertLessEqual(len(item["source_ids"]), len(prefix) + 1)


if __name__ == "__main__":
    unittest.main()
