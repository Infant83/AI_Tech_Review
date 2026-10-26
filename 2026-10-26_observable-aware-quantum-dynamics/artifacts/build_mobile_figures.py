#!/usr/bin/env python3
"""Stack the approved desktop SVG panels without changing plotted geometry.

Only translation, line wrapping and type size change. Curve points, bar widths,
axis positions within each panel, labels, scales and values remain unchanged.
"""
from __future__ import annotations

import copy
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ROOT = Path(__file__).resolve().parents[1]


def tag(name):
    return f"{{{NS}}}{name}"


def units(text):
    return sum(1.0 if unicodedata.east_asian_width(c) in "WF" else
               .30 if c.isspace() else .56 for c in text)


def wrapped(text, width, size):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and units(candidate) * size > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def text_lines(parent, text, x, y, cls="small", width=530, size=20,
               leading=29):
    lines = wrapped(text, width, size)
    for line in lines:
        el = ET.SubElement(parent, tag("text"), x=str(x), y=str(y),
                           attrib={"class": cls})
        el.text = line
        y += leading
    return y


def new_root(source):
    out = ET.Element(tag("svg"), width="600", height="1500",
                     viewBox="0 0 600 1500", role="img",
                     attrib={"aria-labelledby": "title desc"})
    for node in list(source)[:2]:
        out.append(copy.deepcopy(node))
    ET.SubElement(out, tag("rect"), width="100%", height="100%",
                  fill="#fffdf8")
    style = ET.SubElement(out, tag("style"))
    style.text = ('text{font-family:Arial,"Apple SD Gothic Neo",'
                  '"Malgun Gothic",sans-serif;fill:#23333d}'
                  '.title{font-size:26px;font-weight:700}'
                  '.small{font-size:20px}.label{font-size:22px}'
                  '.tick{font-size:19px}')
    texts = [n for n in source if n.tag == tag("text")]
    y = text_lines(out, texts[0].text, 30, 37, "title", size=26,
                   leading=34)
    y = text_lines(out, texts[1].text, 30, y + 2, width=530)
    return out, y


def group(parent, elements, dx, dy, axis_x=None):
    out = ET.SubElement(parent, tag("g"),
                        transform=f"translate({dx} {dy})")
    for original in elements:
        node = copy.deepcopy(original)
        if axis_x is not None and node.tag == tag("text") and \
                node.get("transform", "").startswith("rotate(-90"):
            y = node.get("y")
            node.set("x", str(axis_x))
            node.set("transform", f"rotate(-90 {axis_x} {y})")
        out.append(node)


def finish(source, out, target, height):
    out.set("height", str(height))
    out.set("viewBox", f"0 0 600 {height}")
    # Line wrapping keeps every visible word, including the scope notes.
    old = " ".join(" ".join(source.itertext()).split())
    new = " ".join(" ".join(out.itertext()).split())
    # Styles intentionally differ; compare all text/title/desc nodes instead.
    def words(svg):
        return " ".join(" ".join(n.itertext()) for n in svg.iter()
                        if n.tag in {tag("text"), tag("title"), tag("desc")}).split()
    assert words(source) == words(out), target
    # Plotted points and bar dimensions remain byte-for-byte attribute values.
    old_points = [n.get("points") for n in source.iter(tag("polyline"))]
    new_points = [n.get("points") for n in out.iter(tag("polyline"))]
    assert old_points == new_points, target
    old_bars = [(n.get("width"), n.get("height"), n.get("fill"))
                for n in source.iter(tag("rect"))
                if n.get("fill") in {"#bd5939", "#247f79"}]
    new_bars = [(n.get("width"), n.get("height"), n.get("fill"))
                for n in out.iter(tag("rect"))
                if n.get("fill") in {"#bd5939", "#247f79"}]
    assert old_bars == new_bars, target
    # Inline type sizes make the exported SVG portable to PDF/SVG renderers
    # that do not implement CSS class selectors completely.
    for node in out.iter(tag("text")):
        node.set("font-size", str({"title": 26, "small": 20,
                                   "label": 22, "tick": 19}[node.get("class", "small")]))
        node.set("font-family", "Arial, Apple SD Gothic Neo, Malgun Gothic, sans-serif")
        node.set("fill", "#23333d")
        if node.get("class") == "title":
            node.set("font-weight", "700")
    ET.indent(out, space="  ")
    target.write_text(ET.tostring(out, encoding="unicode") + "\n")


