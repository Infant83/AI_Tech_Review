"""Render the existing bilingual article from reports/, preserving its assets and links."""
from pathlib import Path
import html
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
TOPIC = '2026-08-27_dwave-molecular-inverse-design-benchmark'
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts'))
from markdown_to_html import build_context, render_final_review_template
from html_to_dist import package_html

# The former Markdown renderer generated these stable public fragment IDs.
# Preserve them if headings are later phrased differently.
LEGACY_IDS = {
    '계산한 범위부터 확인해 보자':'_1',
    '예측 모델에서는 ExtraTrees의 MAE가 더 낮았다':'extratrees-mae',
    '세 생성 경로에 같은 화학 규칙을 적용했다':'_2',
    'QUBO는 목표 적합성과 배치 다양성을 함께 계산한다':'qubo',
    '한 번의 QPU 실행은 exact optimum을 재현하지 못했다':'qpu-exact-optimum',
    'PySCF 계산에서 exact batch는 평균이 낮았고, QPU batch에는 가장 가까운 한 후보가 있었다':'pyscf-exact-batch-qpu-batch',
    '반복 정책은 고정 QM9 라벨 replay로 점검했다':'qm9-replay',
    '확인된 증거와 남은 판단':'_3',
    '작성 정보':'_4',
    'References':'references',
}


def preserve_links(text):
    present=set(re.findall(r'\bid="([^"]+)"',text))
    def alias(m):
        title=html.unescape(re.sub('<[^>]+>','',m[3]))
        old=LEGACY_IDS.get(title)
        if old and old not in present:
            present.add(old)
            return f'<span class="legacy-anchor" id="{old}" aria-hidden="true"></span>'+m[0]
        return m[0]
    return re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>',alias,text,flags=re.S)


def main():
    settings=json.loads((HERE/'rendering-settings.json').read_text())
    for language,suffix,subdir in [('ko','',''),('en','_en','en')]:
        source=ROOT/TOPIC/'reports'/f'{TOPIC}_final_review{suffix}.md'
        context=build_context(source,'final-review')
        context.generated_at=settings['original_generated_at'][language]
        context.source_modified_at=context.modified_date
        context.body_html=preserve_links(context.body_html)
        def version_artwork(url):
            local=url.split('?',1)[0]
            if Path(local).stem not in {'molecular_inverse_design_infographic','molecular_inverse_design_infographic_en'}:
                return url
            path=(source.parent/local).resolve()
            if not path.is_file():raise ValueError('Missing infographic source')
            return local+'?v='+hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        context.body_html=re.sub(r'(\b(?:src|href)=")([^"]+)(")',lambda m:m[1]+version_artwork(m[2])+m[3],context.body_html)
        for item in context.links:
            if not item.external:item.href=version_artwork(item.href)
        count=0
        def figure(m):
            nonlocal count
            count+=1
            url=re.search(r'\bsrc="([^"]+)"',m[1]).group(1)
            label=f'그림 {count} 크게 보기 (새 탭)' if language=='ko' else f'Open Figure {count} at full size (new tab)'
            return f'<figure class="figure-panel"><a class="figure-zoom" href="{url}" target="_blank" rel="noopener" aria-label="{label}">{m[1]}</a><figcaption>{m[2]}</figcaption></figure>'
        context.body_html=re.sub(r'<p>(<img\b[^>]+>)</p>\s*<p><em>((?:그림|Figure) \d+\..*?)</em></p>',figure,context.body_html,flags=re.S)
        if count!=8:raise ValueError(f'Expected all8figures, got{count} in{language}')
        table_label='비교표 좌우로 보기' if language=='ko' else 'Scroll comparison table horizontally'
        context.body_html=context.body_html.replace('<table>',f'<div class="table-scroll" tabindex="0" role="region" aria-label="{table_label}"><table>').replace('</table>','</table></div>')
        math_label='수식 좌우로 보기' if language=='ko' else 'Scroll equation horizontally'
        context.body_html=re.sub(r'(?s)(\$\$.*?\$\$)',rf'<div class="equation-scroll" tabindex="0" role="region" aria-label="{math_label}">\1</div>',context.body_html)
        output=render_final_review_template(context)
        labels=('생성 시각:','원본 파일 최종 수정 시각:') if language=='ko' else ('Generated:','Source last modified:')
        newlabels=('원 발행본 생성 시각:','편집 개정:') if language=='ko' else ('Original edition generated:','Editorial revision:')
        for old,new in zip(labels,newlabels):output=output.replace(old,new)
        css='''\n    .final-article, .content-grid > *, .hero-inner > * { min-width: 0; }
    .figure-panel { margin: 1.7rem 0; }
    .figure-panel figcaption { color: var(--muted); font-size: .94rem; line-height: 1.65; margin-top: .65rem; }
    .figure-zoom { display: block; cursor: zoom-in; }
    .figure-zoom:focus-visible { outline: 2px solid var(--teal); outline-offset: 4px; }
    .table-scroll, .equation-scroll { max-width: 100%; overflow-x: auto; }
    .equation-scroll { margin: 1rem 0; }
    .table-scroll:focus-visible, .equation-scroll:focus-visible { outline: 2px solid var(--teal); }
    .reference-list { padding-left: 1.9rem; overflow-wrap: anywhere; }
    .reference-list li { padding-left: .35rem; margin-bottom: 1rem; }
    .citation { white-space: nowrap; }
'''
        output=output.replace('  </style>',css+'  </style>')
        source.with_suffix('.html').write_text('\n'.join(x.rstrip() for x in output.splitlines())+'\n')
        dist=ROOT/TOPIC/'dist'/subdir
        result=package_html(source.with_suffix('.html'),dist)
        if result.missing_refs:raise ValueError(result.missing_refs)
        flat=source.read_text()
        for name in [*list((HERE/'figures').glob('*')),HERE/'data/benchmark_results.csv']:
            if name.is_file():flat=flat.replace('../artifacts/final_review/'+('data/' if name.suffix=='.csv' else 'figures/')+name.name,name.name)
        (dist/source.name).write_text(flat)
    print('Rendered both complete source manuscripts;8figures each')


if __name__=='__main__':main()
