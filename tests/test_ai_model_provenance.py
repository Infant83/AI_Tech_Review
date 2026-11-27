from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from scripts import ai_model_provenance as provenance
from scripts import capture_ai_model_provenance as capture


ROOT_ID = "00000000-0000-4000-8000-000000000001"
CHILD_ID = "00000000-0000-4000-8000-000000000002"
OTHER_ID = "00000000-0000-4000-8000-000000000003"


def context(stamp, model="gpt-6.1-sol", effort="ultra"):
    payload = {"model": model, "instructions": "private instructions must not be retained"}
    if effort is not None:
        payload["effort"] = effort
    return {"timestamp": stamp, "type": "turn_context", "payload": payload}


def public_record(rows=None):
    return {"version": 1, "system": "OpenAI Codex", "scope": "recorded_editorial_work", "checked_on": "2026-11-27",
            "roles": rows or [{"role": "authoring", "model_id": "gpt-6.1-sol", "reasoning_effort": "ultra", "evidence_kind": "turn_context"}]}


class ModelProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "codex"
        self.home.mkdir()
        self.database = self.home / "state_5.sqlite"
        with sqlite3.connect(self.database) as connection:
            connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, model TEXT, reasoning_effort TEXT)")
        self.config = self.home / "config.toml"
        self.config.write_text('model = "gpt-6.2-astra"\nmodel_reasoning_effort = "high"\napi_key = "not-public"\n')

    def add_thread(self, identity=ROOT_ID, records=(), model="gpt-6.2-astra", effort="high", session_identity=None):
        source = self.home / "sessions/2020/01/01" / ("rollout-" + identity + ".jsonl")
        source.parent.mkdir(parents=True, exist_ok=True)
        meta = {"timestamp": "2020-01-01T00:00:00.000Z", "type": "session_meta",
                "payload": {"id": session_identity or identity, "session_id": session_identity or identity,
                            "creator_account_id": "private-account", "base_instructions": "private instructions"}}
        source.write_text("\n".join(json.dumps(x) for x in [meta, *records]) + "\n")
        with sqlite3.connect(self.database) as connection:
            connection.execute("INSERT INTO threads VALUES (?,?,?,?)", (identity, str(source), model, effort))
        return source

    def collect(self, participants=None, **kwargs):
        return provenance.collect_participants(participants or [("authoring", ROOT_ID)], codex_home=self.home, **kwargs)

    def test_explicit_interval_and_worker_roles_keep_all_model_effort_pairs(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z", "gpt-6-sol", "medium"),
                                 context("2020-01-01T02:00:00Z"), context("2020-01-01T03:00:00Z", "gpt-6.1-sol", "high"),
                                 context("2020-01-01T04:00:00Z", "gpt-6.2-astra", "max")])
        self.add_thread(CHILD_ID, records=[context("2020-01-01T02:30:00Z", "gpt-6.1-terra", "high")])
        result, evidence = self.collect([("authoring", ROOT_ID), ("independent-review", CHILD_ID)],
                                        since="2020-01-01T02:00:00Z", until="2020-01-01T03:00:00Z")
        actual = {(x["role"], x["model_id"], x["reasoning_effort"]) for x in result["roles"]}
        self.assertEqual(actual, {("authoring", "gpt-6.1-sol", "ultra"), ("authoring", "gpt-6.1-sol", "high"),
                                  ("independent-review", "gpt-6.1-terra", "high")})
        self.assertEqual(len(evidence["participants"][0]["records"]), 2)
        self.assertTrue(all(x["session_identity_verified"] for x in evidence["participants"]))

    def test_latest_selection_does_not_mix_unrelated_earlier_settings(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z", "gpt-6-sol", "medium"), context("2020-01-01T02:00:00Z")])
        result, evidence = self.collect()
        self.assertEqual([(x["model_id"], x["reasoning_effort"]) for x in result["roles"]], [("gpt-6.1-sol", "ultra")])
        self.assertEqual(evidence["participants"][0]["contexts_seen_in_selected_range"], 2)
        self.assertEqual(len(evidence["participants"][0]["records"]), 1)

    def test_until_only_uses_latest_preceding_record(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z", "gpt-6-sol", "medium"), context("2020-01-01T02:00:00Z")])
        result, _ = self.collect(until="2020-01-01T01:30:00Z")
        self.assertEqual(result["roles"][0]["model_id"], "gpt-6-sol")
        self.assertEqual(result["roles"][0]["evidence_kind"], "turn_context")

    def test_missing_effort_is_not_filled_from_thread_or_config(self):
        self.add_thread(records=[context("2020-01-01T02:00:00Z", effort=None)], effort="ultra")
        result, _ = self.collect()
        row = result["roles"][0]
        self.assertIsNone(row["reasoning_effort"])
        self.assertEqual(row["evidence_kind"], "turn_context")
        self.assertIn("추론 강도 미기록", provenance.render_disclosure(result, "ko"))
        self.assertNotIn("ultra", provenance.render_disclosure(result, "en"))

    def test_missing_model_context_is_preserved_without_default_substitution(self):
        self.add_thread(records=[context("2020-01-01T02:00:00Z", model=None, effort="high")])
        result, _ = self.collect()
        self.assertIsNone(result["roles"][0]["model_id"])
        self.assertEqual(result["roles"][0]["reasoning_effort"], "high")
        self.assertEqual(result["roles"][0]["evidence_kind"], "turn_context")

    def test_config_only_current_snapshot_is_not_historical_usage(self):
        self.add_thread(model=None, effort=None)
        current, evidence = self.collect()
        self.assertEqual(current["roles"][0], {"role": "authoring", "model_id": "gpt-6.2-astra", "reasoning_effort": "high", "evidence_kind": "settings_snapshot"})
        self.assertEqual(evidence["participants"][0]["settings_snapshot"]["source"], "user_config_defaults")
        self.assertIn("not writing-time usage evidence", provenance.render_disclosure(current, "en"))
        historical, _ = self.collect(since="2020-01-01T01:00:00Z", until="2020-01-01T02:00:00Z")
        self.assertEqual(historical["roles"][0], {"role": "authoring", "model_id": None, "reasoning_effort": None, "evidence_kind": "unconfirmed"})

    def test_current_thread_snapshot_missing_effort_does_not_borrow_config(self):
        self.add_thread(model="gpt-6.1-sol", effort=None)
        result, evidence = self.collect()
        self.assertIsNone(result["roles"][0]["reasoning_effort"])
        self.assertEqual(evidence["participants"][0]["settings_snapshot"]["source"], "current_thread_settings")

    def test_parent_session_id_is_not_used_as_child_identity(self):
        identity = provenance.default_participant(environ={"CODEX_THREAD_ID": CHILD_ID, "CODEX_SESSION_ID": ROOT_ID})
        self.assertEqual(identity, ("authoring", CHILD_ID))
        with self.assertRaisesRegex(provenance.ProvenanceError, "provide --participant"):
            provenance.default_participant(environ={"CODEX_SESSION_ID": ROOT_ID})

    def test_corrupt_or_mismatched_identity_has_no_settings_fallback(self):
        self.add_thread(session_identity=OTHER_ID)
        with self.assertRaisesRegex(provenance.ProvenanceError, "identities do not match"):
            self.collect()
        with self.assertRaises(provenance.ProvenanceError):
            self.collect([("authoring", "../../private")])
        with self.assertRaisesRegex(provenance.ProvenanceError, "No exact"):
            self.collect([("authoring", CHILD_ID)])

    def test_conflicting_effort_and_malformed_metadata_do_not_fallback(self):
        row = context("2020-01-01T01:00:00Z")
        row["payload"]["reasoning_effort"] = "low"
        source = self.add_thread(records=[row])
        with self.assertRaisesRegex(provenance.ProvenanceError, "Conflicting"):
            self.collect()
        source.write_text(source.read_text().splitlines()[0] + '\n{"timestamp":"2020-01-01T02:00:00Z","type":"turn_context","payload":{"model":"gpt-6.1-sol",INVALID}}\n')
        with self.assertRaises(provenance.ProvenanceError):
            self.collect()

    def test_duplicate_metadata_model_fields_are_rejected(self):
        source = self.add_thread()
        with source.open("a") as handle:
            handle.write('{"timestamp":"2020-01-01T02:00:00Z","type":"turn_context","payload":{"model":"gpt-6.1-sol","model":"gpt-6-sol","effort":"ultra"}}\n')
        with self.assertRaises(provenance.ProvenanceError):
            self.collect()

    def test_current_codex_ordinal_header_and_legacy_header_are_both_supported(self):
        source = self.add_thread(records=[context("2020-01-01T01:00:00Z"), context("2020-01-01T02:00:00Z", "gpt-6-sol", "high")])
        records = [json.loads(line) for line in source.read_text().splitlines()]
        with source.open("w") as handle:
            for ordinal, record in enumerate(records):
                # Actual current Codex storage inserts ordinal before type.
                value = {"timestamp": record["timestamp"], "ordinal": ordinal, "type": record["type"], "payload": record["payload"]}
                handle.write(json.dumps(value, separators=(",", ":")) + "\n")
        result, evidence = self.collect(since="2020-01-01T00:30:00Z", until="2020-01-01T02:30:00Z")
        self.assertEqual({x["model_id"] for x in result["roles"]}, {"gpt-6.1-sol", "gpt-6-sol"})
        self.assertEqual(len(evidence["participants"][0]["records"]), 2)

    def test_child_thread_id_is_distinct_from_root_conversation_session_id(self):
        source = self.add_thread(CHILD_ID, records=[context("2020-01-01T01:00:00Z")])
        records = [json.loads(line) for line in source.read_text().splitlines()]
        records[0]["payload"].update(session_id=ROOT_ID, parent_thread_id=ROOT_ID, forked_from_id=ROOT_ID)
        source.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        result, evidence = self.collect([("source-review", CHILD_ID)])
        self.assertEqual(result["roles"][0]["model_id"], "gpt-6.1-sol")
        self.assertEqual(evidence["participants"][0]["session_identity_source_field"], "payload.id")
        # A matching root session_id must not rescue a mismatched thread id.
        records[0]["payload"].update(id=OTHER_ID, session_id=CHILD_ID)
        source.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        with self.assertRaisesRegex(provenance.ProvenanceError, "identities do not match"):
            self.collect([("source-review", CHILD_ID)])

    def test_legacy_session_only_identity_is_verified_without_guessing(self):
        source = self.add_thread(records=[context("2020-01-01T01:00:00Z")])
        records = [json.loads(line) for line in source.read_text().splitlines()]
        del records[0]["payload"]["id"]
        source.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        _, evidence = self.collect()
        self.assertEqual(evidence["participants"][0]["session_identity_source_field"], "payload.session_id")

    def test_private_transcript_account_and_paths_never_enter_public_record(self):
        source = self.add_thread(records=[context("2020-01-01T02:00:00Z"),
                                         {"timestamp": "2020-01-01T02:01:00Z", "type": "response_item", "payload": {"content": "private-message token=secret someone@example.org"}}])
        result, evidence = self.collect()
        serialized = json.dumps(result)
        for forbidden in [ROOT_ID, str(source), str(self.home), "private instructions", "private-account", "private-message", "token=secret", "someone@example.org"]:
            self.assertNotIn(forbidden, serialized)
            self.assertNotIn(forbidden, provenance.render_disclosure(result, "ko"))
        private_serialized = json.dumps(evidence)
        self.assertNotIn("private-message", private_serialized)
        self.assertNotIn("private instructions", private_serialized)
        self.assertNotIn("private-account", private_serialized)
        self.assertIn(ROOT_ID, private_serialized)

    def test_public_schema_rejects_unknown_fields_identifiers_and_markup(self):
        mutations = [lambda x: x.update(thread_id=ROOT_ID), lambda x: x.update(version=True),
                     lambda x: x.update(scope=str(self.root)), lambda x: x.update(checked_on="2026-11-7"),
                     lambda x: x["roles"][0].update(local_path="/Users/private"),
                     lambda x: x["roles"][0].update(role=ROOT_ID), lambda x: x["roles"][0].update(role="<script>"),
                     lambda x: x["roles"][0].update(model_id="/Users/private/model"),
                     lambda x: x["roles"][0].update(model_id="gpt-" + ROOT_ID),
                     lambda x: x["roles"][0].update(reasoning_effort="secret@example.org"),
                     lambda x: x["roles"][0].update(evidence_kind="current-config-used-in-the-past")]
        for change in mutations:
            with self.subTest(change=change):
                value = public_record(); change(value)
                with self.assertRaises(provenance.ProvenanceError):
                    provenance.validate_public_provenance(value)

    def test_render_groups_shared_settings_but_preserves_mixed_models_and_evidence(self):
        rows = [{"role": x, "model_id": "gpt-6.1-sol", "reasoning_effort": "ultra", "evidence_kind": "turn_context"}
                for x in ["authoring", "source-review", "pdf-production", "independent-review"]]
        record = public_record(rows)
        for language in ["ko", "en"]:
            text = provenance.render_disclosure(record, language)
            self.assertEqual(text.count("`gpt-6.1-sol`"), 1)
            self.assertEqual(text.count("`ultra`"), 1)
        rows.append({"role": "source-review", "model_id": "gpt-6.1-terra", "reasoning_effort": "high", "evidence_kind": "turn_context"})
        rows.append({"role": "editing", "model_id": "gpt-6.1-sol", "reasoning_effort": "ultra", "evidence_kind": "settings_snapshot"})
        text = provenance.render_disclosure(public_record(rows), "en")
        self.assertIn("`gpt-6.1-terra`", text)
        self.assertIn("reasoning effort `high`", text)
        self.assertIn("not writing-time usage evidence", text)
        self.assertEqual(text.count("`gpt-6.1-sol`"), 2)

    def test_saved_record_remains_fixed_after_current_config_changes(self):
        source = self.add_thread(records=[context("2020-01-01T02:00:00Z")])
        saved, _ = self.collect()
        before = provenance.render_disclosure(saved, "ko")
        self.config.write_text('model="gpt-6.2-astra"\nmodel_reasoning_effort="max"\n')
        source.unlink()
        with mock.patch.object(sqlite3, "connect", side_effect=AssertionError("build must not read metadata stores")):
            self.assertEqual(provenance.render_disclosure(saved, "ko"), before)
            self.assertEqual(provenance.validate_public_provenance(saved), saved)

    def test_bounded_tail_does_not_search_entire_transcript_for_old_context(self):
        source = self.add_thread(records=[context("2020-01-01T01:00:00Z"),
                                         {"timestamp": "2020-01-01T02:00:00Z", "type": "response_item", "payload": {"content": "x" * 4000}}])
        with mock.patch.object(provenance, "TAIL_BYTES", 256):
            result, evidence = self.collect()
        self.assertEqual(result["roles"][0]["evidence_kind"], "settings_snapshot")
        self.assertLessEqual(evidence["participants"][0]["range_bytes_traversed"], 256)
        self.assertNotIn("x" * 100, json.dumps(evidence))
        self.assertGreater(source.stat().st_size, 4000)

    def test_explicit_window_and_metadata_read_budget_are_enforced(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z"), context("2020-01-01T02:00:00Z")])
        with mock.patch.object(provenance, "MAX_WINDOW_BYTES", 100):
            with self.assertRaisesRegex(provenance.ProvenanceError, "bounded reader"):
                self.collect(since="2020-01-01T00:00:01Z", until="2020-01-01T03:00:00Z")
        with mock.patch.object(provenance, "MAX_BYTES_READ", 100):
            with self.assertRaisesRegex(provenance.ProvenanceError, "read budget"):
                self.collect()

    def test_rollout_locator_escape_or_symlink_is_rejected(self):
        source = self.add_thread(records=[context("2020-01-01T01:00:00Z")])
        other = self.root / "outside.jsonl"; other.write_bytes(source.read_bytes())
        with sqlite3.connect(self.database) as connection:
            connection.execute("UPDATE threads SET rollout_path=? WHERE id=?", (str(other), ROOT_ID))
        with self.assertRaisesRegex(provenance.ProvenanceError, "outside"):
            self.collect()
        link = source.parent / "link.jsonl"; link.symlink_to(source)
        with sqlite3.connect(self.database) as connection:
            connection.execute("UPDATE threads SET rollout_path=? WHERE id=?", (str(link), ROOT_ID))
        with self.assertRaisesRegex(provenance.ProvenanceError, "Symlinked"):
            self.collect()

    def test_source_database_config_and_rollout_are_not_modified(self):
        source = self.add_thread(records=[context("2020-01-01T01:00:00Z")])
        paths = [self.database, self.config, source]
        before = [(p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]
        self.collect()
        self.assertEqual(before, [(p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])

    def test_cli_uses_thread_id_and_separates_private_evidence(self):
        self.add_thread(ROOT_ID, records=[context("2020-01-01T01:00:00Z", "gpt-6-sol", "medium")])
        self.add_thread(CHILD_ID, records=[context("2020-01-01T01:00:00Z")])
        repo = self.root / "repo"; (repo / ".git").mkdir(parents=True)
        public = repo / "publication/model.json"; private = self.root / "private/evidence.json"
        args = ["--codex-home", str(self.home), "--output", str(public), "--private-evidence", str(private)]
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {"CODEX_THREAD_ID": CHILD_ID, "CODEX_SESSION_ID": ROOT_ID}), redirect_stdout(output), redirect_stderr(errors):
            self.assertEqual(capture.main(args), 0)
        self.assertEqual(json.loads(public.read_text())["roles"][0]["model_id"], "gpt-6.1-sol")
        self.assertIn(CHILD_ID, private.read_text())
        self.assertNotIn(CHILD_ID, public.read_text())
        self.assertNotIn(str(self.root), output.getvalue() + errors.getvalue())
        self.assertEqual(private.stat().st_mode & 0o777, 0o600)

    def test_cli_private_target_inside_any_git_checkout_is_refused(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z")])
        other_repo = self.root / "other-repo"; (other_repo / ".git").mkdir(parents=True)
        out = self.root / "public.json"; private = other_repo / "ignored-private/evidence.json"
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = capture.main(["--participant", "authoring=" + ROOT_ID, "--codex-home", str(self.home), "--output", str(out), "--private-evidence", str(private)])
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())
        self.assertFalse(private.exists())
        self.assertIn("outside Git", errors.getvalue())

    def test_time_bounds_and_duplicate_participants_are_not_silently_repaired(self):
        self.add_thread(records=[context("2020-01-01T01:00:00Z")])
        for kwargs in [{"since": "2020-01-01T00:00:00"}, {"since": "2020-01-02T00:00:00Z", "until": "2020-01-01T00:00:00Z"},
                       {"since": "9999-01-01T00:00:00Z"}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(provenance.ProvenanceError):
                self.collect(**kwargs)
        with self.assertRaisesRegex(provenance.ProvenanceError, "Duplicate participant"):
            self.collect([("authoring", ROOT_ID), ("authoring", ROOT_ID)])

    def test_malformed_config_defaults_and_unconfirmed_rows_fail_closed(self):
        self.add_thread(model=None, effort=None)
        self.config.write_text('instructions="""\nmodel="gpt-6.1-sol"\n"""\n')
        with self.assertRaises(provenance.ProvenanceError):
            self.collect()
        record = public_record(); record["roles"][0]["evidence_kind"] = "unconfirmed"
        with self.assertRaises(provenance.ProvenanceError):
            provenance.validate_public_provenance(record)


if __name__ == "__main__":
    unittest.main()
