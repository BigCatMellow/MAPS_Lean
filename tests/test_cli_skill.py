"""CLI tests for `maps skill …` — SEC4 / 6.10 operator-driven lifecycle transitions.

Slices A1 (`list`/`show`) + A2 (`approve`/`activate`/`retire`/`supersede`).
Every command is thin over `runtime.state.skill_lifecycle_storage`; these
tests round-trip each verb against a real temp-file `TaskStore` seeded via
`record_skill_lifecycle_subject`, and pin the exact `MutationResult` code
strings the resolver and the store return (not just the process exit code).
"""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import unittest

from runtime.cli import _resolve_skill_catalog_key, main
from runtime.skills import assess_skill

from tests.test_skill_lifecycle_storage import (
    QUARANTINE_BODY,
    SAFE_BODY,
    SkillFixtureMixin,
)


class _SkillCliMixin(SkillFixtureMixin):
    def run_maps(self, *args: str) -> tuple[int, object]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(['--db', str(self.db_dir / 'maps.db'), *args])
        text = buffer.getvalue()
        payload = json.loads(text) if text.strip() else None
        return code, payload

    def run_cli(self, *args: str) -> tuple[int, object]:
        return self.run_maps('skill', *args)

    def seed(self, name: str, *, body: str = SAFE_BODY, **kwargs):
        entry, _report, result = self.register(name, body=body, **kwargs)
        self.assertTrue(result.ok, result)
        return entry


class SkillCliListShowTests(_SkillCliMixin, unittest.TestCase):
    def test_list_is_empty_before_any_subject(self):
        code, payload = self.run_cli('list')
        self.assertEqual(code, 0)
        self.assertEqual(payload, [])

    def test_list_reports_composed_state_and_filters(self):
        self.seed('alpha-skill')
        code, payload = self.run_cli('list')
        self.assertEqual(code, 0)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['state'], 'VALIDATED')

        code, filtered = self.run_cli('list', '--state', 'QUARANTINED')
        self.assertEqual(code, 0)
        self.assertEqual(filtered, [])

        code, matched = self.run_cli('list', '--state', 'VALIDATED')
        self.assertEqual(code, 0)
        self.assertEqual(len(matched), 1)

    def test_list_rejects_an_unknown_state_string(self):
        code, payload = self.run_cli('list', '--state', 'NOT_A_STATE')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'INVALID_LIFECYCLE_STATE')

    def test_show_returns_subject_and_decision_history(self):
        self.seed('beta-skill')
        code, payload = self.run_cli('show', 'bundled:beta-skill')
        self.assertEqual(code, 0)
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['subject']['state'], 'VALIDATED')
        self.assertEqual(payload['decisions'], [])

    def test_show_unknown_subject_is_a_typed_failure(self):
        code, payload = self.run_cli('show', 'bundled:missing-skill')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'SKILL_SUBJECT_NOT_FOUND')

    def test_list_and_show_never_write_a_decision(self):
        self.seed('gamma-skill')
        self.run_cli('list')
        self.run_cli('show', 'bundled:gamma-skill')
        subjects = self.store.list_skill_lifecycle_subjects()
        self.assertEqual(len(subjects), 1)
        self.assertEqual(
            self.store.list_skill_lifecycle_decisions(subjects[0]['catalog_key']),
            [],
        )


