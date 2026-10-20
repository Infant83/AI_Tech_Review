from __future__ import annotations

from html.parser import HTMLParser
import json
import unittest

from scripts import briefing_site


BASE_URL = "https://infant83.github.io/AI_Tech_Review/"


def document(day: str, suffix: str = "daily", series: str = "daily-quantum") -> dict:
    identity = f"{day}-{suffix}"
    return {
        "id": identity,
        "date": day,
        "series": series,
        "title": "양자 오류 정정의 새 연구",
        "title_en": "New research in quantum error correction",
        "summary": "검증된 공개 연구를 소개하는 브리핑입니다.",
        "summary_en": "A briefing on published research.",
        "tags": ["Quantum error correction"],
        "language": "ko",
        "href": f"archive/files/{identity}.pdf",
        "file": f"files/{identity}.pdf",
        "public_reviewed": True,
        "source_title": "PRIVATE_SOURCE_TITLE",
        "mail_id": "PRIVATE_MAIL_ID",
        "size_bytes": 1234,
        "sha256": "private-for-client-data",
    }


class CalendarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict]] = []
        self.cell: dict | None = None
        self.links: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "tr":
            self.rows.append([])
        elif tag == "td":
            self.cell = {**values, "buttons": [], "links": []}
            self.rows[-1].append(self.cell)
        elif tag == "button" and self.cell is not None:
            self.cell["buttons"].append(values)
        elif tag == "a":
            self.links.append(values)
            if self.cell is not None:
                self.cell["links"].append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            self.cell = None


class EmbeddedDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.payload = ""
        self.in_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.in_data = tag == "script" and values.get("id") == "briefing-data"
        if self.in_data:
            assert values.get("type") == "application/json"

    def handle_data(self, data: str) -> None:
        if self.in_data:
            self.payload += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_data = False


class BriefingSiteTests(unittest.TestCase):
    def test_public_briefing_data_excludes_other_series_and_private_source_fields(self) -> None:
        daily = document("2026-10-20")
        weekly = document("2026-10-16", "weekly", "weekly-review")
        article = document("2026-10-19", "article", "article")
        lecture = document("2026-10-18", "lecture", "lecture-notes")

        selected = briefing_site.briefing_documents([daily, weekly, article, lecture], prefix="../")

        self.assertEqual({item["id"] for item in selected}, {daily["id"], weekly["id"]})
        allowed = {"id", "date", "series", "title", "title_en", "summary", "summary_en", "tags", "language", "href"}
        for item in selected:
            self.assertTrue(set(item) <= allowed)
            self.assertEqual(item["href"], "../archive/files/" + item["id"] + ".pdf")
        serialized = json.dumps(selected)
        for secret in ("PRIVATE_SOURCE_TITLE", "PRIVATE_MAIL_ID", "private-for-client-data"):
            self.assertNotIn(secret, serialized)

    def test_month_navigation_includes_empty_months_and_crosses_year_boundaries(self) -> None:
        items = [document("2025-01-02"), document("2024-11-30")]

        self.assertEqual(briefing_site.calendar_months(items), ["2025-01", "2024-12", "2024-11"])
        self.assertEqual(briefing_site.calendar_months([]), [])

    def test_leap_year_calendar_uses_monday_first_and_keeps_february_29(self) -> None:
        items = [document("2024-02-01"), document("2024-02-29")]
        parser = CalendarParser()

        parser.feed(briefing_site.render_calendar(items, "2024-02"))

        self.assertTrue(parser.rows)
        self.assertTrue(all(len(row) == 7 for row in parser.rows))
        cells = [cell for row in parser.rows for cell in row]
        dated_cells = {
            button["data-date"]: (index, cell, button)
            for index, cell in enumerate(cells)
            for button in cell["buttons"]
            if button.get("data-date")
        }
        self.assertEqual(len(dated_cells), 29)
        self.assertEqual(dated_cells["2024-02-01"][0], 3, "February 1, 2024 is Thursday in a Monday-first calendar")
        self.assertEqual(dated_cells["2024-02-29"][0], 31)
        for day in ("2024-02-01", "2024-02-29"):
            _index, cell, button = dated_cells[day]
            self.assertIn("has-briefing", cell.get("class", "").split())
            self.assertNotIn("disabled", button)
            self.assertIn("day-select", button.get("class", "").split())
            self.assertEqual(button.get("aria-pressed"), "false")
        self.assertIn("disabled", dated_cells["2024-02-02"][2], "Dates without a published briefing must not appear readable")

    def test_calendar_keeps_multiple_topics_published_on_the_same_date(self) -> None:
        first = document("2026-10-20", "quantum-error-correction")
        second = document("2026-10-20", "quantum-network")
        second.update(title="양자 네트워크 실험", title_en="Quantum network experiment")
        parser = CalendarParser()

        rendered = briefing_site.render_calendar([first, second], "2026-10")
        parser.feed(rendered)

        cells = [cell for row in parser.rows for cell in row]
        target = next(cell for cell in cells if any(button.get("data-date") == "2026-10-20" for button in cell["buttons"]))
        self.assertEqual(len(target["buttons"]), 1, "One date control must represent all issues on that date")
        self.assertEqual({link.get("href") for link in target["links"]}, {first["href"], second["href"]})
        self.assertIn(first["title"], rendered)
        self.assertIn(second["title"], rendered)

    def test_embedded_json_cannot_escape_its_script_element_and_has_a_public_allowlist(self) -> None:
        item = document("2026-10-20")
        attack = '</script><script>alert("unsafe")</script><b>& topic'
        item.update(title=attack, title_en=attack, summary=attack, summary_en=attack, tags=[attack])

        page = briefing_site.render_briefings([item], BASE_URL)
        parser = EmbeddedDataParser()
        parser.feed(page)
        payload = json.loads(parser.payload)

        self.assertEqual(payload["months"], ["2026-10"])
        self.assertEqual(payload["latest_month"], "2026-10")
        self.assertEqual(payload["documents"][0]["title"], attack)
        self.assertNotIn("<", parser.payload)
        self.assertNotIn(">", parser.payload)
        self.assertNotIn("&", parser.payload)
        self.assertNotIn('<script>alert("unsafe")</script>', page)
        self.assertNotIn("PRIVATE_SOURCE_TITLE", page)
        self.assertNotIn("PRIVATE_MAIL_ID", page)


if __name__ == "__main__":
    unittest.main()
