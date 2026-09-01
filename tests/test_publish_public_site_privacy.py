from __future__ import annotations

import unittest

from scripts.publish_public_site import (
    inject_public_local_note,
    public_asset_names,
    public_text_risks,
    strip_private_public_material,
)


class PublicSitePrivacyTests(unittest.TestCase):
    def test_private_message_metadata_and_working_links_are_removed(self) -> None:
        source = """
        <ul>
          <li>Private e-mail subject and timestamp: do not publish.</li>
          <li><a href="research_runlog.md">working note</a></li>
          <li><a href="figure.svg">public figure</a></li>
          <li><a href="https://arxiv.org/abs/2604.20927">public paper</a></li>
        </ul>
        <p>Source: <a href="intake.json">internal file</a></p>
        """

        sanitized = strip_private_public_material(source, "en")

        self.assertNotIn("timestamp", sanitized)
        self.assertNotIn("research_runlog.md", sanitized)
        self.assertNotIn("intake.json", sanitized)
        self.assertIn("figure.svg", sanitized)
        self.assertIn("https://arxiv.org/abs/2604.20927", sanitized)
        self.assertIn("private working file omitted", sanitized)

    def test_public_note_replaces_legacy_note(self) -> None:
        source = """
        <body>
          <section id="public-local-references" class="public-note">
            <p>Legacy note linked local review notes.</p>
          </section>
        </body>
        """

        sanitized = inject_public_local_note(source, "ko")

        self.assertEqual(sanitized.count('id="public-local-references"'), 1)
        self.assertNotIn("Legacy note", sanitized)
        self.assertIn("비공개 작업 메모", sanitized)

    def test_manifest_asset_allowlist_excludes_text_support(self) -> None:
        assets = public_asset_names(
            [
                "figure.svg",
                "hero.jpg",
                "review.md",
                "runlog.txt",
                "table.csv",
                "helper.py",
                "duplicate.html",
            ]
        )

        self.assertEqual(assets, ["figure.svg", "hero.jpg"])

    def test_private_message_metadata_is_a_publication_risk(self) -> None:
        risks = public_text_risks("Private e-mail subject and timestamp: hidden")
        self.assertIn("private message metadata", risks)

    def test_math_delimiters_in_scripts_do_not_capture_visible_smart_quotes(self) -> None:
        source = """
        <script>window.MathJax = {tex: {displayMath: [['$$', '$$']]}};</script>
        <p>The paper&rsquo;s result precedes a displayed equation.</p>
        $$
        \\mathrm{MSE}=\\mathrm{Bias}^2+\\mathrm{Variance}
        $$
        """

        self.assertNotIn("smart-quote entity inside math", public_text_risks(source))

    def test_smart_quote_entity_inside_visible_math_remains_a_risk(self) -> None:
        source = r"<p>\(W&rdquo;s\)</p>"

        self.assertIn("smart-quote entity inside math", public_text_risks(source))


if __name__ == "__main__":
    unittest.main()