class SkillCliTransitionTests(_SkillCliMixin, unittest.TestCase):
    def test_full_operator_chain_composes_after_every_verb(self):
        self.seed('delta-skill')
        ref = 'bundled:delta-skill'

        code, payload = self.run_cli(
            'approve', ref, '--actor', 'operator-1', '--decision-ref', 'commit:aaa'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['code'], 'SKILL_TRANSITION_RECORDED')
        self.assertEqual(payload['task']['to_state'], 'APPROVED')

        code, _ = self.run_cli('activate', ref, '--decision-ref', 'commit:bbb')
        self.assertEqual(code, 0)

        code, payload = self.run_cli('show', ref)
        self.assertEqual(payload['subject']['state'], 'ACTIVE')
        self.assertEqual(len(payload['decisions']), 2)

        code, payload = self.run_cli('retire', ref, '--decision-ref', 'commit:ccc')
        self.assertEqual(code, 0)
        code, payload = self.run_cli('show', ref)
        self.assertEqual(payload['subject']['state'], 'RETIRED')

    def test_quarantined_skill_can_be_approved_or_retired_by_the_cli(self):
        self.seed('quar-skill', body=QUARANTINE_BODY)
        code, payload = self.run_cli('show', 'bundled:quar-skill')
        self.assertEqual(payload['subject']['state'], 'QUARANTINED')

        code, payload = self.run_cli(
            'retire', 'bundled:quar-skill', '--decision-ref', 'commit:rej'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'RETIRED')

    def test_approve_without_actor_is_rejected_by_argparse(self):
        self.seed('eps-skill')
        with self.assertRaises(SystemExit) as raised:
            self.run_cli('approve', 'bundled:eps-skill', '--decision-ref', 'x')
        self.assertEqual(raised.exception.code, 2)

    def test_illegal_edge_exits_non_zero_and_writes_nothing(self):
        self.seed('zeta-skill')  # starts VALIDATED
        # VALIDATED -> ACTIVE is not a legal edge.
        code, payload = self.run_cli(
            'activate', 'bundled:zeta-skill', '--decision-ref', 'commit:bad'
        )
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'ILLEGAL_SKILL_TRANSITION')
        subjects = self.store.list_skill_lifecycle_subjects()
        self.assertEqual(
            self.store.list_skill_lifecycle_decisions(subjects[0]['catalog_key']),
            [],
        )

    def test_supersede_decision_ref_can_name_the_successor(self):
        self.seed('eta-skill')
        ref = 'bundled:eta-skill'
        self.run_cli('approve', ref, '--actor', 'op', '--decision-ref', 'c:1')
        self.run_cli('activate', ref, '--decision-ref', 'c:2')
        successor = 'bundled:eta-skill@sha256:' + 'f' * 64
        code, payload = self.run_cli('supersede', ref, '--decision-ref', successor)
        self.assertEqual(code, 0, payload)
        code, shown = self.run_cli('show', ref)
        self.assertEqual(shown['subject']['state'], 'SUPERSEDED')
        self.assertEqual(shown['decisions'][-1]['decision_ref'], successor)

    def test_transition_on_unknown_subject_is_typed(self):
        code, payload = self.run_cli(
            'approve', 'bundled:nope', '--actor', 'op', '--decision-ref', 'r'
        )
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'SKILL_SUBJECT_NOT_FOUND')


class SkillCatalogKeyResolverTests(_SkillCliMixin, unittest.TestCase):
    def test_full_catalog_key_passes_through_untouched(self):
        key = 'bundled:thing@sha256:' + 'a' * 64
        self.assertEqual(_resolve_skill_catalog_key(self.store, key), key)

    def test_bare_string_without_a_pair_is_invalid_reference(self):
        result = _resolve_skill_catalog_key(self.store, 'not-a-reference')
        self.assertEqual(result.code, 'INVALID_SKILL_REFERENCE')

    def test_empty_reference_is_invalid(self):
        self.assertEqual(
            _resolve_skill_catalog_key(self.store, '   ').code,
            'INVALID_SKILL_REFERENCE',
        )

    def test_unique_pair_resolves_to_its_catalog_key(self):
        entry = self.seed('theta-skill')
        self.assertEqual(
            _resolve_skill_catalog_key(self.store, 'bundled:theta-skill'),
            entry.catalog_key,
        )

    def test_multiple_revisions_are_refused_with_multiple_revisions(self):
        self.seed('iota-skill', body=SAFE_BODY)
        # A content edit yields a distinct content_sha256 -> a second subject
        # under the same source_id:skill_id.
        self.write_skill('iota-skill', body=SAFE_BODY + "4. Extra verified step.\n")
        entry2 = self.entry_for('iota-skill')
        self.store.record_skill_lifecycle_subject(entry2, assess_skill(entry2.descriptor))

        result = _resolve_skill_catalog_key(self.store, 'bundled:iota-skill')
        self.assertEqual(result.code, 'MULTIPLE_REVISIONS')

        # Disambiguating by sha prefix resolves.
        sha = entry2.descriptor.content_sha256
        resolved = _resolve_skill_catalog_key(
            self.store, f'bundled:iota-skill@{sha[:16]}'
        )
        self.assertEqual(resolved, entry2.catalog_key)

    def test_ambiguous_sha_prefix_code_is_distinct_from_multiple_revisions(self):
        class _FakeStore:
            @staticmethod
            def list_skill_lifecycle_subjects():
                return [
                    {
                        'source_id': 'bundled',
                        'skill_id': 'twin',
                        'content_sha256': 'ab' + '0' * 62,
                        'catalog_key': 'bundled:twin@sha256:ab' + '0' * 62,
                    },
                    {
                        'source_id': 'bundled',
                        'skill_id': 'twin',
                        'content_sha256': 'ab' + '1' * 62,
                        'catalog_key': 'bundled:twin@sha256:ab' + '1' * 62,
                    },
                ]

        result = _resolve_skill_catalog_key(_FakeStore(), 'bundled:twin@ab')
        self.assertEqual(result.code, 'AMBIGUOUS_SHA_PREFIX')

    def test_pair_with_no_recorded_subject_is_not_found(self):
        result = _resolve_skill_catalog_key(self.store, 'bundled:ghost')
        self.assertEqual(result.code, 'SKILL_SUBJECT_NOT_FOUND')


