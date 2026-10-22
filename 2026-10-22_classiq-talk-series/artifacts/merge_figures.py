"""Build the explicit reading-copy figure allowlist from reviewed source fragments."""
from pathlib import Path
import hashlib
import json
import re

root=Path(__file__).resolve().parents[1]
fragments=['figures/concepts/manifest.json','figures/screens/platform-manifest.json','figures/screens/finance-manifest.json']
captions={}
for md in [root/'README.md',root/'technical-companion.md',*(root/'sessions').glob('*.md')]:
    for match in re.finditer(r'!\[([^\]]+)\]\(([^)]+)\)\s*\n\s*그림 (\d+-\d+)\. ([^\n]+)',md.read_text()):
        alt,relative,number,caption=match.groups()
        asset=(md.parent/relative).resolve().relative_to(root).as_posix()
        if asset in captions:
            raise ValueError('Figure repeated in manuscript '+asset)
        captions[asset]={'number':number,'alt':alt,'caption':caption,'chapter':md.relative_to(root).as_posix()}
figures=[]
for name in fragments:
    part=json.loads((root/name).read_text())
    for item in part['figures']:
        relative=item['file']
        if not re.fullmatch(r'figures/(concepts|screens)/[a-z0-9-]+\.(svg|png)',relative):
            raise ValueError('Unexpected figure path '+relative)
        item=dict(item)
        item.pop('png',None)
        item.pop('optional',None)
        if relative not in captions:
            raise ValueError('Figure has no final caption '+relative)
        item.update(captions[relative])
        item.pop('insertion_anchor',None)
        item['sha256']=hashlib.sha256((root/relative).read_bytes()).hexdigest()
        figures.append(item)
if len({x['file'] for x in figures})!=len(figures):
    raise ValueError('Duplicate figure file')
manifest={'edition':'1.1','scope':'Selected official replay excerpts and independently authored teaching diagrams','figures':figures}
serial=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
if re.search(r'/Users/|file://|token=',serial):
    raise ValueError('Private source detail in final manifest')
(root/'figures/manifest.json').write_text(serial)
print(json.dumps({'figures':len(figures),'screens':sum(x['kind']=='replay-frame' for x in figures)},ensure_ascii=False))
