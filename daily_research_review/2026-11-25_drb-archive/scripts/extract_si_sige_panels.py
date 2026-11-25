"""Excerpt unchanged Fig.4(a,b) of Zhang et al., arXiv:2605.31342v1.

Source image carries the author manuscript's CC BY 4.0 license. The final
journal article is DOI10.1103/qbss-wkz7. No numerical reconstruction occurs.
"""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
expected='85addceed1b2708f10311debdb87a6c4d5226ed18d81b2c21d537ab97986a301'
assert hashlib.sha256(a.source.read_bytes()).hexdigest()==expected
im=Image.open(a.source)
assert im.size==(6601,1585)
box=(0,0,3570,1585)
out=im.crop(box)
# Remove only neighboring panel(c) left tick labels above panel(b) x labels.
# Panel(b) border, data, native lower-right x tick and Nat. label remain.
ImageDraw.Draw(out).rectangle((3490,0,3569,1320),fill="white")
a.output.parent.mkdir(parents=True,exist_ok=True)
out.save(a.output)
print(json.dumps({'asset':a.output.name,'source_sha256':expected,'crop_pixels':box,'pixels':out.size,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'license':'CC BY4.0','source':'https://arxiv.org/html/2605.31342v1/figure4-v6.jpg','figure':'Fig.4(a,b)','changes':'Left two panels only; neighboring panel(c) y tick labels in rectangle(3490,0,3569,1320) cleared to white, native panel(b) axes/points/curves/colorbar/legend and lower-right x tick preserved.'}))
