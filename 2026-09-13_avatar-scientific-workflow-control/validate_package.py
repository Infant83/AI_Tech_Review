"""Publication checks; not an independent reproduction of Avatar."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from PIL import Image

P=Path(__file__).resolve().parent
ROOT=P.parent
sys.path.insert(0,str(ROOT/'scripts'))
import publish_public_site as pub
import markdown_to_html as render

manifest=json.loads((ROOT/'site/manifest.json').read_text())
errors=pub.validate_public_site(manifest)
entry=next(x for x in manifest if x['folder']==P.name)
assert len(manifest)==28
assert entry['category']=='Agent Systems'
expected_thumb=f'reviews/{P.name}/avatar_control_hero.webp'
assert entry['thumbnail']==expected_thumb
hero=Image.open(P/'artifacts/avatar_control_hero.webp')
assert hero.size==(1600,900),hero.size
assert not hero.getexif()
assert not hero.info.get('xmp')
descriptions={}
external=set()
for lang,suffix in [('ko',''),('en','_en')]:
    md=P/'reports'/f'{P.name}_final_review{suffix}.md'
    metadata,_=render.strip_frontmatter(md.read_text())
    desc=render.metadata_value(metadata,'description')
    descriptions[lang]=len(desc)
    if not 150<=len(desc)<=160:
        errors.append(f'{lang} description length {len(desc)} is outside 150–160')
    public=ROOT/'site/reviews'/P.name/('en/index.html' if lang=='en' else 'index.html')
    soup=BeautifulSoup(public.read_text(),'html.parser')
    assert soup.html['lang']==lang
    assert soup.h1.get_text()==soup.title.get_text()
    assert soup.find('meta',property='og:title')['content']==soup.h1.get_text()
    assert soup.find('meta',attrs={'name':'description'})['content']==desc
    assert set(x['hreflang'] for x in soup.select('link[hreflang]'))=={'ko','en','x-default'}
    for img in soup.select('article img'):
        assert img.get('alt')
        assert (public.parent/img['src']).is_file()
    for table in soup.select('article table'):
        counts=[len(r.find_all(['td','th'],recursive=False)) for r in table.select('tr')]
        assert len(set(counts))==1,counts
    for a in soup.select('a[href]'):
        if a['href'].startswith('https:'):
            external.add(a['href'])
    for text in ['5,000','100','32','12','7','40','21','99','55','0.35','1/3','0.2','0.5.0','2026.3.9']:
        assert text in md.read_text(),(lang,text)
    assert 'QM9' in md.read_text() and 'DFT' in md.read_text()
    assert 'C_{\\mathrm{wrong}}' in md.read_text()
    assets=list(public.parent.iterdir())
    assert not any(x.suffix in {'.md','.json','.py'} for x in assets)

hub=BeautifulSoup((ROOT/'site/index.html').read_text(),'html.parser')
cards=hub.select('.review-card')
assert len(cards)==28,len(cards)
for item in manifest:
    card=next(c for c in cards if c.find('a',href=item['href']))
    assert card.find('img')['src']==item['thumbnail'],item['folder']
    assert (ROOT/'site'/item['thumbnail']).is_file()
old=json.loads(subprocess.check_output(['git','show','c036d5efe539fcf7f0b1b9bc3888589713a297dd:site/manifest.json'],cwd=ROOT))
for item in old:
    current=next(x for x in manifest if x['folder']==item['folder'])
    assert current==item,f'existing manifest entry changed: {item["folder"]}'
assert abs(5/12*100-41.66666666666667)<1e-10
result={'checks':'public site, bilingual metadata, body tables, images, preserved manifest, 28 hub cards, protected numeric tokens, round arithmetic',
        'description_lengths':descriptions,'external_reference_urls':sorted(external),'errors':errors,
        'hero_sha256':hashlib.sha256((P/'artifacts/avatar_control_hero.webp').read_bytes()).hexdigest(),
        'scientific_reproduction':False,'human_line_review':False}
(P/'notes/package_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
