"""Small pure fixtures for exact public search wire; no site/index generation."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from scripts import site_search_wire as wire


class SearchWireTests(unittest.TestCase):
    def record(self, identifier="first"):
        row = dict.fromkeys(wire.FIELDS, "")
        row.update(id=identifier, scope="reviews", title="한글 광자 " + "A🧪B" * 12,
                   title_en="Exact ENGLISH " + "e\u0301" * 20, url="reviews/" + identifier + "/",
                   url_en="reviews/" + identifier + "/en/", date="2026-11-28",
                   topics="Case  空白\n\t\"\\", summary="한글 원문 " + "반복 " * 20,
                   summary_en="English SUMMARY " + "unchanged " * 20,
                   headings="isolated \udc00 · fullwidth Ａ · ㍿")
        row["titles"] = "prefix " + row["title"] + " / " + row["title_en"] + " suffix"
        row["text"] = "before\n" + row["summary"] + " MID " + row["summary_en"] + "\nafter"
        return row

    def raw(self, value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "backslashreplace")

    def rejects(self, value):
        before = deepcopy(value)
        with self.assertRaises(wire.WireError) as caught:
            wire.decode_wire(value)
        self.assertEqual(value, before)
        self.assertNotIn("PRIVATE_SENTINEL", str(caught.exception))

    def test_exact_all_fields_row_key_order_and_no_input_mutation(self):
        records = [self.record("second"), self.record("first")]
        records[1]["scope"] = "lectures"
        before = deepcopy(records)
        encoded = wire.encode_records(records)
        self.assertEqual(set(encoded), {"version", "coverage", "fields", "records"})
        self.assertEqual(encoded["version"], 2)
        self.assertEqual(encoded["fields"], list(wire.FIELDS))
        self.assertIsInstance(encoded["records"][0][7], list)
        self.assertIsInstance(encoded["records"][0][11], list)
        decoded = wire.decode_wire(json.loads(self.raw(encoded)))
        self.assertEqual(decoded, {"version": 1, "coverage": wire.COVERAGE, "records": records})
        self.assertEqual([row["id"] for row in decoded["records"]], ["second", "first"])
        for old, new in zip(records, decoded["records"]):
            self.assertEqual(tuple(new), wire.FIELDS)
            for field in wire.FIELDS:
                self.assertEqual(old[field].encode("utf-16-le", "surrogatepass"),
                                 new[field].encode("utf-16-le", "surrogatepass"))
        self.assertEqual(records, before)

    def test_only_allowed_cells_use_exact_earlier_reference_order(self):
        encoded = wire.encode_records([self.record()])
        row = encoded["records"][0]
        for index, cell in enumerate(row):
            if index in {7, 11}:
                self.assertTrue(2 <= len(cell) <= 5)
                self.assertEqual([part for part in cell if type(part) is int],
                                 [2, 3] if index == 7 else [9, 10])
                self.assertTrue(all(part != "" for part in cell))
            else:
                self.assertIsInstance(cell, str)

    def test_empty_missing_overlap_and_non_saving_matches_remain_literal(self):
        for kind in ["empty", "missing", "overlap", "not_smaller"]:
            with self.subTest(kind=kind):
                row = self.record()
                if kind == "empty":
                    row["title_en"] = ""
                elif kind == "missing":
                    row["titles"] = "contains neither earlier source"
                elif kind == "overlap":
                    row.update(title="abcdefghij", title_en="fghij", titles="abcdefghij")
                elif kind == "not_smaller":
                    row.update(title="A", title_en="B", titles="A B")
                encoded = wire.encode_records([row])
                self.assertIsInstance(encoded["records"][0][7], str)
                self.assertEqual(wire.decode_wire(encoded)["records"], [row])

    def test_first_match_and_sequential_second_match_are_deterministic(self):
        row = self.record()
        row["titles"] = row["title"] + " one " + row["title_en"] + " two " + row["title"]
        encoded = wire.encode_records([row])
        self.assertEqual(encoded, wire.encode_records(deepcopy([row])))
        self.assertEqual(encoded["records"][0][7], [2, " one ", 3, " two " + row["title"]])
        self.assertEqual(wire.decode_wire(encoded)["records"], [row])
        row["titles"] = row["title"] + row["title_en"]
        encoded = wire.encode_records([row])
        self.assertEqual(encoded["records"][0][7], [2, 3])
        self.assertEqual(wire.decode_wire(encoded)["records"], [row])

    def test_top_version_fields_row_width_and_literal_types_fail_closed(self):
        normal = wire.encode_records([self.record()])
        mutations = [lambda d: d.update(extra="PRIVATE_SENTINEL"),
                     lambda d: d.pop("coverage"), lambda d: d.update(version=True),
                     lambda d: d.update(version=2.0), lambda d: d.update(version=1),
                     lambda d: d.update(fields=list(reversed(wire.FIELDS))),
                     lambda d: d.update(fields=list(wire.FIELDS[:-1])),
                     lambda d: d["records"][0].pop(),
                     lambda d: d["records"][0].append("extra"),
                     lambda d: d["records"][0].__setitem__(0, None),
                     lambda d: d["records"][0].__setitem__(8, [2, " ", 3])]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                bad = deepcopy(normal); mutate(bad); self.rejects(bad)

    def test_malformed_bool_negative_forward_nested_extra_and_empty_fragments_refuse(self):
        normal = wire.encode_records([self.record()])
        malformed = [[True, " ", 3], [-2, " ", 3], [7, " ", 3], [2, " ", 7],
                     [3, " ", 2], [2, " ", 3.0], [[2], " ", 3], [2, "", 3],
                     [2, " ", 3, "", "suffix"], [2, " ", 3, "x", "y"],
                     [2, " ", 3, "x", "y", "z"], [2], []]
        for cell in malformed:
            with self.subTest(cell=cell):
                bad = deepcopy(normal); bad["records"][0][7] = cell; self.rejects(bad)

    def test_generation_saves_bytes_but_decoder_only_requires_valid_structure(self):
        normal = wire.encode_records([self.record()])
        bad = deepcopy(normal); bad["records"][0][2] = ""; self.rejects(bad)
        short = dict.fromkeys(wire.FIELDS, "")
        short.update(id="short", title="A", title_en="B", titles="A B")
        alternate = wire.encode_records([short])
        self.assertEqual(alternate["records"][0][7], "A B")
        alternate["records"][0][7] = [2, " ", 3]
        self.assertEqual(wire.decode_wire(alternate)["records"], [short])
        # An alternative valid earlier-source layout also expands exactly.
        row = self.record(); row["titles"] = row["title"] + " " + row["title"] + " " + row["title_en"]
        alternate = wire.encode_records([row])
        alternate["records"][0][7] = [row["title"] + " ", 2, " ", 3]
        self.assertEqual(wire.decode_wire(alternate)["records"], [row])

    def test_encode_rejects_changed_key_sets_order_and_non_string_without_mutation(self):
        for kind in ["extra", "missing", "order", "value"]:
            row = self.record()
            if kind == "extra": row["extra"] = "PRIVATE_SENTINEL"
            elif kind == "missing": row.pop("headings")
            elif kind == "order": row = dict(reversed(list(row.items())))
            else: row["headings"] = False
            before = deepcopy(row)
            with self.subTest(kind=kind), self.assertRaises(wire.WireError):
                wire.encode_records([row])
            self.assertEqual(row, before)

    def test_exact_row_expanded_input_and_wire_caps_and_one_over(self):
        records = [self.record()]
        encoded = wire.encode_records(records)
        v1 = {"version": 1, "coverage": wire.COVERAGE, "records": records}
        units = sum(len(value.encode("utf-16-le", "surrogatepass")) // 2
                    for value in [wire.COVERAGE, *records[0].values()])
        for constant, exact in [("MAX_RECORDS", 1), ("MAX_EXPANDED_UTF16_UNITS", units),
                                ("MAX_INPUT_BYTES", len(self.raw(v1))),
                                ("MAX_WIRE_BYTES", len(self.raw(encoded)))]:
            with self.subTest(constant=constant), patch.object(wire, constant, exact):
                self.assertEqual(wire.decode_wire(encoded), v1)
                self.assertEqual(wire.encode_records(records), encoded)
            with self.subTest(constant=constant, over=True), patch.object(wire, constant, exact - 1):
                with self.assertRaises(wire.WireError): wire.decode_wire(encoded)
                with self.assertRaises(wire.WireError): wire.encode_records(records)

    def test_empty_records_coverage_and_escaping_roundtrip(self):
        coverage = "한글 🧪 e\u0301\n\t\"\\ \ud800"
        result = wire.decode_wire(wire.encode_records([], coverage))
        self.assertEqual(result, {"version": 1, "coverage": coverage, "records": []})
        self.assertEqual(wire.COVERAGE, "Public titles, topics, summaries and study HTML headings/glossary terms; not full PDF text.")


if __name__ == "__main__":
    unittest.main()
