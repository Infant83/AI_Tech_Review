#!/usr/bin/env python3
"""Extract specified panels from the two reviewed CC BY 4.0 AIP PDFs.

Inputs remain local; only selected, attributed crops are publication assets.
No resampling of the plotted data, curve reconstruction or content edits.
"""
from pathlib import Path
import argparse, hashlib, json
import fitz

p=argparse.ArgumentParser()
p.add_argument('--qsut',type=Path,required=True)
p.add_argument('--sripe',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
specs=[
 (a.qsut,'b42fe9964961272518633f26b10bb190855b514ed671503c4462ea5ccfa8c540',10,(210,42,566,222),'qsut-fig6.png','10.1038/s41534-026-01420-x','Fig.6(a,b)'),
 (a.sripe,'6c2ac65a9b45caeacf3d1320ef73902966b83e95356288bc5e4ff78995a1ebfa',3,(37,44,535,216),'sripe-fig3.png','10.1038/s41534-026-01413-w','Fig.3(a,b)')
]
rows=[]
for src,sha,page,box,name,doi,panel in specs:
 assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
 doc=fitz.open(src);doc[page].get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(box),alpha=False).save(a.output/name)
 rows.append({'asset':name,'doi':doi,'panel':panel,'pdf_page':page+1,'pdf_sha256':sha,'crop_points':list(box),'scale':4,'asset_sha256':hashlib.sha256((a.output/name).read_bytes()).hexdigest(),'version':'Article in Press, 27 November 2026','license':'https://creativecommons.org/licenses/by/4.0/','credit':'The Author(s) 2026','modification':'Graph/device regions cropped; original caption replaced by an attributed Korean explanation. Axes, marks and legends retained; no data altered.','third_party_credit':'No separate third-party credit observed for these selected panels in the source and article rights notice.'})
(a.output/'source-figure-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'selected_panels':len(rows)}))
