"""Extract unchanged source panels from the publisher’s public PNG.

Not executed by the research agent. The publication owner runs this serially
inside the permitted load window. No paper/model/data calculation is performed.
Source: Thomas, Chabaud and Emeriau, PRX Quantum 7, 043038 (2026),
DOI10.1103/d6k4-4xrz, Fig.3 (CC BY4.0).
"""
from pathlib import Path
import argparse
import hashlib
from PIL import Image

p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--input",type=Path,required=True)
p.add_argument("--output",type=Path,required=True)
p.add_argument("--mode",choices=["energy-outer-pair","energy-full-a"],default="energy-outer-pair")
a=p.parse_args()
expected="7791d557d8c3cab454d5ec89c46ed0c342a1e802546aab43af3300a56fcab44a"
if hashlib.sha256(a.input.read_bytes()).hexdigest()!=expected:
    raise SystemExit("Source image differs from the reviewed publisher Fig.3 PNG")
im=Image.open(a.input).convert("RGB")
if im.size!=(1600,831):
    raise SystemExit(f"Unexpected source size: {im.size}")
if a.mode=="energy-full-a":
    out=im.crop((0,0,1600,375))
else:
    # First and fourth native subplots of Fig.3(a). Native titles, axes and
    # legends are retained; the omitted middle cases are declared in caption.
    left=im.crop((0,0,400,325))
    right=im.crop((1200,0,1600,325))
    out=Image.new("RGB",(824,325),"white")
    out.paste(left,(0,0));out.paste(right,(424,0))
a.output.parent.mkdir(parents=True,exist_ok=True)
out.save(a.output)
print(f"Saved unchanged source-panel crop: {a.output}")
