from __future__ import annotations

import unittest

from scripts.briefing_routes import editorial_paths


class BriefingRoutesTests(unittest.TestCase):
    def test_regular_and_legacy_issue_routes_are_unchanged(self):
        published = "2026-11-17"
        for series, namespace in (("daily-quantum", "briefings"),
                                  ("weekly-review", "briefings"),
                                  ("daily-research", "briefings/research"),
                                  ("daily-quantum-exercise", "briefings/exercises")):
            expected = (f"{namespace}/{published}/index.html", f"{namespace}/{published}/en/index.html")
            for identifier in (None, published + "-legacy-topic", published + "-" + series):
                with self.subTest(series=series, identifier=identifier):
                    self.assertEqual(editorial_paths(published, series, identifier), expected)

    def test_only_explicit_exercise_supplements_gain_a_slug(self):
        published = "2026-11-17"
        identifier = published + "-daily-quantum-exercise-ntca"
        self.assertEqual(editorial_paths(published, "daily-quantum-exercise", identifier),
                         ("briefings/exercises/2026-11-17/ntca/index.html",
                          "briefings/exercises/2026-11-17/ntca/en/index.html"))
        self.assertEqual(editorial_paths(published, "daily-research", identifier),
                         ("briefings/research/2026-11-17/index.html", "briefings/research/2026-11-17/en/index.html"))
        self.assertEqual(editorial_paths(published, "daily-quantum-exercise", published + "-ntca"),
                         ("briefings/exercises/2026-11-17/index.html", "briefings/exercises/2026-11-17/en/index.html"))

    def test_unsafe_or_reserved_supplement_slugs_cannot_alias_public_paths(self):
        for slug in ("", "en", "../other", "en/other", "NTCA", "a_b", "a--b", "한글", "a%2fb", "a\\b"):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                editorial_paths("2026-11-17", "daily-quantum-exercise", "2026-11-17-daily-quantum-exercise-" + slug)


if __name__ == "__main__":
    unittest.main()