def stacked_plots(path):
    source = ET.parse(path).getroot()
    nodes = list(source)
    out, after_header = new_root(source)
    left = next(i for i,n in enumerate(nodes)
                if n.tag == tag("rect") and n.get("x") == "110")
    right = next(i for i,n in enumerate(nodes)
                 if n.tag == tag("rect") and n.get("x") == "685")
    end = next(i for i,n in enumerate(nodes)
               if n.tag == tag("text") and n.get("x") == "628") + 1
    if "flat_band" in path.name:
        # The long +pi decimal labels are kept but aligned inside the canvas.
        for n in nodes[left:end]:
            if n.tag == tag("text") and n.get("class") == "tick" and n.get("x") in {"530.00", "1105.00"}:
                n.set("text-anchor", "end")
    # The 420px data rectangles stay intact, with identical axis scale.
    top = max(155, after_header + 24)
    plot_y = float(nodes[left].get("y"))
    dy_left = top - plot_y
    dy_right = dy_left + 465
    group(out, nodes[left:right], 35, dy_left, axis_x=26)
    group(out, nodes[right:end], -540, dy_right, axis_x=601)
    tail = nodes[end:]
    y = int(max(float(n.get("y", "0")) for n in nodes[right:end]
                if n.tag == tag("text")) + dy_right + 46)
    for n in tail:
        if n.tag == tag("line"):
            # Four product-formula legend entries become four rows.
            c = copy.deepcopy(n)
            c.set("x1", "44"); c.set("x2", "82")
            c.set("y1", str(y - 6)); c.set("y2", str(y - 6))
            out.append(c)
        elif n.tag == tag("text") and n.get("class") == "label" \
                and "product_formula" in path.name:
            y = text_lines(out, n.text, 98, y, "label", width=460,
                           size=22, leading=34)
        elif n.tag == tag("text"):
            y = text_lines(out, n.text, 30, y + 8, width=530,
                           size=22 if n.get("class") == "label" else 20,
                           cls=n.get("class", "small"), leading=30)
    target = path.with_name(path.stem.rsplit("_", 1)[0] + "_mobile_" +
                            path.stem.rsplit("_", 1)[1] + ".svg")
    finish(source, out, target, y + 18)


def stacked_bars(path):
    source = ET.parse(path).getroot()
    nodes = list(source)
    out, after_header = new_root(source)
    left = next(i for i,n in enumerate(nodes)
                if n.tag == tag("text") and n.get("x") == "82")
    right = next(i for i,n in enumerate(nodes)
                 if n.tag == tag("text") and n.get("x") == "647")
    end = next(i for i,n in enumerate(nodes)
               if n.tag == tag("rect") and n.get("x") == "80")
    y_heading = max(150, after_header + 22)
    text_lines(out, nodes[left].text, 52, y_heading, "label", width=500,
               size=22, leading=29)
    dy_left = y_heading - 119 + 28
    group(out, nodes[left+1:right], 20, dy_left)
    y_heading_right = y_heading + 430
    text_lines(out, nodes[right].text, 52, y_heading_right, "label", width=500,
               size=22, leading=29)
    group(out, nodes[right+1:end], -545, dy_left + 430)
    tail = nodes[end:]
    y = int(433 + dy_left + 430 + 48)
    for n in tail:
        if n.tag == tag("rect"):
            c = copy.deepcopy(n)
            c.set("x", "42"); c.set("y", str(y-18))
            out.append(c)
        elif n.tag == tag("text"):
            is_legend = n.get("y") == "471"
            y = text_lines(out, n.text, 76 if is_legend else 30, y,
                           width=490 if is_legend else 530, leading=30)
            y += 10 if is_legend else 12
    target = path.with_name(path.stem.rsplit("_", 1)[0] + "_mobile_" +
                            path.stem.rsplit("_", 1)[1] + ".svg")
    finish(source, out, target, y + 12)


def main():
    for lang in ("ko", "en"):
        for stem in ("product_formula_comparison", "flat_band_norm_counterexample"):
            stacked_plots(ROOT / "figures" / f"{stem}_{lang}.svg")
        stacked_bars(ROOT / "figures" / f"observable_sampling_comparison_{lang}.svg")
    print("Six mobile SVGs: identical words, curve points and bar dimensions.")


if __name__ == "__main__":
    main()
