"""Lossless, bounded transport for the existing thirteen public search fields.

This module does no I/O, search tokenization, normalization, or ranking. Version
2 stores ordered row arrays; only titles/text may reference two earlier complete
strings in the same row. The search engine receives the unchanged v1 records.
"""
from __future__ import annotations

FIELDS = ("id", "scope", "title", "title_en", "url", "url_en", "date", "titles",
          "topics", "summary", "summary_en", "text", "headings")
COVERAGE = "Public titles, topics, summaries and study HTML headings/glossary terms; not full PDF text."
MAX_RECORDS = 10_000
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_EXPANDED_UTF16_UNITS = 2 * 1024 * 1024
MAX_WIRE_BYTES = 8 * 1024 * 1024
SOURCES = {7: (2, 3), 11: (9, 10)}


class WireError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Invalid public search wire (" + code + ").")


def _require(condition, code):
    if not condition:
        raise WireError(code)


def _string_info(value):
    """JS UTF-16 length and compact JSON UTF-8 bytes including string quotes.

    JSON escapes isolated surrogate units; valid astral characters use four
    UTF-8 bytes/two UTF-16 units. No character or whitespace is transformed.
    """
    _require(isinstance(value, str), "string_type")
    _require(len(value) <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
    units, size = len(value), 2
    for character in value:
        code = ord(character)
        units += code > 0xFFFF
        if character in {'"', "\\", "\b", "\f", "\n", "\r", "\t"}:
            size += 2
        elif code < 0x20 or 0xD800 <= code <= 0xDFFF:
            size += 6
        elif code < 0x80:
            size += 1
        elif code < 0x800:
            size += 2
        elif code < 0x10000:
            size += 3
        else:
            size += 4
        _require(units <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
        _require(size <= MAX_WIRE_BYTES, "wire_limit")
    return units, size


def _json_size(value, maximum):
    """Count only already shape-validated data, without allocating JSON bytes."""
    size = 0
    def add(amount):
        nonlocal size
        size += amount
        _require(size <= maximum, "byte_limit")
    def visit(item):
        if isinstance(item, str):
            add(_string_info(item)[1])
        elif type(item) is int:
            add(len(str(item)))
        elif isinstance(item, list):
            add(2 + max(0, len(item) - 1))
            for part in item:
                visit(part)
        elif isinstance(item, dict):
            add(2 + max(0, len(item) - 1))
            for key, part in item.items():
                add(_string_info(key)[1] + 1); visit(part)
        else:
            raise WireError("json_type")
    visit(value)
    return size


def _records(records, coverage):
    _require(isinstance(records, list) and len(records) <= MAX_RECORDS, "record_limit")
    total = _string_info(coverage)[0]
    _require(total <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
    for row in records:
        _require(isinstance(row, dict) and tuple(row) == FIELDS, "record_fields")
        for value in row.values():
            total += _string_info(value)[0]
            _require(total <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
    return total


def _compact(value, values, sources):
    first, second = (values[index] for index in sources)
    if not first or not second:
        return value
    start = value.find(first)
    if start < 0:
        return value
    end = start + len(first)
    later = value.find(second, end)
    if later < 0:
        return value
    fragments = [value[:start], sources[0], value[end:later], sources[1], value[later + len(second):]]
    fragments = [part for part in fragments if part != ""]
    if (2 <= len(fragments) <= 5
            and _json_size(fragments, MAX_WIRE_BYTES) < _string_info(value)[1]):
        return fragments
    return value


def encode_records(records, coverage=COVERAGE):
    """Encode ordered v1 record dictionaries, preserving all string values."""
    _records(records, coverage)
    _json_size({"version": 1, "coverage": coverage, "records": records}, MAX_INPUT_BYTES)
    rows = []
    for record in records:
        values = list(record.values())
        encoded = list(values)
        for target, sources in SOURCES.items():
            encoded[target] = _compact(values[target], values, sources)
        rows.append(encoded)
    wire = {"version": 2, "coverage": coverage, "fields": list(FIELDS), "records": rows}
    _json_size(wire, MAX_WIRE_BYTES)
    return wire


def _fragments(cell, values, lengths, field, remaining):
    sources = SOURCES.get(field)
    _require(sources is not None and isinstance(cell, list) and 2 <= len(cell) <= 5, "fragment_shape")
    parts, size, position = [], 0, 0
    # Exactly optional-prefix, source1, optional-middle, source2, optional-suffix.
    for source in sources:
        if position < len(cell) and isinstance(cell[position], str):
            literal = cell[position]
            _require(bool(literal), "empty_fragment")
            size += _string_info(literal)[0]; parts.append(literal); position += 1
            _require(size <= remaining, "expanded_limit")
        _require(position < len(cell) and type(cell[position]) is int and cell[position] == source,
                 "fragment_reference")
        _require(source < field and values[source] != "", "fragment_reference")
        size += lengths[source]; parts.append(values[source]); position += 1
        _require(size <= remaining, "expanded_limit")
    if position < len(cell):
        literal = cell[position]
        _require(isinstance(literal, str) and bool(literal), "fragment_literal")
        size += _string_info(literal)[0]; parts.append(literal); position += 1
        _require(size <= remaining, "expanded_limit")
    _require(position == len(cell), "extra_fragment")
    value = "".join(parts)
    return value, size


def decode_wire(wire):
    """Validate strict v2 and return an ordered, unchanged v1 record wrapper.

    Limits count compact JSON UTF-8 without a transport trailing newline and the
    sum of coverage/expanded field UTF-16 units. References never cross rows or
    point forward, nest, normalize, truncate, or authorize additional fields.
    """
    _require(isinstance(wire, dict) and set(wire) == {"version", "coverage", "fields", "records"}, "wire_keys")
    _require(type(wire["version"]) is int and wire["version"] == 2, "wire_version")
    _require(isinstance(wire["fields"], list) and wire["fields"] == list(FIELDS), "wire_fields")
    rows = wire["records"]
    _require(isinstance(rows, list) and len(rows) <= MAX_RECORDS, "record_limit")
    total = _string_info(wire["coverage"])[0]
    _require(total <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
    records = []
    for row in rows:
        _require(isinstance(row, list) and len(row) == len(FIELDS), "row_width")
        values, lengths = [], []
        for field, cell in enumerate(row):
            if isinstance(cell, str):
                value, size = cell, _string_info(cell)[0]
            else:
                value, size = _fragments(cell, values, lengths, field,
                                         MAX_EXPANDED_UTF16_UNITS - total)
            total += size
            _require(total <= MAX_EXPANDED_UTF16_UNITS, "expanded_limit")
            values.append(value); lengths.append(size)
        records.append(dict(zip(FIELDS, values)))
    result = {"version": 1, "coverage": wire["coverage"], "records": records}
    _json_size(wire, MAX_WIRE_BYTES)
    _json_size(result, MAX_INPUT_BYTES)
    return result
