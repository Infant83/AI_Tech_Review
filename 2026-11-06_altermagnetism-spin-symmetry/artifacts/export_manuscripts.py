"""Export bilingual manuscripts with shared APS references in first-use order."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
sources = json.loads((ROOT/'artifacts/reference-sources.json').read_text())
lookup = {item['key']:item for item in sources['references']}
texts = {lang:(ROOT/'artifacts/manuscripts'/f'review_{lang}.md').read_text() for lang in ['ko','en']}
sequences = {lang:re.findall(r'\[@([^\]]+)\]',text) for lang,text in texts.items()}
assert sequences['ko'] == sequences['en'], 'Bilingual citation order differs.'
order = list(dict.fromkeys(sequences['ko']))
assert set(order) <= set(lookup), set(order)-set(lookup)
manifest = []
entries = []
for number,key in enumerate(order,1):
    item = {**lookup[key], 'number':number}
    citation = item['aps_citation']
    title = item['title_aps']
    assert title in citation, key
    citation = citation.replace(title,f'[{title}]({item["url"]})',1)
    entries.append(f'{number}. {citation}')
    manifest.append(item)
numbers = {key:str(index+1) for index,key in enumerate(order)}
for lang,text in texts.items():
    text = re.sub(r'\[@([^\]]+)\]',lambda match:'['+numbers[match[1]]+']',text)
    assert '<!-- REFERENCES_INSERT -->' in text
    text = text.replace('<!-- REFERENCES_INSERT -->','\n\n'.join(entries))
    (ROOT/'reports'/f'review_{lang}.md').write_text(text.rstrip()+'\n')
(ROOT/'artifacts/reference-manifest.json').write_text(json.dumps({'checked_on':'2026-11-06','style':'APS numbered references; shared Korean and English order','references':manifest},ensure_ascii=False,indent=2)+'\n')
print(f'Exported two manuscripts with {len(order)} shared references.')
