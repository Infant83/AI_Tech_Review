"""Build reviewed bilingual publication HTML with a strict, flat asset allowlist.

Run with a Python environment containing Markdown. PDF printing is separate so a
content rebuild does not silently regenerate editions already being verified.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import re
import shutil
import markdown

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
DIST = ROOT / 'dist'
BASE = 'https://infant83.io/AI_Tech_Review/reviews/' + ROOT.name + '/'
DATE = '2026-11-27'
PUBLICATION_DATE = '2026-11-28'
BRAND = 'Agentic Tech Review Letters'
SOURCE_FIGURES = ['deng-2025-fig4.png', 'grandel-2026-fig4.png']
FONT_FILES = ['review-regular.woff2','review-bold.woff2','review-symbols-regular.woff2','review-symbols-bold.woff2','review-math.woff2']

def sha(data): return hashlib.sha256(data).hexdigest()
def esc(s): return html.escape(str(s), quote=True)

def font_css():
    rules = []
    for filename in FONT_FILES:
        weight = 700 if 'bold' in filename else 400
        family = 'ReviewSymbols' if 'symbols' in filename else 'ReviewMath' if 'math' in filename else 'ReviewSans'
        payload = base64.b64encode((ART/filename).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/woff2;base64,{payload}) format('woff2');font-display:block}}")
    return '\n'.join(rules)

def embed_svg(source):
    svg = source.read_text(encoding='utf-8')
    svg = re.sub(r'font-family:[^;}]+', 'font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif', svg)
    license_text = (ART/'font-license.txt').read_text().replace('*/','')
    return re.sub(r'<svg\b[^>]*>', lambda m:m[0]+'<style><![CDATA[/* '+license_text+' */\n'+font_css()+']]></style>',svg,count=1)

def model_disclosure(lang):
    # Read fixed, nonsecret authoring records; no session/config access at build time.
    ko=lang=='ko'
    editing=json.loads((ART/'ai-model-provenance-figures-integration.json').read_text(encoding='utf-8'))['roles']
    production=json.loads((ART/'ai-model-provenance-figures-production.json').read_text(encoding='utf-8'))['roles']
    assert len(editing)==1 and editing[0]['role']=='editing' and editing[0]['evidence_kind']=='turn_context'
    assert len(production)==1 and production[0]['role']=='pdf-production' and production[0]['evidence_kind']=='settings_snapshot'
    e,p=editing[0],production[0]
    if ko:
        return f"OpenAI Codex · 이번 원그림 보완의 편집 설정: {e['model_id']}, 추론 강도 {e['reasoning_effort']}(대화 설정 기록). PDF 제작 설정: {p['model_id']}, 추론 강도 {p['reasoning_effort']}(현재 기본설정 스냅숏; 실제 대화별 제작 모델 미확인). 초기 집필 담당별 설정은 이번 보완에서 확인하지 않았다."
    return f"OpenAI Codex · Editing settings for this source-figure addition: {e['model_id']}, reasoning effort {e['reasoning_effort']} (conversation-setting record). PDF production settings: {p['model_id']}, reasoning effort {p['reasoning_effort']} (current default-settings snapshot; actual production-conversation model unverified). Initial writing-role settings were not checked in this update."

def disclosure(lang, reference_count):
    ko = lang=='ko'
    rows = [
      ('책임 편집자' if ko else 'Responsible editor','김현중' if ko else 'Hyun-Jung Kim'),
      ('AI 시스템' if ko else 'AI system',model_disclosure(lang)),
      ('확인 가능한 에이전트 역할' if ko else 'Identifiable agent roles',
       'Codex: 기획·국문 집필·통합. foundation_sources: 1차 문헌·서지 대조, 영문 집필·한영 출판 출력과 시각 검토. foundation_calculations: 교육 모형의 독립 검산·한영 피규어. quantum_registration: 별도 독자 관점 감수. figure_source_audit: 원논문 그림·조건·이용 조건 대조. source_figure_production: 원그림 통합과 한영 출력 검수.' if ko else
       'Codex: planning, Korean writing and integration. foundation_sources: primary-source and bibliographic audit, English writing, bilingual production and visual checks. foundation_calculations: independent numerical checks and bilingual figures. quantum_registration: separate reader review. figure_source_audit: source figures, conditions and reuse terms. source_figure_production: integration and bilingual output checks.'),
      ('편집·검수 방법서 기본판' if ko else 'Editorial/checking method','AI Tech Review Editorial Harness '+('기본판 2026.08' if ko else 'base edition 2026.08')),
      ('이번에 적용한 보완' if ko else 'Applied supplements','2026-10-22 '+('과학 설명 준칙; 2026-11-06 문장·캡션; 2026-11-11 독자 친화성; 2026-11-16 독자 흐름; 2026-11-26 문맥·관습적 전개 감수; 2026-11-27 외부 그림의 선정·이용 조건·출처·변경 공개' if ko else 'scientific explanation; 2026-11-06 prose/captions; 2026-11-11 reader-friendly explanation; 2026-11-16 reader flow; 2026-11-26 contextual prose and habitual narrative patterns; 2026-11-27 selection, reuse terms, attribution and change disclosure for external figures')),
      ('공방 조직·운영 근거' if ko else 'Atelier organization/operations','ATRL의 편집부(AEDAUT)·운영팀(ADOPT) 역할 기준을 따른다. 이번 리뷰는 사전학습 원자간 포텐셜의 재사용·물성 검증·에이전틱 계산 절차를 다룬다.' if ko else 'Follows the ATRL role framework for the editorial team (AEDAUT) and operations team (ADOPT). This review examines the reuse of pretrained interatomic potentials, property validation and agentic computational workflows.'),
      ('이번 원고 판본' if ko else 'Current manuscript','제1판 · 원고·근거 기준일 2026-11-27; 한영 출력 검수 2026-11-27.' if ko else 'First edition · manuscript and evidence date 2026-11-27; bilingual production checks 2026-11-27.'),
      ('검증 범위' if ko else 'Verification scope',f'원 논문·공식 자료·{reference_count}개 참고문헌 대조. 조화 진동 교육 모형의 단위·힘·곡률·진동수 독립 검산. 한영 본문·그림·웹·PDF 검토. 출발 Perspective는 공개 소개·서지를 확인했고, 개별 결과는 공개 원 연구와 대조했다. 원 연구의 MLIP·DFT·MD·에이전트 계산은 독립 재실행하지 않았다.' if ko else f'Primary papers, official sources and {reference_count} references checked. Independent checks of units, forces, curvature and frequencies in a harmonic teaching model. Bilingual prose, figures, web and PDF outputs reviewed. The starting Perspective was checked through its public introduction and bibliographic record; individual results were checked against public primary studies. Source MLIP, DFT, MD and agent calculations were not independently rerun.'),
      ('사람 검토 수준' if ko else 'Human review level','사람이 주제·관점·기획 방향을 제시하고 집필 진행을 승인했다. 별도의 문장 단위 사람 감수는 기록되지 않았다.' if ko else 'A person set the topic, perspective and editorial direction and approved proceeding with the manuscript. No separate line-by-line human review is recorded.')]
    dl=''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in rows)
    note='그림 1·5는 재사용·검증·계산 절차의 개념 설계이며, 그림 2는 조화 진동 교육 계산이다. 그림 3·4는 각각 Deng 등과 Grandel 등의 정식 출판 그림을 CC BY 4.0에 따라 원본 그대로 복제했고 출처·저작권·이용 조건을 캡션에 표시했다. 실제 물질의 모델 성능·상전이·반복 실행 결과는 원 연구의 저자 보고로 구별했다. 표지는 내장 imagegen의 AI 생성 개념 그림이다.' if ko else 'Figures 1 and 5 are conceptual designs for reuse, validation and computational workflows; Figure 2 is a harmonic teaching calculation. Figures 3 and 4 reproduce the original published figures of Deng et al. and Grandel et al. under CC BY 4.0; their captions identify sources, copyright and reuse terms. Model performance, phase-transition and repeated-execution results for real materials are distinguished as author-reported findings. The cover is a conceptual illustration generated with built-in imagegen.'
    title='작성·검증 정보' if ko else 'How this review was made'
    methods='작성·검증 원칙' if ko else 'Methods and verification'
    return f'<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure"><h2>{title}</h2><dl>{dl}</dl><p>{note}</p><p><a href="https://infant83.io/AI_Tech_Review/methods/">{methods}</a></p></section><!-- End AI Tech Review Authoring Disclosure -->'

CSS = '''
:root{--paper:#f7f5ef;--ink:#223c44;--muted:#566c70;--teal:#236366;--line:#ccd5d1;--wash:#e7eeeb}
*{box-sizing:border-box}html{scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif;font-size:18px;line-height:1.9;word-break:keep-all;overflow-wrap:anywhere}
header{border-bottom:1px solid var(--line);padding:19px 32px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{font-size:12px;font-weight:700;letter-spacing:.1em;text-decoration:none}.header-links{display:flex;gap:22px;font-size:12px}.header-links a{text-decoration:none}.paper{max-width:960px;margin:auto;padding:52px 64px 70px}.issue-meta{font-size:11px;color:var(--teal);letter-spacing:.04em;margin-bottom:17px}h1{font-size:42px;line-height:1.35;letter-spacing:-.04em;font-weight:700;margin:0 0 22px;text-wrap:balance}p{margin:0 0 23px}h2{font-size:26px;line-height:1.45;letter-spacing:-.03em;margin:58px 0 25px;border-top:1px solid var(--line);padding-top:20px;text-wrap:balance}p.dek{font-size:20px;line-height:1.65;color:var(--teal);margin-bottom:20px}.byline-disclosure{font-size:11px;color:var(--muted);line-height:1.85;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:12px 0;margin:23px 0 28px}a{color:var(--teal);text-underline-offset:3px;text-decoration-thickness:1px}.cite{font-size:.76em;white-space:nowrap;vertical-align:super;line-height:0}.cite a{text-decoration:none}
figure{margin:34px -30px 39px;break-inside:avoid}figure img{display:block;width:100%;height:auto}figure picture{display:block}.source-result{background:#fff;border:1px solid var(--line);padding:14px 14px 17px}.source-figure-scroll{max-width:100%;overflow-x:auto}.source-figure-scroll:focus-visible{outline:2px solid var(--teal);outline-offset:3px}.source-figure-hint{display:none}.source-result figcaption{padding:12px 2px 0}figure figcaption{font-size:12px;line-height:1.8;color:var(--muted);padding:12px 10px 0}.hero{margin:31px -30px 37px}.hero img{border-radius:3px}.figure-larger{white-space:nowrap;margin-left:.5em;font-weight:700}.equation{font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif;font-size:22px;text-align:center;background:var(--wash);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:21px 10px;margin:25px 0 29px;break-inside:avoid}.table-scroll{max-width:100%;overflow-x:auto}table{border-collapse:collapse;width:100%;margin:26px 0 34px;font-size:13px;line-height:1.75;table-layout:fixed}th{text-align:left;background:var(--wash);font-weight:700}th,td{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}th:first-child,td:first-child{width:18%;font-weight:700}thead{display:table-header-group}tr{break-inside:avoid}.theory-note{font-size:15px;line-height:1.9;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:27px 0 32px;padding:14px 0}.theory-note summary{font-weight:700;color:var(--teal);cursor:pointer}.theory-note p{margin:17px 0 2px}.references{font-size:13px;line-height:1.8}.references p{margin-bottom:18px;word-break:normal}.authoring-disclosure{margin-top:40px;padding:24px 25px;background:var(--wash);border-top:2px solid var(--teal);font-size:12px;line-height:1.8}.authoring-disclosure h2{font-size:19px;border:0;padding:0;margin:0 0 17px}.authoring-disclosure dl{margin:0}.authoring-disclosure dl>div{display:grid;grid-template-columns:145px 1fr;gap:15px;margin:12px 0}.authoring-disclosure dt{font-weight:700}.authoring-disclosure dd{margin:0}.authoring-disclosure p{margin:17px 0 0}.downloads{display:flex;gap:22px;margin-top:25px;font-size:13px}.footer{font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:18px;margin-top:30px}
@media(max-width:760px){.source-result{padding:10px}.source-figure-scroll img{width:860px;max-width:none}.source-figure-hint{display:block;font-size:11px;line-height:1.6;color:var(--muted);margin:0 0 9px}.source-result figcaption{padding:11px 0 0}table{min-width:680px;font-size:13px;line-height:1.75;margin:23px 0}th,td{padding:10px 9px}th:first-child,td:first-child{width:18%}body{font-size:17px;line-height:1.9}header{padding:17px 20px;flex-wrap:wrap}.brand{font-size:10px}.header-links{font-size:11px;gap:16px}.paper{padding:34px 21px 50px}h1{font-size:31px;line-height:1.4}h2{font-size:23px;margin-top:44px}p.dek{font-size:17px}.hero{margin:27px -21px 31px}.hero figcaption{padding-left:21px;padding-right:21px}figure{margin:29px -8px 34px}figure figcaption{font-size:12px;padding-left:8px;padding-right:8px}.equation{font-size:19px}.authoring-disclosure{padding:19px 20px}.authoring-disclosure dl>div{grid-template-columns:1fr;gap:3px;margin:15px 0}.references{font-size:12px}}
@media print{.source-result{padding:7pt;border-width:.5pt}.source-figure-scroll{overflow:visible}.source-figure-scroll img{width:100%;max-width:100%;height:auto}.source-figure-hint{display:none}.table-scroll{overflow:visible}table{min-width:0;font-size:7.2pt;line-height:1.65;margin:12pt 0 16pt}th,td{padding:3.5pt 5pt}table,tbody{break-inside:auto}tr{break-inside:avoid}thead{display:table-header-group}@page{size:A4;margin:17mm 17mm 19mm}html[lang="en"] body{font-size:9.6pt;line-height:1.6}body{background:white;color:var(--ink);font-size:10pt;line-height:1.66}header,.downloads,.footer,.figure-larger{display:none}.paper{max-width:none;margin:0;padding:0}.issue-meta{font-size:7pt;margin-bottom:10pt}h1{font-size:25pt;line-height:1.35;margin-bottom:12pt}p.dek{font-size:11.5pt;line-height:1.6;margin-bottom:12pt}p{margin:0 0 10.5pt;orphans:3;widows:3}h2{font-size:15.8pt;line-height:1.4;padding-top:9pt;margin:22pt 0 10pt;break-after:avoid}h2+p{break-inside:avoid}.byline-disclosure{font-size:7pt;padding:7pt 0;margin:12pt 0 15pt}.hero{margin:16pt 0 18pt}.hero img{max-height:82mm;object-fit:contain}figure{margin:15pt 0 18pt;break-inside:avoid}figure picture img{max-height:142mm;object-fit:contain}figure figcaption{padding:6pt 0 0;font-size:7.5pt;line-height:1.65}.equation{font-size:12pt;padding:10pt 8pt;margin:13pt 0 16pt}.theory-note{font-size:8.5pt;line-height:1.7;padding:9pt 0;margin:14pt 0 17pt;break-inside:avoid}.theory-note summary{font-size:9pt}.theory-note p{margin:9pt 0 0}.references{font-size:8pt;line-height:1.7}.references p{margin-bottom:10pt;break-inside:avoid}.authoring-disclosure{font-size:7.4pt;line-height:1.5;padding:10pt 13pt;margin-top:16pt;break-inside:avoid}.authoring-disclosure h2{font-size:12pt;margin-bottom:10pt}.authoring-disclosure dl>div{grid-template-columns:92pt 1fr;gap:9pt;margin:3.5pt 0;break-inside:avoid}.authoring-disclosure p{margin-top:6pt}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''

def build():
    license_text=(ART/'font-license.txt').read_text().replace('*/','')
    css='/* '+license_text+' */\n'+font_css()+'\n'+CSS
    source_records=json.loads((ART/'source-figures/manifest.json').read_text(encoding='utf-8'))['figures']
    assert {r['file'] for r in source_records}==set(SOURCE_FIGURES)
    source_hashes={r['file']:r['sha256'] for r in source_records}
    for name,expected_hash in source_hashes.items():
        if sha((ART/'source-figures'/name).read_bytes())!=expected_hash: raise ValueError('Unreviewed source-figure bytes: '+name)
    results=[]
    for lang in ['ko','en']:
        ko=lang=='ko'; source=ROOT/'reports'/f'review_{lang}.md'
        text=source.read_text(encoding='utf-8')
        if re.search(r'/Users/|file://|<script\b',text):raise ValueError('Private or executable source input')
        lines=text.splitlines();title=lines[0][2:];dek=lines[2].strip('*')
        text=text.replace(lines[2],f'<p class="dek">{esc(dek)}</p>',1)
        body=markdown.markdown(text,extensions=['tables','sane_lists'])
        head,refs=body.split('<h2>'+('참고문헌' if ko else 'References')+'</h2>',1)
        refs=re.sub(r'<p>\[(\d+)\]',lambda m:f'<p id="ref-{m[1]}">[{m[1]}]',refs)
        reference_count=len(re.findall(r'id="ref-\d+"',refs))
        if reference_count < 1: raise ValueError('No numbered references')
        def cite(m):
            terms=[]
            for part in m[1].split(','):
                if '–' in part or '-' in part:
                    first,last=map(int,re.split('[–-]',part))
                    terms.append('–'.join(f'<a role="doc-biblioref" href="#ref-{n}">{n}</a>' for n in [first,last]))
                else:
                    n=part.strip();terms.append(f'<a role="doc-biblioref" href="#ref-{n}">{n}</a>')
            return '<span class="cite">['+','.join(terms)+']</span>'
        head=re.sub(r'\[(\d+(?:(?:,|–|-)\s*\d+)*)\]',cite,head)
        body=head+'<h2 id="references">'+('참고문헌' if ko else 'References')+'</h2><div class="references">'+refs+'</div>'
        body=body.replace('../artifacts/figures/','').replace('../artifacts/source-figures/','').replace('../artifacts/','')
        body=body.replace('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="'+('가로로 살펴보는 비교표' if ko else 'Horizontally scrollable comparison table')+'"><table>').replace('</table>','</table></div>')
        def larger(m):
            figure=m[0]
            filename=re.search(r'<img[^>]*src="([^"]+\.(?:svg|png|jpg|jpeg))"',figure)[1]
            original=filename in SOURCE_FIGURES
            label=('원본 크게 보기' if ko else 'View original at full size') if original else ('크게 보기' if ko else 'View larger')
            if original:
                if 'class="source-result"' not in figure: raise ValueError('Source figure needs an explicit result class')
                hint='좌우로 이동해 원그림의 축·범례를 읽을 수 있습니다.' if ko else 'Scroll horizontally to read the original axes and legends.'
                number=re.search(r'id="fig-(\d+)"',figure)[1]
                region='그림 '+number+' 원논문 결과' if ko else 'Figure '+number+' original research results'
                figure=re.sub(r'(<img[^>]+>)',lambda image:f'<p class="source-figure-hint">{hint}</p><div class="source-figure-scroll" tabindex="0" role="region" aria-label="{region}">{image[0]}</div>',figure,count=1)
            return figure.replace('</figcaption>',f' <a class="figure-larger" href="{filename}" target="_blank" rel="noopener">{label}</a></figcaption>')
        body=re.sub(r'<figure(?![^>]*class="hero")[\s\S]*?</figure>',larger,body)

        byline=f'<p class="byline-disclosure">'+('책임 편집: 김현중 · AI 보조 작성: Codex' if ko else 'Responsible editor: Hyun-Jung Kim · AI assistance: Codex')+f' · {DATE} · '+('근거 기준 2026-11-27 / 출력 검수 2026-11-27' if ko else 'Evidence 2026-11-27 / production checks 2026-11-27')+' · <a href="#authoring-disclosure">'+('작성·검증 정보' if ko else 'Production and verification')+'</a></p>'
        body=re.sub(r'(<p class="dek">.*?</p>)',lambda m:m[0]+byline,body,count=1)
        url=BASE+('' if ko else 'en/');other=BASE+('en/' if ko else '')
        desc=('사전학습한 원자간 포텐셜을 새 물질에서 다시 쓰는 조건을 살핀다. 에너지의 곡률과 진동에서 출발해 모델의 적응·물성 검증·에이전틱 계산 절차로 이어간다.' if ko else 'Explore what it takes to reuse a pretrained interatomic potential for a new material, from energy curvature and vibrations to model adaptation, property validation and agentic computational workflows.')
        top='<header><a class="brand" href="https://infant83.io/AI_Tech_Review/">'+BRAND.upper()+'</a><nav class="header-links" aria-label="'+('언어와 다운로드' if ko else 'Language and downloads')+'"><span lang="'+lang+'" aria-current="page">'+('한국어' if ko else 'English')+'</span><a href="'+other+'" hreflang="'+('en' if ko else 'ko')+'">'+('English' if ko else '한국어')+'</a><a href="review_'+lang+'.pdf">PDF ↓</a><a href="https://infant83.io/AI_Tech_Review/methods/">'+('작성 원칙' if ko else 'Methods')+'</a></nav></header>'
        document=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="author" content="{'김현중' if ko else 'Hyun-Jung Kim'}"><meta name="evidence-cutoff" content="{DATE}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}hero.png"><meta property="article:published_time" content="{PUBLICATION_DATE}"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ko" href="{BASE}"><link rel="alternate" hreflang="en" href="{BASE}en/"><link rel="alternate" hreflang="x-default" href="{BASE}"><link rel="stylesheet" href="review.css"></head><body>{top}<main class="paper"><div class="issue-meta">RESEARCH LETTER · {DATE} · {'원자간 포텐셜 · 물성 검증 · 연구 워크플로' if ko else 'INTERATOMIC POTENTIALS · PROPERTY VALIDATION · RESEARCH WORKFLOWS'}</div><article>{body}{disclosure(lang,reference_count)}</article><div class="downloads"><a href="review_{lang}.pdf">{'한국어 PDF 내려받기' if ko else 'Download English PDF'}</a><a href="{other}">{'English version' if ko else '한국어판'}</a></div><footer class="footer">{BRAND} · {DATE}</footer></main></body></html>
'''
        dest=DIST/('' if ko else 'en');dest.mkdir(parents=True,exist_ok=True)
        assets=set(re.findall(r'(?:src|srcset)="([^"#]+)"',document))
        expected={'hero.png'}|set(SOURCE_FIGURES)|{f'fig{n}_{variant}'+('' if ko else '_en')+'.svg' for n in [1,2,5] for variant in ['desktop','mobile']}
        assert assets==expected,(assets,expected)
        for name in sorted(assets):
            src=ART/name if name=='hero.png' else ART/('source-figures' if name in SOURCE_FIGURES else 'figures')/name
            if name.endswith('.svg'):(dest/name).write_text(embed_svg(src),encoding='utf-8')
            else:
                shutil.copy2(src,dest/name)
                if name in source_hashes: assert sha((dest/name).read_bytes())==source_hashes[name]
        (dest/'review.css').write_text(css,encoding='utf-8');(dest/'index.html').write_text(document,encoding='utf-8')
        (ART/f'review_{lang}.html').write_text(document,encoding='utf-8')
        results.append({'language':lang,'title':title,'subtitle':dek,'description':desc,'date':DATE,'published_date':PUBLICATION_DATE,'html_sha256':sha(document.encode()),'assets':sorted(assets),'references':reference_count,'tables':body.count('<table>'),'images':body.count('<img '),'source_figures':SOURCE_FIGURES,'source_figure_sha256':source_hashes})
    (ART/'production-html-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False))

if __name__=='__main__':build()
