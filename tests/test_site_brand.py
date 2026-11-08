import unittest

from scripts.site_brand import SITE_NAME, current_source_title, normalize_brand_html


class CurrentJournalBrandTests(unittest.TestCase):
    def test_current_chrome_changes_without_touching_issue_history_or_science(self):
        science = ('<article class="final-article"><h1>AI Tech Review Letters as a historical title</h1>'
                   '<p class="brand">AI Tech Review Letters</p>'
                   '<code>AI Tech Review Letters</code><svg><text>Q = 1</text></svg></article>')
        original = ('<html>\n<head><title>Lecture | AI Tech Review Letters</title>'
                    '<meta property="og:site_name" content="AI Tech Review Letters"></head>'
                    '<body><nav class="top"><a href="../">AI Tech Review Letters</a></nav>'
                    '<div class="topline"><span>AI Tech Review Letters: Week 19 (2026-05-06)</span>'
                    '<span class="brand">AI TECH REVIEW LETTERS</span></div>'
                    '<header class="hero"><p class="eyebrow">AI Tech Review Letters</p></header>'
                    + science + '<footer class="footer">AI Tech Review Letters · 2026-05-06<br>부제</footer>'
                    '<aside class="authoring-disclosure">AI Tech Review Editorial Harness 2026.08</aside>'
                    '<script>const label = "AI Tech Review Letters";</script></body></html>')
        result = normalize_brand_html(original)
        self.assertIn(science, result)
        self.assertIn('AI Tech Review Letters: Week 19 (2026-05-06)', result)
        self.assertIn('AI Tech Review Editorial Harness 2026.08', result)
        self.assertIn('const label = "AI Tech Review Letters";', result)
        self.assertIn(f'<title>Lecture | {SITE_NAME}</title>', result)
        self.assertIn(f'content="{SITE_NAME}"', result)
        self.assertIn(f'<a href="../">{SITE_NAME}</a>', result)
        self.assertIn(f'<span class="brand">{SITE_NAME.upper()}</span>', result)
        self.assertIn(f'{SITE_NAME} · 2026-05-06<br>부제', result)
        self.assertEqual(normalize_brand_html(result), result)

    def test_title_body_quotation_and_third_party_source_are_preserved(self):
        original = ('<title>History of AI Tech Review Letters</title>'
                    '<main><p>Quoted AI Tech Review Letters</p>'
                    '<div class="footer">A citation to AI Tech Review Letters</div></main>')
        self.assertEqual(normalize_brand_html(original), original)
        self.assertEqual(current_source_title('Nature Reviews'), 'Nature Reviews')
        self.assertEqual(current_source_title('AI Tech Review Letters: Week 19'), 'AI Tech Review Letters: Week 19')
        self.assertEqual(current_source_title('AI Tech Review Letters'), SITE_NAME)

    def test_original_crlf_markup_quotes_links_and_subtitle_are_unchanged(self):
        original = "<header>\r\n<a class='brand' href='same#anchor'>AI TECH REVIEW LETTERS</a>\r\n</header>"
        expected = original.replace('AI TECH REVIEW LETTERS', SITE_NAME.upper())
        self.assertEqual(normalize_brand_html(original), expected)
        footer = '<main><div class="footer"><a href="same">AI Tech Review Letters</a><br>original subtitle</div></main>'
        self.assertEqual(normalize_brand_html(footer), footer.replace('AI Tech Review Letters', SITE_NAME))


if __name__ == '__main__':
    unittest.main()
