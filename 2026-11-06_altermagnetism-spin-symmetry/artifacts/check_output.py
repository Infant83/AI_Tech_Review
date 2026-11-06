"""Check review assets, citation parity, publication metadata and PDF annotations."""
import argparse
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--public-base', default='')
args = parser.parse_args()
public_base = args.public_base.rstrip('/') + '/' if args.public_base else ''
records=[]
references=json.loads((ROOT/'artifacts/reference-manifest.json').read_text())['references']
numbered=list(range(1,len(references)+1))
maths={}
for lang in ['ko','en']:
    manuscript=(ROOT/'reports'/f'review_{lang}.md').read_text()
    heading='## 참고문헌' if lang=='ko' else '## References'
    body,bibliography=manuscript.split(heading,1)
    ordered=list(dict.fromkeys(map(int,re.findall(r'\[(\d+)\]',body))))
    assert ordered==numbered, (lang,ordered)
    assert list(map(int,re.findall(r'^(\d+)\. ',bibliography,re.M)))==numbered
    assert not re.search(r'REFERENCES_INSERT|\[@|TODO|FIXME',manuscript)
    maths[lang]=Counter(re.findall(r'\\\((.*?)\\\)|\$\$([\s\S]*?)\$\$',body))
    folder=ROOT/'dist'/('' if lang=='ko' else 'en')
    document=(folder/'index.html').read_text()
    if public_base:
        url = public_base + ('' if lang == 'ko' else 'en/')
        assert f'<link rel="canonical" href="{url}">' in document
        assert f'hreflang="ko" href="{public_base}"' in document
        assert f'hreflang="en" href="{public_base}en/"' in document
        assert f'property="og:image" content="{public_base}hero.webp"' in document
        assert '로컬 검토본' not in document and 'Local review copy' not in document
    else:
        assert '로컬 검토본' in document if lang=='ko' else 'Local review copy' in document
    assert 'id="authoring-disclosure"' in document
    assert sorted(map(int,re.findall(r'id="ref-(\d+)"',document)))==numbered
    assert not re.search(r'/Users/|file://|data-mjx-error|<merror|MATHBLOCK\d+END|\*\*',document)
    assets=set(re.findall(r'\bsrc="([^"#]+)"',document))
    for target in assets:
        assert not urlsplit(target).scheme, target
        assert (folder/unquote(target)).is_file(), target
    for target in re.findall(r'\bhref="([^"]+)"',document):
        split=urlsplit(target)
        if not split.scheme and split.path:
            assert (folder/unquote(split.path)).is_file(), (lang,target)
        if not split.path and split.fragment:
            assert f'id="{split.fragment}"' in document, (lang,target)
    pdf=folder/f'review_{lang}.pdf'
    reader=PdfReader(pdf)
    assert len(reader.pages)>0
    for page in reader.pages:
        text=page.extract_text()
        assert not re.search(r'/Users/|file://|MATHBLOCK|REFERENCES_INSERT',text)
        for annotation in page.get('/Annots',[]):
            action=annotation.get_object().get('/A')
            if action and action.get('/URI'):
                assert str(action['/URI']).startswith(('https://','http://','mailto:')), action
    records.append({'language':lang,'pages':len(reader.pages),'references':len(numbered),'local_assets':len(assets),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'html_sha256':hashlib.sha256((folder/'index.html').read_bytes()).hexdigest(),'status':'pass'})
assert maths['ko']==maths['en'], 'Bilingual equation multiset differs.'
payload={'date':'2026-11-06','publication_state':'Public-ready output' if public_base else 'Local review copy','public_base':public_base,'records':records,'math_expression_parity':'pass','scope':'Structural checks; visual and scientific reviews recorded separately.'}
(ROOT/'artifacts/output-validation.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(payload,ensure_ascii=False,indent=2))