class OperatorRegistryCliTests(_SkillCliMixin, unittest.TestCase):
    """SEC4 Half 3 — `maps init --operator`, `maps operator …`, and the opt-in
    identity check on `maps skill approve`."""

    def test_init_seeds_genesis_and_lists(self):
        code, payload = self.run_maps(
            'init', '--operator', 'alice', '--operator-decision-ref', 'd:1'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['genesis_operator']['code'], 'OPERATOR_AUTHORIZED')

        code, payload = self.run_maps('operator', 'list')
        self.assertEqual(code, 0)
        self.assertEqual(
            [o['operator_id'] for o in payload['operators']], ['alice']
        )
        self.assertTrue(payload['operators'][0]['authorized'])

    def test_init_operator_without_decision_ref_is_typed(self):
        code, payload = self.run_maps('init', '--operator', 'alice')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'INVALID_DECISION_REF')

    def test_plain_init_is_unchanged(self):
        code, payload = self.run_maps('init')
        self.assertEqual(code, 0)
        self.assertNotIn('genesis_operator', payload)
        self.assertIn('settings', payload)

    def test_operator_add_and_revoke_roundtrip(self):
        self.run_maps('init', '--operator', 'alice', '--operator-decision-ref', 'd:1')
        code, payload = self.run_maps(
            'operator', 'add', 'bob', '--by', 'alice', '--decision-ref', 'd:2'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['code'], 'OPERATOR_AUTHORIZED')

        code, payload = self.run_maps(
            'operator', 'add', 'carol', '--by', 'eve', '--decision-ref', 'd:3'
        )
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'UNAUTHORIZED_AUTHORIZER')

        code, payload = self.run_maps(
            'operator', 'revoke', 'bob', '--by', 'alice', '--decision-ref', 'd:4'
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload['code'], 'OPERATOR_REVOKED')

    def test_skill_approve_inert_while_registry_empty(self):
        self.seed('reg-skill')
        code, payload = self.run_cli(
            'approve', 'bundled:reg-skill',
            '--actor', 'nobody-in-particular', '--decision-ref', 'd:x',
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['code'], 'SKILL_TRANSITION_RECORDED')

    def test_skill_approve_blocked_for_unknown_actor_once_seeded(self):
        self.seed('reg-skill')
        self.run_maps('init', '--operator', 'alice', '--operator-decision-ref', 'd:1')

        code, payload = self.run_cli(
            'approve', 'bundled:reg-skill',
            '--actor', 'mallory', '--decision-ref', 'd:x',
        )
        self.assertEqual(code, 2, payload)
        self.assertEqual(payload['code'], 'UNAUTHORIZED_ACTOR')
        _, show = self.run_cli('show', 'bundled:reg-skill')
        self.assertEqual(show['decisions'], [])

    def test_skill_approve_allowed_for_authorized_actor(self):
        self.seed('reg-skill')
        self.run_maps('init', '--operator', 'alice', '--operator-decision-ref', 'd:1')

        code, payload = self.run_cli(
            'approve', 'bundled:reg-skill',
            '--actor', 'alice', '--decision-ref', 'd:ok',
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'APPROVED')

    # SEC4 Half 3 slice 2 (2a): the opt-in gate now covers every `maps skill`
    # lifecycle-transition verb, not just `approve`.

    def _seed_and_init(self):
        self.seed('reg-skill')
        self.run_maps('init', '--operator', 'alice', '--operator-decision-ref', 'd:1')

    def test_seeded_registry_gates_activate(self):
        self._seed_and_init()
        # activate with no --actor while the registry is seeded -> blocked,
        # nothing recorded (the empty-string actor is not authorized).
        code, payload = self.run_cli(
            'activate', 'bundled:reg-skill', '--decision-ref', 'd:b'
        )
        self.assertEqual(code, 2, payload)
        self.assertEqual(payload['code'], 'UNAUTHORIZED_ACTOR')
        _, show = self.run_cli('show', 'bundled:reg-skill')
        self.assertEqual(show['decisions'], [])
        # an unauthorized --actor is also blocked
        code, payload = self.run_cli(
            'activate', 'bundled:reg-skill', '--actor', 'mallory', '--decision-ref', 'd:b'
        )
        self.assertEqual((code, payload['code']), (2, 'UNAUTHORIZED_ACTOR'))
        # an authorized --actor: gate passes, transition proceeds as before
        self.assertEqual(
            self.run_cli('approve', 'bundled:reg-skill',
                         '--actor', 'alice', '--decision-ref', 'd:a')[0], 0)
        code, payload = self.run_cli(
            'activate', 'bundled:reg-skill', '--actor', 'alice', '--decision-ref', 'd:b'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'ACTIVE')

    def test_seeded_registry_gates_retire_and_supersede(self):
        self._seed_and_init()
        for verb in ('retire', 'supersede'):
            code, payload = self.run_cli(
                verb, 'bundled:reg-skill', '--actor', 'mallory', '--decision-ref', 'd:x'
            )
            self.assertEqual((code, payload['code']), (2, 'UNAUTHORIZED_ACTOR'), verb)
            code, payload = self.run_cli(
                verb, 'bundled:reg-skill', '--decision-ref', 'd:x'
            )
            self.assertEqual((code, payload['code']), (2, 'UNAUTHORIZED_ACTOR'), verb)
        _, show = self.run_cli('show', 'bundled:reg-skill')
        self.assertEqual(show['decisions'], [])

    def test_seeded_registry_authorized_actor_can_retire(self):
        self._seed_and_init()
        for verb, ref in (('approve', 'd:a'), ('activate', 'd:v')):
            self.assertEqual(
                self.run_cli(verb, 'bundled:reg-skill',
                             '--actor', 'alice', '--decision-ref', ref)[0], 0, verb)
        code, payload = self.run_cli(
            'retire', 'bundled:reg-skill', '--actor', 'alice', '--decision-ref', 'd:r'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'RETIRED')

    def test_empty_registry_gates_no_skill_verb(self):
        self.seed('reg-skill')  # no `init --operator` -> registry empty
        self.assertEqual(
            self.run_cli('approve', 'bundled:reg-skill',
                         '--actor', 'whoever', '--decision-ref', 'd:a')[0], 0)
        # activate / retire with NO --actor still work while the registry is empty
        code, payload = self.run_cli(
            'activate', 'bundled:reg-skill', '--decision-ref', 'd:b'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'ACTIVE')
        code, payload = self.run_cli(
            'retire', 'bundled:reg-skill', '--decision-ref', 'd:c'
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['task']['to_state'], 'RETIRED')


if __name__ == '__main__':
    unittest.main()
