from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

try:
    import markdown  # noqa: F401
    HAS_MARKDOWN = True
except ModuleNotFoundError:
    HAS_MARKDOWN = False
    markdown_stub = types.ModuleType("markdown")
    markdown_stub.Markdown = object  # type: ignore[attr-defined]
    sys.modules["markdown"] = markdown_stub

from scripts.markdown_to_html import (  # noqa: E402
    ProtectedMathExpression,
    build_markdown_html,
    protect_math_expressions,
    restore_math_expressions,
    strip_frontmatter,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
IGNORE_DOLLAR = '<span class="tex2jax_ignore">$</span>'


def expression_sources(expressions: list[ProtectedMathExpression]) -> list[str]:
    return [expression.source for expression in expressions]


class MathProtectionTests(unittest.TestCase):
    def test_code_and_raw_html_are_opaque(self) -> None:
        source = r'''Outside $x_y$.

`inline $not_math$ and \(not_math\)`

```python
price = "$5"
formula = r"\[not_math\]"
```

<a href="/plans/$5" data-formula="$not_math$" title="\(not_math\)">link</a>
<script>const price = "$5";</script>

Outside again \(z_i * z_i\).
'''

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(
            expression_sources(expressions), ["$x_y$", r"\(z_i * z_i\)"]
        )
        self.assertIn('`inline $not_math$ and \\(not_math\\)`', protected)
        self.assertIn('price = "$5"', protected)
        self.assertIn('data-formula="$not_math$"', protected)
        self.assertIn('<script>const price = "$5";</script>', protected)
        self.assertEqual(restore_math_expressions(protected, expressions), source)

    def test_delimiters_do_not_search_across_opaque_ranges(self) -> None:
        source = (
            'Before $orphan `code $x$` and '
            '<a title="$attr$">link</a> after $real$.'
        )

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(expression_sources(expressions), ["$real$"])
        self.assertIn(f"Before {IGNORE_DOLLAR}orphan", protected)
        self.assertIn('`code $x$`', protected)
        self.assertIn('title="$attr$"', protected)

    def test_escaped_backticks_do_not_open_code_and_tex_is_html_safe(self) -> None:
        source = r"\`not code $a<b & c>$\`"

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(expression_sources(expressions), ["$a<b & c>$"])
        self.assertEqual(
            restore_math_expressions(protected, expressions),
            r"\`not code $a&lt;b &amp; c&gt;$\`",
        )

    def test_currency_and_other_literal_dollars_cannot_cross_pair(self) -> None:
        literals = (
            "$5 and Pro costs $10",
            "$5-$10",
            "$5/kg",
            "$5M",
            "$5.0-beta",
            '"$5"',
            "$HOME",
        )
        for literal in literals:
            with self.subTest(literal=literal):
                source = f"{literal} and state $x_1$."
                protected, expressions = protect_math_expressions(source)
                self.assertEqual(expression_sources(expressions), ["$x_1$"])
                self.assertIn(IGNORE_DOLLAR, protected)

    def test_indented_code_and_markdown_destinations_are_opaque(self) -> None:
        source = r'''    price = "$5"
    formula = "$x_y$"

[item](https://example.test/items/$5 "cost $5")
[book](https://x.test/O'Reilly/$5)
[label][$id$]
<https://x.test/items/$5>
<mailto:user+$5@example.com>
![alt $5](https://example.test/image/\$5.png)

Outside $x_y$.
'''

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(expression_sources(expressions), ["$x_y$"])
        self.assertIn('    price = "$5"', protected)
        self.assertIn('(https://example.test/items/$5 "cost $5")', protected)
        self.assertIn("(https://x.test/O'Reilly/$5)", protected)
        self.assertIn("[label][$id$]", protected)
        self.assertIn("<https://x.test/items/$5>", protected)
        self.assertIn("<mailto:user+$5@example.com>", protected)
        self.assertIn('![alt $5](https://example.test/image/\\$5.png)', protected)

    def test_compact_table_currency_does_not_pair_across_cells(self) -> None:
        source = "|a|b|\n|-|-|\n|$5|$x_y$|"

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(expression_sources(expressions), ["$x_y$"])
        self.assertEqual(protected.splitlines()[-1].count("|"), 3)
        self.assertIn(IGNORE_DOLLAR, protected)

        three_cells = "|price|label|state|\n|-|-|-|\n|$5|formula|$x_y$|"
        protected, expressions = protect_math_expressions(three_cells)
        self.assertEqual(expression_sources(expressions), ["$x_y$"])
        self.assertEqual(protected.splitlines()[-1].count("|"), 4)
        self.assertIn(IGNORE_DOLLAR, protected)

        absolute_values = "|value|\n|-|\n|$|x|$|\n|$\\|y\\|$|"
        protected, expressions = protect_math_expressions(absolute_values)
        self.assertEqual(
            expression_sources(expressions), ["$|x|$", "$\\|y\\|$"]
        )
        self.assertTrue(
            all(row.count("|") == 2 for row in protected.splitlines()[2:])
        )

    def test_blockquote_display_math_and_placeholder_collision(self) -> None:
        blockquote = "> $$\n> x_y\n>$$"
        protected, expressions = protect_math_expressions(blockquote)

        self.assertEqual(expression_sources(expressions), ["$$\nx_y\n$$"])
        restored = restore_math_expressions(protected, expressions)
        self.assertEqual(restored, "> $$\nx_y\n$$")
        self.assertNotIn("&gt;", restored)

        collision = (
            '<span data-ai-tech-math-0="0"></span> and $x$'
        )
        protected, expressions = protect_math_expressions(collision)
        self.assertIn('data-ai-tech-math-1="0"', protected)
        self.assertEqual(
            restore_math_expressions(protected, expressions), collision
        )

    @unittest.skipUnless(HAS_MARKDOWN, "Python-Markdown is not installed")
    def test_renderer_preserves_all_stress_cases(self) -> None:
        body, _ = build_markdown_html(
            '    price = "$5"\n    formula = "$x_y$"\n'
        )
        self.assertIn('price = "$5"', body)
        self.assertIn('formula = "$x_y$"', body)
        self.assertNotIn("tex2jax_ignore", body)

        body, _ = build_markdown_html(
            r'[item](https://example.test/items/$5) '
            r"[book](https://x.test/O'Reilly/$5) "
            r'<https://x.test/items/$5> '
            r'<mailto:user+$5@example.com> '
            r'![alt $5](https://example.test/image/\$5.png)'
        )
        self.assertIn('href="https://example.test/items/$5"', body)
        self.assertIn('href="https://x.test/O\'Reilly/$5"', body)
        self.assertIn('href="https://x.test/items/$5"', body)
        self.assertIn('alt="alt $5"', body)
        self.assertNotIn("tex2jax_ignore", body)

        body, _ = build_markdown_html("|a|b|\n|-|-|\n|$5|$x_y$|")
        self.assertIn(f"<td>{IGNORE_DOLLAR}5</td>", body)
        self.assertIn("<td>$x_y$</td>", body)

        body, _ = build_markdown_html("> $$\n> x_y\n>$$")
        self.assertIn("$$\nx_y\n$$", body)
        self.assertNotIn("&gt;", body)

        collision = '<span data-ai-tech-math-0="0"></span> and $x$'
        body, _ = build_markdown_html(collision)
        self.assertIn(collision, body)

    def test_all_four_math_delimiters_and_table_pipes_are_protected(self) -> None:
        source = r'''| form | expression |
|---|---|
| dollar | $\lvert 0 | 1\rangle$ |
| slash | \(x_i * y_i\) |

$$
H_{ij}=a_i b_j
$$

\[
Q_{ij}=c_i d_j
\]
'''

        protected, expressions = protect_math_expressions(source)

        self.assertEqual(
            expression_sources(expressions),
            [
                r"$\lvert 0 | 1\rangle$",
                r"\(x_i * y_i\)",
                "$$\nH_{ij}=a_i b_j\n$$",
                "\\[\nQ_{ij}=c_i d_j\n\\]",
            ],
        )
        table_rows = protected.splitlines()[:4]
        self.assertTrue(all(row.count("|") == 3 for row in table_rows))
        self.assertEqual(restore_math_expressions(protected, expressions), source)

        indented_display = "$$\n    H_{ij}=x\n$$\n\n\\[\n    Q_i=y\n\\]"
        _, expressions = protect_math_expressions(indented_display)
        self.assertEqual(
            expression_sources(expressions),
            ["$$\n    H_{ij}=x\n$$", "\\[\n    Q_i=y\n\\]"],
        )

    def test_current_august_29_report_math_is_unchanged(self) -> None:
        report_directory = (
            REPOSITORY_ROOT
            / "2026-08-29_quantum-simulation-vibronic-dynamics"
            / "reports"
        )
        expected_counts = {
            "2026-08-29_quantum-simulation-vibronic-dynamics_final_review.md": 80,
            "2026-08-29_quantum-simulation-vibronic-dynamics_final_review_en.md": 73,
        }

        for filename, expected_count in expected_counts.items():
            with self.subTest(filename=filename):
                _, source = strip_frontmatter(
                    (report_directory / filename).read_text(encoding="utf-8")
                )
                protected, expressions = protect_math_expressions(source)
                self.assertEqual(len(expressions), expected_count)
                self.assertNotIn("tex2jax_ignore", protected)
                self.assertEqual(
                    restore_math_expressions(protected, expressions), source
                )


if __name__ == "__main__":
    unittest.main()
