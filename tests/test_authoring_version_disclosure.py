from __future__ import annotations

import html
from pathlib import Path
import unittest

from scripts import publish_public_site as publisher


class AuthoringVersionDisclosureTests(unittest.TestCase):
    methods = "https://infant83.io/AI_Tech_Review/methods/"

    def setUp(self) -> None:
        self.review = publisher.PublicReview(
            folder="2026-11-12_version-test",
            title="Version test",
            subtitle="Edition provenance",
            date="2026-11-09",
            updated="2026-11-12",
            category="AI for Science",
            tags=(),
            summary="Public review",
        )

    def fields(self, language: str) -> dict[str, str]:
        labels = publisher.METHOD_VERSION_DISCLOSURE_LABELS[language]
        return dict(zip(labels, (
            "AI Tech Review Editorial Harness, base edition 2026.08.",
            "Scientific explanation: 2026-11-06; reader-friendly explanation: 2026-11-11.",
            "Organization revised 2026-11-08–09 [3]; operations checked 2026-11-12 [10].",
            "Revision 28 · 2026-11-12; issue 2026-11-09; first publication 2026-11-10.",
        )))

    def source(self, language: str, fields: dict[str, str] | None = None) -> str:
        fields = self.fields(language) if fields is None else fields
        rows = "".join(
            f"<div><dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd></div>"
            for label, value in fields.items()
        )
        rows = rows.replace("[3]", '<a href="#ref-3">[3]</a>')
        rows = rows.replace("[10]", '<a href="#ref-10">[10]</a>')
        return f'''<html lang="{language}"><body><header>Review</header>
        <main><article><h1>Version test</h1><p id="ref-3">Organization source</p>
        <p id="ref-10">Operating source</p></article></main>
        <!-- AI Tech Review Authoring Disclosure -->
        <section class="authoring-disclosure"><dl>
        <dt>Responsible editor</dt><dd>Editor</dd><dt>AI system</dt><dd>Codex</dd>
        {rows}<dt>Evidence cutoff</dt><dd>2026-11-12</dd></dl></section>
        <!-- End AI Tech Review Authoring Disclosure --></body></html>'''

    def parse(self, text: str) -> publisher.DisclosureMetadataParser:
        parser = publisher.DisclosureMetadataParser()
        parser.feed(text)
        return parser

    def test_public_injection_preserves_each_explicit_version_layer_in_both_languages(self) -> None:
        for language in ("ko", "en"):
            with self.subTest(language=language):
                source = self.source(language)
                output = publisher.inject_review_navigation_and_disclosure(
                    source, self.review, language, self.methods,
                )
                parsed = self.parse(output)
                expected = self.fields(language)
                for index, (label, value) in enumerate(expected.items()):
                    if index == 0:
                        self.assertTrue(parsed.fields[label].startswith(value))
                        self.assertIn(self.methods, parsed.field_links[label])
                    else:
                        self.assertEqual(parsed.fields[label], value)
                self.assertNotIn("Editorial harness", parsed.fields)
                self.assertNotIn("편집 하네스", parsed.fields)
                organization = publisher.METHOD_VERSION_DISCLOSURE_LABELS[language][2]
                self.assertEqual(parsed.field_links[organization], ["#ref-3", "#ref-10"])
                self.assertEqual(output.count('id="authoring-disclosure"'), 1)
                self.assertEqual(publisher.validate_disclosure(Path("site/reviews/test/index.html"), output), [])

    def test_missing_or_blank_version_layer_keeps_existing_generic_output_exactly(self) -> None:
        for language in ("ko", "en"):
            baseline = publisher.render_authoring_disclosure(self.review, language, self.methods)
            fields = self.fields(language)
            for label in fields:
                for partial in (
                    {key: value for key, value in fields.items() if key != label},
                    {**fields, label: " "},
                ):
                    with self.subTest(language=language, label=label, partial=partial):
                        self.assertEqual(
                            publisher.render_authoring_disclosure(
                                self.review, language, self.methods, partial,
                            ),
                            baseline,
                        )

    def test_fields_are_escaped_and_only_observed_reference_fragments_are_linked(self) -> None:
        fields = self.fields("en")
        labels = publisher.METHOD_VERSION_DISCLOSURE_LABELS["en"]
        fields[labels[0]] += ' <img src=x onerror="alert(1)"> & text'
        fields[labels[2]] = "Verified [3]; unlinked [10]; external [11]."
        links = {labels[2]: ["#ref-3", "javascript:alert(1)", "https://example.com/#ref-11"]}
        _, output = publisher.render_authoring_disclosure(
            self.review, "en", self.methods, fields, links,
        )
        self.assertNotIn("<img", output)
        self.assertIn("&lt;img", output)
        self.assertIn("&amp; text", output)
        self.assertNotIn('href="javascript:', output)
        self.assertNotIn('href="https://example.com/', output)
        self.assertIn('<a href="#ref-3">[3]</a>', output)
        self.assertNotIn('href="#ref-10"', output)
        self.assertNotIn('href="#ref-11"', output)

    def test_public_refresh_is_idempotent_through_three_passes(self) -> None:
        method_urls = (
            self.methods,
            "https://infant83.github.io/AI_Tech_Review/methods/",
            "../../methods/",
            "../../../methods/",
        )
        for language in ("ko", "en"):
            for methods in method_urls:
                with self.subTest(language=language, methods=methods):
                    output = self.source(language)
                    records = []
                    disclosure_blocks = []
                    public_page = Path("site/reviews/test") / (
                        "en/index.html" if methods.startswith("../../../") else "index.html"
                    )
                    for _ in range(3):
                        output = publisher.inject_review_navigation_and_disclosure(
                            output, self.review, language, methods,
                        )
                        parsed = self.parse(output)
                        records.append((dict(parsed.fields), dict(parsed.field_links)))
                        disclosure_blocks.append(
                            publisher.AUTHORING_DISCLOSURE_BLOCK_RE.search(output).group(0).strip()
                        )
                        self.assertEqual(
                            publisher.validate_disclosure(public_page, output),
                            [],
                        )
                    self.assertEqual(records[0], records[1])
                    self.assertEqual(records[1], records[2])
                    self.assertEqual(disclosure_blocks[0], disclosure_blocks[1])
                    self.assertEqual(disclosure_blocks[1], disclosure_blocks[2])
                    labels = publisher.METHOD_VERSION_DISCLOSURE_LABELS[language]
                    self.assertEqual(records[2][1][labels[0]], [methods])
                    self.assertEqual(records[2][1][labels[2]], ["#ref-3", "#ref-10"])

    def test_authored_method_words_without_a_recorded_valid_link_are_not_removed(self) -> None:
        for language in ("ko", "en"):
            label = publisher.METHOD_VERSION_DISCLOSURE_LABELS[language][0]
            suffix = " · " + ("public method" if language == "en" else "공개 방법서")
            fields = self.fields(language)
            fields[label] += suffix
            for links in ({}, {label: ["https://example.com/methods/"]}):
                with self.subTest(language=language, links=links):
                    _, output = publisher.render_authoring_disclosure(
                        self.review, language, self.methods, fields, links,
                    )
                    parsed = self.parse(output)
                    self.assertTrue(parsed.fields[label].startswith(fields[label]))
                    self.assertEqual(parsed.fields[label].count(suffix), 2)

    def test_new_base_label_requires_all_four_layers_and_the_existing_method_url_rules(self) -> None:
        page = Path("site/reviews/test/index.html")
        for language in ("ko", "en"):
            fields = self.fields(language)
            labels = publisher.METHOD_VERSION_DISCLOSURE_LABELS[language]
            for missing in labels[1:]:
                partial = {key: value for key, value in fields.items() if key != missing}
                source = self.source(language, partial).replace(
                    html.escape(fields[labels[0]]),
                    f'{html.escape(fields[labels[0]])} <a href="{self.methods}">Methods</a>',
                )
                self.assertTrue(publisher.validate_disclosure(page, source))
            _, invalid_url = publisher.render_authoring_disclosure(
                self.review, language, "https://example.com/methods/", fields,
            )
            self.assertIn("missing public method link", " ".join(publisher.validate_disclosure(page, invalid_url)))
            output = publisher.inject_review_navigation_and_disclosure(
                self.source(language), self.review, language, self.methods,
            )
            parsed = self.parse(output)
            core = (
                ("Responsible editor", "AI system", "Evidence cutoff")
                if language == "en" else ("책임 편집자", "AI 시스템", "근거 기준일")
            )
            for label in core:
                value = parsed.fields[label]
                without_core = output.replace(
                    f"<dt>{label}</dt><dd>{html.escape(value)}</dd>",
                    f"<dt>{label}</dt><dd></dd>",
                )
                self.assertTrue(publisher.validate_disclosure(page, without_core))


if __name__ == "__main__":
    unittest.main()
