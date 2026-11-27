# -*- coding: utf-8 -*-
"""Build the revised Korean lecture with XeLaTeX and original vector figures.

Run only at an authorized serial compile/render stage. The body, edition
metadata and fixed model disclosure are explicit reviewed inputs. Intermediates
and page images stay private; the existing v2 PDF cannot be overwritten here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import fitz

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parents[1]
REPO = TOPIC.parent
IDENTIFIER = '2026-11-28-hadamard-pauli-basis-notes-ko'
FONT_FILES = ['NotoSerifKR-Regular.otf', 'NotoSerifKR-Bold.otf',
              'NotoSansKR-Regular.otf', 'NotoSansKR-Bold.otf']
ACTION_PATTERNS = {'Launch': r'/S\s*/Launch\b', 'JavaScript': r'/S\s*/JavaScript\b',
                   'OpenAction': r'/OpenAction\b', 'GoToR': r'/S\s*/GoToR\b',
                   'EmbeddedFile': r'/EmbeddedFile\b', 'AA': r'/AA\b',
                   'AcroForm': r'/AcroForm\b'}
PRIVATE_PATTERN = re.compile(r'/(?:Users|home|private)/|mailto:|chatgpt\.com/share/|'
                             r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tex_escape(value):
    mapping = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
               '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
               '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(mapping.get(char, char) for char in value)


def strict_provenance(path):
    spec = importlib.util.spec_from_file_location('atrl_saved_model_provenance', REPO / 'scripts/ai_model_provenance.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = module.validate_public_provenance(json.loads(path.read_text(encoding='utf-8')))
    # The saved role-setting disclosure, not the machine's current defaults,
    # is authoritative for this edition. Backticks are presentation markup.
    disclosure = module.render_disclosure(record, 'ko').replace('`', '')
    return record, disclosure


def private_workdir(path):
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO.resolve())
    except ValueError:
        return resolved
    if not str(relative).startswith('archive/private/'):
        raise ValueError('In-repository build intermediates must be in ignored private intake')
    return resolved


def compile_tex(engine, workdir):
    environment = os.environ.copy()
    # Stable ancillary timestamps do not claim a source creation time.
    environment['SOURCE_DATE_EPOCH'] = '1795824000'
    runs = []
    for number in range(1, 4):
        result = subprocess.run([engine, '-no-shell-escape', '-interaction=nonstopmode',
                                 '-halt-on-error', '-file-line-error', 'main.tex'],
                                cwd=workdir, env=environment, capture_output=True,
                                text=True, timeout=180)
        (workdir / f'compile-pass-{number}.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
        runs.append({'pass': number, 'exit_code': result.returncode})
        if result.returncode:
            raise RuntimeError(f'XeLaTeX pass {number} failed; inspect the private compile log')
        log = (workdir / 'main.log').read_text(encoding='utf-8', errors='replace')
        if number >= 2 and not any(term in log for term in ['Rerun to get', 'Label(s) may have changed', 'rerunfilecheck Warning']):
            break
    if any(term in log for term in ['Missing character:', 'Undefined control sequence', 'There were undefined references', 'There were multiply-defined labels']):
        raise ValueError('Missing glyph, undefined command or unresolved reference in final TeX log')
    warnings = []
    for line in log.splitlines():
        if any(term in line for term in ['Overfull ', 'Underfull ', 'Warning:']):
            warnings.append(line.strip())
    return runs, warnings, log


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--ai-provenance', type=Path, required=True)
    parser.add_argument('--extra-tex', type=Path, action='append', default=[])
    parser.add_argument('--font-dir', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--engine', default='xelatex')
    parser.add_argument('--render-scale', type=float, default=1.5)
    parser.add_argument('--no-render', '--skip-render', dest='no_render', action='store_true',
                        help='Compile/audit only; page rendering is a separate serial stage')
    args = parser.parse_args()
    old_v2 = TOPIC / 'output/pdf' / (IDENTIFIER + '.pdf')
    if args.output.resolve() == old_v2.resolve():
        raise ValueError('The existing v2 public edition must remain immutable')
    if (REPO / 'archive/files').resolve() in args.output.resolve().parents:
        raise ValueError('Build a separate candidate; archive import is a separate reviewed step')
    if args.output.exists():
        raise FileExistsError('Do not overwrite an existing candidate or frozen edition')
    engine = shutil.which(args.engine)
    if not engine:
        raise FileNotFoundError('XeLaTeX engine is not available')
    metadata = json.loads(args.metadata.read_text(encoding='utf-8'))
    required = {'title', 'author', 'subject', 'short_title', 'version'}
    assert required <= set(metadata) and all(isinstance(metadata[key], str) and metadata[key].strip() for key in required)
    record, disclosure = strict_provenance(args.ai_provenance)
    body = args.body.read_text(encoding='utf-8')
    extras = {path.name: path.read_text(encoding='utf-8') for path in args.extra_tex}
    assert len(extras) == len(args.extra_tex), 'Extra TeX basenames must be unique'
    assert not set(extras) & {'main.tex', 'figures.tex', 'atrl-lecture.sty', 'provenance.tex', 'lecture-body.tex'}
    combined_source = body + '\n' + '\n'.join(extras.values())
    assert r'\documentclass' not in body and r'\begin{document}' not in body
    assert r'\AIModelDisclosure' in combined_source, 'Body must place the saved role-setting disclosure in its colophon'
    assert not PRIVATE_PATTERN.search(combined_source)
    workdir = private_workdir(args.work_dir)
    workdir.mkdir(parents=True, exist_ok=False)
    fonts = workdir / 'fonts'
    fonts.mkdir()
    for name in FONT_FILES:
        shutil.copyfile(args.font_dir / name, fonts / name)
    for name in ['atrl-lecture.sty', 'figures.tex']:
        shutil.copyfile(HERE / name, workdir / name)
    (workdir / 'lecture-body.tex').write_text(body, encoding='utf-8')
    for name, content in extras.items():
        (workdir / name).write_text(content, encoding='utf-8')
    (workdir / 'provenance.tex').write_text(
        '\\newcommand{\\AIModelDisclosure}{' + tex_escape(disclosure) + '}\n', encoding='utf-8')
    declarations = (
        '\\renewcommand{\\ATRLRunningTitle}{' + tex_escape(metadata['short_title']) + '}\n'
        '\\renewcommand{\\ATRLVersion}{' + tex_escape(metadata['version']) + '}\n'
        '\\hypersetup{pdftitle={' + tex_escape(metadata['title']) + '},'
        'pdfauthor={' + tex_escape(metadata['author']) + '},'
        'pdfsubject={' + tex_escape(metadata['subject']) + '}}\n'
    )
    wrapper = ('\\documentclass[11pt,a4paper]{article}\n'
               '\\usepackage{atrl-lecture}\n' + declarations +
               '\\input{figures.tex}\n\\input{provenance.tex}\n'
               '\\begin{document}\n\\input{lecture-body.tex}\n\\end{document}\n')
    (workdir / 'main.tex').write_text(wrapper, encoding='utf-8')
    passes, warnings, log = compile_tex(engine, workdir)
    generated = fitz.open(workdir / 'main.pdf')
    generated.set_metadata({'title': metadata['title'], 'author': metadata['author'],
                            'subject': metadata['subject'],
                            'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted lecture',
                            'producer': '', 'creationDate': '', 'modDate': '', 'keywords': ''})
    generated.del_xml_metadata()
    generated.xref_set_key(generated.pdf_catalog(), 'OpenAction', 'null')
    generated.update_object(generated.pdf_catalog(), re.sub(r'\s*/OpenAction\s+null\b', '',
                                                           generated.xref_object(generated.pdf_catalog())))
    intermediate = workdir / 'public-candidate.pdf'
    generated.save(intermediate, garbage=4, deflate=True, clean=False)
    generated.close()
    final = fitz.open(intermediate)
    text = '\n'.join(page.get_text() for page in final)
    objects = '\n'.join(final.xref_object(index) for index in range(1, final.xref_length()))
    assert not PRIVATE_PATTERN.search(text + objects)
    assert not re.search(r'\\(?:frac|begin|end|mathrm|textbf|ket|bra)\b', text), 'Raw TeX escaped into visible PDF text'
    assert len(re.findall('[가-힣]', text)) >= 200, 'Korean text extraction is unexpectedly incomplete'
    assert not '\ufffd' in text, 'Replacement glyph in extracted text'
    actions = {key: len(re.findall(pattern, objects)) for key, pattern in ACTION_PATTERNS.items()}
    assert not any(actions.values()) and final.embfile_count() == 0
    original_links = []
    for page_number, page in enumerate(final):
        for link in page.get_links():
            assert link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED, fitz.LINK_URI)
            if 'uri' in link:
                assert link['uri'].startswith('https://'), 'Only clean public HTTPS references are permitted'
                original_links.append({'page': page_number + 1, 'uri': link['uri']})
    font_inventory = []
    for xref in sorted({font[0] for page in final for font in page.get_fonts(full=True)}):
        name, extension, font_type, font_bytes = final.extract_font(xref)
        assert font_bytes, f'Font is not embedded: {name}'
        font_inventory.append({'name': name, 'format': extension, 'type': font_type,
                               'embedded_bytes': len(font_bytes)})
    if not args.no_render:
        page_images = workdir / 'render'
        page_images.mkdir()
        for number, page in enumerate(final):
            page.get_pixmap(matrix=fitz.Matrix(args.render_scale, args.render_scale),
                           alpha=False).save(page_images / f'page-{number + 1:02d}.png')
    figure_keys = re.findall(r'\\lecturefigure\s*\{([^{}]+)\}', body)
    assert len(figure_keys) == len(set(figure_keys)), 'Figure labels must be unique'
    report = {
        'status': 'AWAITING_FULL_PAGE_VISUAL_AND_SCIENTIFIC_REVIEW',
        'identifier': IDENTIFIER, 'edition': metadata['version'],
        'public_pages': len(final), 'public_sha256': sha256(intermediate),
        'public_bytes': intermediate.stat().st_size, 'file': args.output.name,
        'source_inputs': {name: sha256(path) for name, path in [
            ('lecture-body.tex', args.body), ('metadata.json', args.metadata),
            ('ai-model-provenance.json', args.ai_provenance),
            ('atrl-lecture.sty', HERE / 'atrl-lecture.sty'), ('figures.tex', HERE / 'figures.tex')]},
        'compile_passes': passes, 'latex_warnings_for_review': warnings,
        'missing_glyphs': False, 'raw_tex_visible': False,
        'korean_text_extractable': True, 'fonts_embedded': font_inventory,
        'figure_keys': figure_keys, 'public_uri_annotations': original_links,
        'outline_entries': len(final.get_toc()), 'named_destinations': len(final.resolve_names()),
        'action_scan': actions, 'embedded_files': 0,
        'private_patterns_found': False, 'source_dates_and_tool_metadata_removed': True,
        'model_provenance': record, 'qa_images_public': False,
        'page_images_rendered': not args.no_render,
        'v2_pdf_overwritten': False,
        'build_scope': 'Typesetting, original deterministic vector diagrams, static PDF QA and full-page rendering only; no SDK, backend, QPU or physical experiment.',
    }
    report['source_inputs'].update({path.name: sha256(path) for path in args.extra_tex})
    (workdir / 'pdf-build-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    final.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(intermediate, args.output)
    print(json.dumps({'pages': report['public_pages'], 'sha256': report['public_sha256'],
                      'bytes': report['public_bytes'], 'figure_keys': figure_keys,
                      'warnings_to_review': len(warnings)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
