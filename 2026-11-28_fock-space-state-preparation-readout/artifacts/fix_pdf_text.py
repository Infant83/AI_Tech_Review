"""Repair Chrome's null Unicode mappings for proven GSUB variants only.

The browser keeps the right outlines but may emit U+0000 for CJK proportional
punctuation/space and Latin ligatures. Recover characters from the exact bundled
font's GSUB table, check embedded outlines, and require pixel-identical pages.
No page content stream, layout, or font outline is modified.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import tempfile
from PIL import Image
import fitz
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'

def sha(data): return hashlib.sha256(data).hexdigest()

def glyph_text(font):
    mapping = {}
    for cp, glyph in font.getBestCmap().items():
        mapping.setdefault(glyph, set()).add(chr(cp))
    # U+0020 and U+00A0 share the same outline; rendered SVG spaces are U+0020.
    if 'space' in mapping: mapping['space'] = {' '}
    tables=[]
    for lookup in font['GSUB'].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            tables.append(getattr(sub, 'ExtSubTable', sub))
    for _ in range(4):
        for sub in tables:
            for source, target in getattr(sub, 'mapping', {}).items():
                if source in mapping: mapping.setdefault(target,set()).update(mapping[source])
            for first, ligatures in getattr(sub, 'ligatures', {}).items():
                for lig in ligatures:
                    components=[first]+list(lig.Component)
                    if all(len(mapping.get(g,set()))==1 for g in components):
                        value=''.join(next(iter(mapping[g])) for g in components)
                        mapping.setdefault(lig.LigGlyph,set()).add(value)
    return mapping

def glyph_signature(font, name):
    g=font['glyf'][name]
    coords, ends, flags=g.getCoordinates(font['glyf'])
    return (g.numberOfContours, tuple(coords), tuple(ends), tuple(flags), font['hmtx'][name])

def render_hashes(doc):
    return [sha(p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).samples) for p in doc]

def poppler_hashes(path):
    with tempfile.TemporaryDirectory(prefix='atrl-quantum-poppler-') as temp:
        stem=Path(temp)/'page'
        subprocess.run(['pdftoppm','-r','72','-png',str(path),str(stem)],check=True,capture_output=True)
        return [sha(Image.open(p).convert('RGB').tobytes()) for p in sorted(Path(temp).glob('page-*.png'))]

def repair(path):
    before_bytes=path.read_bytes(); tmp=path.with_suffix('.text-fixed.pdf'); tmp.write_bytes(before_bytes)
    doc=fitz.open(tmp)
    before_pixels=render_hashes(doc); before_poppler=poppler_hashes(path); seen=set(); changes=[]
    for page in doc:
        for entry in page.get_fonts(full=True):
            xref=entry[0]
            if xref in seen: continue
            seen.add(xref)
            obj=doc.xref_object(xref); tu=re.search(r'/ToUnicode (\d+) 0 R',obj)
            if not tu: continue
            stream_xref=int(tu[1]); stream=doc.xref_stream(stream_xref).decode('ascii')
            nulls=re.findall(r'<([0-9A-Fa-f]+)>\s*<0000>',stream)
            if not nulls: continue
            if 'ATRLQuantumReviewSansSubset' not in entry[3]:
                raise ValueError('Unexpected null mapping outside the bundled font')
            descendant=re.search(r'/DescendantFonts\s*\[\s*(\d+) 0 R',obj)
            if not descendant or '/CIDToGIDMap /Identity' not in doc.xref_object(int(descendant[1])):
                raise ValueError('A non-identity glyph map requires separate inspection')
            weight='bold' if 'Bold' in entry[3] else 'regular'
            source=TTFont(ART/f'review-{weight}.woff2'); mapping=glyph_text(source)
            embedded=TTFont(io.BytesIO(doc.extract_font(xref)[3])); order=source.getGlyphOrder()
            for cid in nulls:
                gid=int(cid,16); name=order[gid]; values=mapping.get(name,set())
                if len(values)!=1: raise ValueError(f'Unproven character for {weight}/{gid}: {values}')
                if glyph_signature(source,name)!=glyph_signature(embedded,embedded.getGlyphOrder()[gid]):
                    raise ValueError(f'Outline/advance changed for glyph {gid}')
                text=next(iter(values)); dest=text.encode('utf-16-be').hex().upper()
                stream=re.sub(r'<'+cid+r'>\s*<0000>',f'<{cid}> <{dest}>',stream)
                changes.append({'font_xref':xref,'weight':weight,'cid_hex':cid,'recovered_text':text,'source':'bundled-font GSUB','empty_outline':source['glyf'][name].numberOfContours==0})
            doc.update_stream(stream_xref,stream.encode('ascii'))
    doc.saveIncr(); doc.close()
    final=fitz.open(tmp); after_pixels=render_hashes(final); after_poppler=poppler_hashes(tmp)
    if before_pixels!=after_pixels or before_poppler!=after_poppler:
        tmp.unlink(); raise AssertionError('Text repair changed a rendered page')
    text='\n'.join(p.get_text() for p in final); pages=len(final); final.close()
    tmp.replace(path)
    return {'file':path.relative_to(ROOT).as_posix(),'pages':pages,'before_sha256':sha(before_bytes),'after_sha256':sha(path.read_bytes()),'changes':changes,'all_pages_pixel_identical':True,'poppler_all_pages_pixel_identical':True,'poppler_page_pixel_sha256':after_poppler,'render_scale':1.5,'page_pixel_sha256':after_pixels,'null_characters_after':text.count('\x00'),'replacement_characters_after':text.count('\ufffd')}

if __name__=='__main__':
    results=[repair(ROOT/'dist/review_ko.pdf'),repair(ROOT/'dist/en/review_en.pdf')]
    (ART/'publication-text-layer-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'file':r['file'],'pages':r['pages'],'sha256':r['after_sha256'],'repaired_mappings':len(r['changes']),'all_pages_pixel_identical':r['all_pages_pixel_identical']} for r in results],ensure_ascii=False))
