"""Verify the actual bilingual review package and PDF annotations before handoff."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
from pypdf import PdfReader
from PIL import Image
import hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.hrefs=[];self.images=[];self.meta={};self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.hrefs.append(a['href'])
        if tag=='img':self.images.append(a)
        if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    results=[]
    for lang,directory,pdfname in [('ko',ROOT/'dist','review.pdf'),('en',ROOT/'dist/en','review-en.pdf')]:
        html=(directory/'index.html').read_text()
        doc=Document();doc.feed(html)
        assert doc.lang==lang
        assert doc.meta['robots']==('index,follow' if '--public' in sys.argv else 'noindex,nofollow')
        if '--public' in sys.argv:assert not re.search(r'로컬 검토본|local review version|REVIEW COPY',html)
        assert len(doc.ids)==len(set(doc.ids))
        assert 'authoring-disclosure' in doc.ids
        assert all(f'ref-{i}' in doc.ids for i in range(1,20))
        for href in doc.hrefs:
            if href.startswith('#'):assert href[1:] in doc.ids,href
            elif not urlparse(href).scheme:assert (directory/unquote(href)).exists(),href
        assert doc.images[0]['src']=='hero.webp'
        for im in doc.images:
            assert im.get('alt')
            assert (directory/im['src']).is_file()
        assert not re.search(r'/(?:Users|home)/|file:/[/][/]|localhost|127[.]0[.]0[.]1|PRIVATE KEY',html)
        for f in directory.rglob('*'):
            if directory==ROOT/'dist' and 'en' in f.relative_to(directory).parts:continue
            if f.is_dir():continue
            assert f.suffix in ['.html','.css','.webp','.svg','.pdf'],f
            assert not any(p in f.parts for p in ['notes','tmp'])
            if f.suffix in ['.html','.css','.svg']:
                text=f.read_text()
                assert not re.search(r'/(?:Users|home)/|file:/[/][/]|localhost|127[.]0[.]0[.]1',text),f
        reader=PdfReader(directory/pdfname)
        assert not reader.is_encrypted
        assert not reader.attachments
        alltext='\n'.join(p.extract_text() or '' for p in reader.pages)
        assert len(alltext)>5000 and '\ufffd' not in alltext
        assert not re.search(r'/(?:Users|home)/|file:/[/][/]|localhost|127[.]0[.]0[.]1',alltext)
        for p in reader.pages:
            assert abs(float(p.mediabox.width)-595.28)<2
            assert abs(float(p.mediabox.height)-841.89)<2
            for ref in p.get('/Annots',[]):
                annotation=ref.get_object();action=annotation.get('/A')
                if action:
                    action=action.get_object()
                    uri=str(action.get('/URI',''))
                    assert not uri.startswith(('file:','http://127.0.0.1'))
                    assert action.get('/S')!='/GoToR'
        results.append({'language':lang,'pdf_pages':len(reader.pages),'images':len(doc.images),
                        'references':19,'pdf_sha256':sha(directory/pdfname),'html_sha256':sha(directory/'index.html')})
    with Image.open(ROOT/'dist/hero.webp') as im:
        assert im.size==(1600,900)
        assert not im.getexif()
        assert not any(k in im.info for k in ['exif','xmp'])
    assert sha(ROOT/'dist/hero.webp')==sha(ROOT/'dist/en/hero.webp')
    output={'status':'passed','independent_replication':False,'results':results}
    (ROOT/'tmp'/'package-checks.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False))

if __name__=='__main__':verify()
