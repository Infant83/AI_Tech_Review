import json
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import preview_admin_inventory as preview


class LocalPreviewBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.assets = self.root / '.automation/admin-readonly'
        self.assets.mkdir(parents=True)
        for name in ('index.html', 'app.js', 'style.css'):
            (self.assets / name).write_text('safe local ' + name)
        self.destination = self.root / 'output/new-preview'
        self.snapshot = {'schemaVersion': 1, 'snapshotToken': 'a' * 64,
                         'items': [], 'baseline': {'status': 'not_provided'}}
        self.script = patch.object(preview, '__file__', str(self.root / 'scripts/preview_admin_inventory.py'))
        self.script.start()
        self.addCleanup(self.script.stop)
        self.builder = patch.object(preview, 'build_inventory', return_value=self.snapshot)
        self.mock_builder = self.builder.start()
        self.addCleanup(self.builder.stop)

    def test_new_local_output_is_protected_and_source_assets_are_unchanged(self):
        before = {p.name: p.read_bytes() for p in self.assets.iterdir()}
        result = preview.create_preview(self.root, self.destination, None)
        self.assertTrue(result['localPreviewOnly'])
        self.assertEqual(set(p.name for p in self.destination.iterdir()),
                         {'.keep', 'inventory.json', 'index.html', 'app.js', 'style.css'})
        self.assertEqual(json.loads((self.destination / 'inventory.json').read_text()), self.snapshot)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.assets.iterdir()})

    def test_existing_successful_output_is_never_overwritten(self):
        self.destination.mkdir(parents=True)
        sentinel = self.destination / 'inventory.json'
        sentinel.write_text('previous successful snapshot')
        with self.assertRaises(preview.OutputError) as caught:
            preview.create_preview(self.root, self.destination, None)
        self.assertEqual(caught.exception.code, 'output_exists')
        self.assertEqual(sentinel.read_text(), 'previous successful snapshot')
        self.mock_builder.assert_not_called()

    def test_symlinked_output_ancestor_is_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'output').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(preview.OutputError) as caught:
            preview.create_preview(self.root, self.destination, None)
        self.assertEqual(caught.exception.code, 'output_symlink')
        self.assertFalse((outside / 'new-preview').exists())

    def test_only_ignored_output_subfolders_are_allowed(self):
        for destination in (self.root / 'site/admin', self.root / 'output'):
            with self.subTest(destination=destination):
                with self.assertRaises(preview.OutputError) as caught:
                    preview.create_preview(self.root, destination, None)
                self.assertEqual(caught.exception.code, 'output_outside_ignored_directory')

    def test_builder_failure_does_not_create_output(self):
        self.mock_builder.side_effect = ValueError('bad source')
        with self.assertRaises(ValueError):
            preview.create_preview(self.root, self.destination, None)
        self.assertFalse(self.destination.exists())

    def test_oversized_response_does_not_create_output(self):
        self.snapshot['items'] = [{'title': '가' * 700_000}]
        with self.assertRaises(preview.OutputError) as caught:
            preview.create_preview(self.root, self.destination, None)
        self.assertEqual(caught.exception.code, 'response_limit')
        self.assertFalse(self.destination.exists())

    def test_malformed_builder_result_is_rejected_before_output(self):
        self.mock_builder.return_value = {"items": []}
        with self.assertRaises(preview.OutputError) as caught:
            preview.create_preview(self.root, self.destination, None)
        self.assertEqual(caught.exception.code, 'inventory_result_invalid')
        self.assertFalse(self.destination.exists())

    def test_cli_unexpected_failure_is_sanitized_without_traceback(self):
        self.mock_builder.side_effect = RuntimeError('private fixture failure')
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = preview.main(['--root', str(self.root), '--output', str(self.destination),
                                 '--without-baseline'])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue()), {'ok': False, 'reason': 'preview_failed'})
        self.assertNotIn('Traceback', stderr.getvalue())
        self.assertNotIn(str(self.root), stderr.getvalue())
        self.assertFalse(self.destination.exists())

    def test_asset_changes_during_write_fail_and_clean_only_this_output(self):
        original_open = Path.open
        changed = False

        def open_and_change(path, *args, **kwargs):
            nonlocal changed
            if path == self.destination / 'inventory.json' and not changed:
                changed = True
                (self.assets / 'app.js').write_text('concurrent changed asset')
            return original_open(path, *args, **kwargs)

        with patch.object(Path, 'open', open_and_change):
            with self.assertRaises(preview.OutputError) as caught:
                preview.create_preview(self.root, self.destination, None)
        self.assertEqual(caught.exception.code, 'output_write_failed')
        self.assertFalse(self.destination.exists())
        self.assertEqual((self.assets / 'app.js').read_text(), 'concurrent changed asset')


if __name__ == '__main__':
    unittest.main()
