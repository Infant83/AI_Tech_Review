from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import generate_readme


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_readme.py"
PERSISTENT_REFERENCES = (
    "[아카이브 운영 안내](archive/README.md)",
    "`archive/manifest.json`",
    "[리뷰허브](https://infant83.github.io/AI_Tech_Review/)",
    "[렉처 노트](https://infant83.github.io/AI_Tech_Review/lectures/)",
    "[전체 자료 아카이브](https://infant83.github.io/AI_Tech_Review/archive/)",
    "python3 scripts/publish_public_site.py --hub-only",
    "`site/manifest.json`",
    "`site/archive-manifest.json`",
    "[과학 표지 제작 원칙](COVER_ART_DIRECTION.md)",
    "[표지 기획 양식](templates/cover-art-brief.md)",
)


class GenerateReadmeTests(unittest.TestCase):
    def assert_persistent_guidance(self, text: str) -> None:
        for reference in PERSISTENT_REFERENCES:
            with self.subTest(reference=reference):
                self.assertEqual(text.count(reference), 1)

    def test_generation_retains_guidance_without_an_existing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            daily = root / "daily_research_review"
            daily.mkdir()
            for day, title in ((18, "Older review"), (20, "Latest review"), (19, "Middle review")):
                (daily / f"2026-10-{day}_review.md").write_text(
                    f"# {title}\n\n## Summary\n- First finding\n- Second finding\n",
                    encoding="utf-8",
                )
            with patch.object(generate_readme, "ROOT", root), patch.object(generate_readme, "DAILY_DIR", daily):
                entries = generate_readme.collect_entries()
                first = generate_readme.render_readme(entries, 2)
                repeated = generate_readme.render_readme(entries, 2)
                smaller = generate_readme.render_readme(entries, 1)
                empty = generate_readme.render_readme([], 5)

            self.assertEqual(first, repeated)
            for text in (first, repeated, smaller, empty):
                self.assert_persistent_guidance(text)
            self.assertIn("최신 2개 항목", first)
            self.assertLess(first.index("### 2026-10-20 · Latest review"), first.index("### 2026-10-19 · Middle review"))
            self.assertNotIn("Older review", first)
            self.assertIn("daily_research_review/2026-10-20_review.md", first)
            self.assertIn("- First finding\n- Second finding", first)
            self.assertIn("최신 1개 항목", smaller)
            self.assertIn("Latest review", smaller)
            self.assertNotIn("Middle review", smaller)
            self.assertIn("No daily review items were found yet.", empty)
            self.assertFalse((root / "README.md").exists())

    def test_cli_output_can_be_regenerated_without_losing_guidance(self) -> None:
        repository_readme = SCRIPT.parents[1] / "README.md"
        original_readme = repository_readme.read_bytes()
        expected_entries = generate_readme.collect_entries()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "README.md"
            for limit in (2, 2, 1):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--limit", str(limit), "--output", str(output)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                text = output.read_text(encoding="utf-8")
                self.assert_persistent_guidance(text)
                self.assertEqual(text, generate_readme.render_readme(expected_entries, limit) + "\n")

        self.assertEqual(repository_readme.read_bytes(), original_readme)


if __name__ == "__main__":
    unittest.main()
