from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from scripts.publish_public_site import (
    ATRL_DATA_ASSETS,
    ATRL_DATA_FOLDER,
    REVIEWS,
    SITE_DIR,
    prune_public_support_files,
    public_asset_names,
    sanitize_for_public,
    validate_public_support_files,
)


class PublicSiteDataTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.dist = self.directory / "dist"
        self.dist.mkdir()
        self.review = replace(REVIEWS[0], folder=ATRL_DATA_FOLDER)
        self.contents = {
            "hub-publication-topics-v15.json": b'{"unit":"review works","count":55}\n',
            "hub-publication-topics-v15.csv": b"month,count\n2026-05,6\n2026-06,2\n",
        }
        for name, contents in self.contents.items():
            (self.dist / name).write_bytes(contents)
        (self.dist / "private-audit.json").write_text('{"draft":true}\n')
        (self.dist / "other.csv").write_text("private,working\n")
        self.source = (
            '<html lang="ko"><head><title>Review</title></head><body><main>'
            f'<h1>{self.review.title}</h1>'
            + ''.join(f'<a href="{name}">Data</a>' for name in sorted(ATRL_DATA_ASSETS))
            + '<a href="private-audit.json">Working audit</a><a href="other.csv">Working data</a>'
            + '</main></body></html>'
        )

    def publish(self, language="ko", review=None):
        public = self.directory / ("public-" + language)
        public.mkdir(exist_ok=True)
        selected = review or self.review
        text, assets = sanitize_for_public(
            self.source, self.dist, public, selected, language,
            SITE_DIR / "reviews" / selected.folder / ("en" if language == "en" else ""),
        )
        return public, text, assets

    def test_both_languages_preserve_only_the_exact_named_data_and_bytes(self):
        for language in ("ko", "en"):
            with self.subTest(language=language):
                public, text, assets = self.publish(language)
                self.assertEqual(set(assets), ATRL_DATA_ASSETS)
                self.assertEqual({path.name for path in public.iterdir()}, ATRL_DATA_ASSETS)
                self.assertEqual(set(public_asset_names(assets, review=self.review, language=language)), ATRL_DATA_ASSETS)
                for name, contents in self.contents.items():
                    self.assertIn(f'href="{name}"', text)
                    self.assertEqual((public / name).read_bytes(), contents)
                self.assertNotIn("private-audit.json", text)
                self.assertNotIn("other.csv", text)
                self.assertNotIn("data-local-ref", text)
                self.assertEqual(validate_public_support_files(public, review=self.review, language=language), [])

    def test_data_permission_does_not_extend_to_another_article_or_language(self):
        for language, review in (("ko", replace(self.review, folder="2026-11-08_other")), ("fr", self.review)):
            with self.subTest(language=language, folder=review.folder):
                public, text, assets = self.publish(language, review)
                self.assertEqual(assets, [])
                self.assertEqual(list(public.iterdir()), [])
                for name in ATRL_DATA_ASSETS:
                    self.assertNotIn(name, text)
                self.assertEqual(public_asset_names(ATRL_DATA_ASSETS, review=review, language=language), [])

    def test_named_data_privacy_risks_fail_before_copy_without_rewriting(self):
        path = self.dist / "hub-publication-topics-v15.json"
        for unsafe in (
            '{"source":"/Users/private/research.json"}\n',
            '{"source":"http://intranet.local/draft"}\n',
            '{"note":"Private e-mail subject and timestamp"}\n',
            '{"access_token":"ghp_' + 'a' * 36 + '"}\n',
        ):
            with self.subTest(kind=unsafe[:30]):
                path.write_text(unsafe)
                with self.assertRaisesRegex(ValueError, "Unsafe public data"):
                    self.publish()
                self.assertEqual(path.read_text(), unsafe)
                self.assertFalse((self.directory / "public-ko" / path.name).exists())

    def test_refresh_pruning_keeps_named_data_and_validation_still_scans_it(self):
        public, _, _ = self.publish()
        (public / "working.json").write_text('{"draft":true}')
        (public / "working.csv").write_text("draft\n")
        prune_public_support_files(public, review=self.review)
        self.assertEqual({path.name for path in public.iterdir()}, ATRL_DATA_ASSETS)
        (public / "hub-publication-topics-v15.csv").write_text("source\n/Users/private/data.csv\n")
        self.assertTrue(any("Unsafe public data" in error for error in validate_public_support_files(public, review=self.review)))

    def test_a_named_data_symlink_is_rejected(self):
        path = self.dist / "hub-publication-topics-v15.csv"
        target = self.dist / "another.csv"
        target.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(target.name)
        with self.assertRaisesRegex(ValueError, "Public data must be a regular file"):
            self.publish()


if __name__ == "__main__":
    unittest.main()
