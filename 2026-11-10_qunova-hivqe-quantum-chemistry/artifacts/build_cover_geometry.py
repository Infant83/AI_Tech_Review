"""Draw a verified Fe4S4 core reference for a conceptual editorial cover.

RCSB CCD SF4 supplies the atom identities, ideal reference coordinates and
coordination graph. The rendered reference is not the geometry of the Qunova
benchmark and does not encode its charge, spin state or electronic solution.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import shlex
from urllib.request import urlopen

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://files.rcsb.org/ligands/view/SF4.cif"
EXPECTED_SOURCE_SHA256 = "c15afc27c7405e2ccd1fefe50e92e38360ea63ba43a443b5ceccb1d1f7a3db48"


def cif_loop(text, prefix):
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if line.strip() != "loop_":
            continue
        tags, tokens = [], []
        index = start + 1
        while index < len(lines) and lines[index].lstrip().startswith("_"):
            tags.append(lines[index].strip())
            index += 1
        if not tags or not tags[0].startswith(prefix):
            continue
        while index < len(lines):
            current = lines[index].strip()
            if current == "#" or current == "loop_" or current.startswith("_"):
                break
            tokens.extend(shlex.split(current))
            index += 1
        assert len(tokens) % len(tags) == 0
        return [dict(zip(tags, tokens[i:i + len(tags)]))
                for i in range(0, len(tokens), len(tags))]
    raise ValueError("Missing CCD table: " + prefix)


def rotation(rx, ry, rz):
    a, b, c = np.radians([rx, ry, rz])
    cx, sx, cy, sy, cz, sz = math.cos(a), math.sin(a), math.cos(b), math.sin(b), math.cos(c), math.sin(c)
    return np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])


def distance_to_segment(point, a, b):
    t = np.clip(np.dot(point-a, b-a) / np.dot(b-a, b-a), 0, 1)
    return np.linalg.norm(point-(a+t*(b-a)))


def main():
    raw = urlopen(SOURCE_URL, timeout=30).read()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise ValueError("CCD source changed; review the source revision before regenerating this reference.")
    text = raw.decode("utf-8")
    atom_rows = cif_loop(text, "_chem_comp_atom.")
    bond_rows = cif_loop(text, "_chem_comp_bond.")
    atoms = [{"id": r["_chem_comp_atom.atom_id"],
              "element": r["_chem_comp_atom.type_symbol"],
              "ideal_ccd_xyz": [float(r[f"_chem_comp_atom.pdbx_model_Cartn_{a}_ideal"]) for a in "xyz"]}
             for r in atom_rows]
    edges = [[r["_chem_comp_bond.atom_id_1"], r["_chem_comp_bond.atom_id_2"]] for r in bond_rows]
    lookup = {a["id"]: i for i, a in enumerate(atoms)}
    assert len(atoms) == 8 and len(edges) == 12
    assert sum(a["element"] == "FE" for a in atoms) == 4
    assert sum(a["element"] == "S" for a in atoms) == 4
    degrees = dict.fromkeys(lookup, 0)
    for a, b in edges:
        assert {atoms[lookup[a]]["element"], atoms[lookup[b]]["element"]} == {"FE", "S"}
        degrees[a] += 1
        degrees[b] += 1
    assert set(degrees.values()) == {3}
    pairs = [(lookup[a], lookup[b]) for a, b in edges]
    xyz = np.array([a["ideal_ccd_xyz"] for a in atoms])
    xyz -= xyz.mean(axis=0)
    # Rotation alone preserves the source geometry. Select a readable view by
    # spacing nodes away from other nodes and nonincident projected edges.
    best = None
    for rx, ry in itertools.product(range(-60, 91, 15), range(-60, 91, 15)):
        rotated = xyz @ rotation(rx, ry, -8).T
        projected = rotated[:, :2]
        span = np.ptp(projected, axis=0)
        projected *= 378 / max(span)
        separation = min(np.linalg.norm(projected[i]-projected[j]) for i, j in itertools.combinations(range(8), 2))
        clearance = min(distance_to_segment(projected[k], projected[i], projected[j]) for i, j in pairs for k in range(8) if k not in (i, j))
        score = separation + 0.9*clearance - 25*abs(math.log(span[0]/span[1]))
        if best is None or score > best[0]:
            best = score, rx, ry, projected, rotated[:, 2]
    _, rx, ry, projected, depths = best
    projected[:, 1] *= -1
    projected += np.array([980, 450]) - (projected.max(axis=0)+projected.min(axis=0))/2
    for atom, xy, depth in zip(atoms, projected, depths):
        atom["canvas_xy"] = [round(float(x), 3) for x in xy]
        atom["camera_depth"] = round(float(depth), 6)
    radius = 34
    box = [float(projected[:, 0].min()-radius), float(projected[:, 1].min()-radius), float(projected[:, 0].max()+radius), float(projected[:, 1].max()+radius)]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">',
           '<title id="title">Fe4S4 cubane-core geometry reference</title>',
           '<desc id="desc">Four iron and four bridging sulfur vertices joined by twelve Fe-S coordination edges. Paper and textile rendering is conceptual. Peripheral ligands are omitted.</desc>',
           '<defs><pattern id="fe-hatch" width="9" height="9" patternUnits="userSpaceOnUse"><path d="M1 0V9M5 0V9" stroke="#f7e4d6" stroke-width=".7" opacity=".24"/></pattern><pattern id="s-hatch" width="9" height="9" patternUnits="userSpaceOnUse"><path d="M-3 9L9-3M0 12L12 0" stroke="#fff2cc" stroke-width=".7" opacity=".3"/></pattern></defs>',
           '<rect width="1600" height="900" fill="#faf6ec"/>']
    for i, j in sorted(pairs, key=lambda pair: float((depths[pair[0]]+depths[pair[1]])/2)):
        x1, y1 = projected[i]
        x2, y2 = projected[j]
        svg += [f'<path d="M{x1:.3f},{y1:.3f}L{x2:.3f},{y2:.3f}" fill="none" stroke="#b6a58e" stroke-width="9" stroke-linecap="round"/>',
                f'<path d="M{x1:.3f},{y1:.3f}L{x2:.3f},{y2:.3f}" fill="none" stroke="#6e665d" stroke-width="1.4" stroke-linecap="round" opacity=".65"/>']
    for index in sorted(range(8), key=lambda i: float(depths[i])):
        atom = atoms[index]
        x, y = projected[index]
        fill = "#b96759" if atom["element"] == "FE" else "#d5aa58"
        hatch = "fe-hatch" if atom["element"] == "FE" else "s-hatch"
        svg += [f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius}" fill="{fill}" stroke="#75695c" stroke-width="1.6"/>',
                f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius-1}" fill="url(#{hatch})"/>',
                f'<path d="M{x-19:.3f},{y-24:.3f}Q{x-3:.3f},{y-32:.3f} {x+15:.3f},{y-25:.3f}" fill="none" stroke="#fff6e5" stroke-width="1.5" opacity=".35"/>']
    svg.append('</svg>')
    (ROOT/'cover_geometry.svg').write_text("\n".join(svg)+'\n')
    result = {
        "kind": "verified source-geometry reference for conceptual cover",
        "source_url": SOURCE_URL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_coordinate_fields": "_chem_comp_atom.pdbx_model_Cartn_[xyz]_ideal",
        "component": "SF4", "source_geometry_not_qunova_benchmark_geometry": True,
        "atom_count": 8, "element_counts": {"Fe":4,"S":4}, "edge_count":12,
        "coordination_edges":edges, "degree_by_atom":degrees, "atoms":atoms,
        "canvas":{"width":1600,"height":900,"core_center":[980,450],"core_bbox_including_nodes":box,"atom_radius":radius,"camera_rotation_degrees":[rx,ry,-8]},
        "visual_scope":["Fe4S4 core only; peripheral ligands omitted.","No oxidation or spin assignments are encoded.","No labels or fabricated quantitative results appear in the image.","Candidate selection in HI-VQE acts on electronic configurations, not atoms or core bonds."],
        "checks_passed":["Four Fe and four S atoms","Twelve exclusively Fe-S coordination edges","All core degrees equal three","No atom/bond dropped during projection","Uniform scaling and 3D rotation preserve reference geometry"]
    }
    (ROOT/'cover_geometry.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'source_sha256':result['source_sha256'],'core_bbox':box,'camera':[rx,ry,-8],'atoms':8,'edges':12}))


if __name__ == '__main__':
    main()
