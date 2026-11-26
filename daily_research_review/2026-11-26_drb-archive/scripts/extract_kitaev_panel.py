"""Extract CC BY4.0 author-manuscript Fig.3h-j; no data redrawing."""
from pathlib import Path
import argparse
import fitz
p=argparse.ArgumentParser()
p.add_argument('source',type=Path,help='arXiv2607.09511v2 PDF, SHA25660a056a9b8e00f38e5903792b53e12fc9d5b531e44e9249572a536042411275f')
a=p.parse_args()
out=Path(__file__).resolve().parents[1]/'artifacts/kitaev-v2-fig3hij.png'
with fitz.open(a.source) as d:
    d[6].get_pixmap(matrix=fitz.Matrix(3.2,3.2),clip=fitz.Rect(66,256,521,389)).save(out)
print(out.name)
