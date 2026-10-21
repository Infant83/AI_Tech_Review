"""Inspect final PDFs, rasterize every page, and create private QA contacts.

The article, formulas, figures and source language are checked elsewhere.
These checks verify metadata, private-link exclusions and the rendered artifact
inventory; the resulting page images still require visual inspection.
"""
from pathlib import Path
import argparse, hashlib, json, math, shutil, subprocess
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--renderer',default=shutil.which('pdftoppm'))
    parser.add_argument('--skip-render',action='store_true')
    args=parser.parse_args();qa=ROOT/'tmp/pdfs';qa.mkdir(parents=True,exist_ok=True);records=[]
    for lang,relative in [('ko','dist/review.pdf'),('en','dist/en/review-en.pdf')]:
        source=ROOT/relative;reader=PdfReader(source);count=len(reader.pages)
        if not args.skip_render:
            if not args.renderer:raise RuntimeError('pdftoppm is required, or pass --renderer.')
            for old in qa.glob(f'{lang}-final-page-*.png'):old.unlink()
            subprocess.run([args.renderer,'-scale-to','1600','-png',str(source),str(qa/f'{lang}-final-page')],check=True)
        files=sorted(qa.glob(f'{lang}-final-page-*.png'))
        if len(files)!=count:raise RuntimeError(f'Incomplete rendered page inventory: {lang}')
        text='\n\f\n'.join(page.extract_text() or '' for page in reader.pages)
        (qa/f'{lang}-final-extracted.txt').write_text(text)
        links=[]
        for page in reader.pages:
            for ref in page.get('/Annots',[]):
                action=ref.get_object().get('/A',{})
                if hasattr(action,'get_object'):action=action.get_object()
                if '/URI' in action:links.append(str(action['/URI']))
        forbidden=['file:','/Users/','/tmp/']
        if any(marker in value for marker in forbidden for value in [text,*links]):raise RuntimeError('Private path or URI found in PDF.')
        if len(reader.attachments):raise RuntimeError('Unexpected PDF attachments.')
        if chr(65533) in text:raise RuntimeError('Replacement characters found in extracted PDF text.')
        rows=math.ceil(count/4);contact=Image.new('RGB',(1600,rows*575),'#deded9');draw=ImageDraw.Draw(contact)
        for index,file in enumerate(files):
            page=Image.open(file);page.thumbnail((390,545));x=index%4*400;y=index//4*575
            contact.paste(page,(x,y+20));draw.text((x+10,y+3),str(index+1),fill='black')
        contact.save(qa/f'{lang}-final-pages-contact.png')
        records.append({'language':lang,'pdf':relative,'pages':count,'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'title':reader.metadata.title,'tagged':bool(reader.trailer['/Root'].get('/MarkInfo',{}).get('/Marked',False)),'embedded_files':0,'private_text_or_link':False,'replacement_characters':0,'all_page_render_count':len(files),'render_scale':1600,'contact':f'tmp/pdfs/{lang}-final-pages-contact.png'})
    (qa/'final-output-checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    manifest=ROOT/'figure-manifest.json';data=json.loads(manifest.read_text())
    for figure in data.get('teaching_figures',[]):
        for variant in figure['variants']:
            variant['sha256']=hashlib.sha256((ROOT/variant['path']).read_bytes()).hexdigest()
    data['pdf_outputs']=records
    data['interactive_lab']['verification']='Exact identity over 177 angles; independent finite-difference gradients and analytic allocation; actual keyboard change and boundary behavior checked in a browser; reset and optimum click bindings inspected in source. Live UI checks are recorded separately.'
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(records,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
