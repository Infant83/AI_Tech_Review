from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scripts.build_briefing_editorial import AI_MODEL_TOKEN, model_disclosure_inputs


class BriefingModelProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.root = self.parent / "repo"
        self.root.mkdir()
        self.record = {
            "version": 1, "system": "OpenAI Codex",
            "scope": "recorded_editorial_work", "checked_on": "2026-11-27",
            "roles": [{"role": "authoring", "model_id": "gpt-6.1-sol",
                       "reasoning_effort": "ultra", "evidence_kind": "turn_context"}],
        }
        self.source = self.root / "model.json"
        self.source.write_text(json.dumps(self.record))
        self.manuscripts = ["본문\n\n" + AI_MODEL_TOKEN, "Body\n\n" + AI_MODEL_TOKEN]

    def test_legacy_manuscripts_do_not_require_or_read_host_model_settings(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.parent / "absent"),
                                    "CODEX_THREAD_ID": "not-a-session"}):
            self.assertIsNone(model_disclosure_inputs(self.root, ["본문", "Body"], None))

    def test_frozen_record_is_stable_when_the_host_settings_change(self):
        from scripts.ai_model_provenance import render_disclosure
        configuration = self.parent / "config.toml"
        outputs = []
        for model in ("gpt-6.1-sol", "different-host-default"):
            configuration.write_text('model = "' + model + '"\n')
            with patch.dict(os.environ, {"CODEX_HOME": str(self.parent), "CODEX_MODEL": model}):
                record = model_disclosure_inputs(self.root, self.manuscripts, self.source)
                outputs.append(tuple(render_disclosure(record, lang) for lang in ("ko", "en")))
        self.assertEqual(outputs[0], outputs[1])
        for text in outputs[0]:
            self.assertIn("gpt-6.1-sol", text)
            self.assertIn("ultra", text)
            self.assertNotIn("different-host-default", text)

    def test_both_languages_must_explicitly_consume_one_record(self):
        for manuscripts, source in (
            (self.manuscripts, None),
            ([AI_MODEL_TOKEN, "Body"], self.source),
            ([AI_MODEL_TOKEN * 2, AI_MODEL_TOKEN], self.source),
            (["본문", "Body"], self.source),
        ):
            with self.subTest(manuscripts=manuscripts, source=source):
                with self.assertRaises(ValueError):
                    model_disclosure_inputs(self.root, manuscripts, source)

    def test_outside_hidden_private_and_symlink_records_are_rejected(self):
        outside = self.parent / "outside.json"
        outside.write_bytes(self.source.read_bytes())
        hidden = self.root / ".hidden.json"
        hidden.write_bytes(self.source.read_bytes())
        private = self.root / "private" / "model.json"
        private.parent.mkdir()
        private.write_bytes(self.source.read_bytes())
        link = self.root / "linked.json"
        link.symlink_to(self.source)
        traversal = self.root / "nested" / ".." / ".." / "outside.json"
        for source in (outside, hidden, private, link, traversal):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    model_disclosure_inputs(self.root, self.manuscripts, source)

    def test_unreviewed_fields_and_oversized_inputs_do_not_reach_compilation(self):
        self.source.write_text(json.dumps({**self.record, "raw_session": "not public"}))
        with self.assertRaises(ValueError):
            model_disclosure_inputs(self.root, self.manuscripts, self.source)
        self.source.write_text(json.dumps(self.record) + " " * 65536)
        with self.assertRaises(ValueError):
            model_disclosure_inputs(self.root, self.manuscripts, self.source)

    def test_conflicting_duplicate_fields_cannot_choose_the_last_model(self):
        text = json.dumps(self.record).replace(
            '"model_id": "gpt-6.1-sol"',
            '"model_id": "gpt-6.1-sol", "model_id": "different-model"',
        )
        self.source.write_text(text)
        with self.assertRaises(ValueError):
            model_disclosure_inputs(self.root, self.manuscripts, self.source)


if __name__ == "__main__":
    unittest.main()
