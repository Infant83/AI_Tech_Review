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
DATE = '2026-11-22'
BRAND = 'Agentic Tech Review Letters'
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

def disclosure(lang):
    ko = lang=='ko'
    rows = [
      ('책임 편집자' if ko else 'Responsible editor','김현중' if ko else 'Hyun-Jung Kim'),
      ('AI 시스템' if ko else 'AI system','OpenAI Codex · '+('정확한 모델 식별자 미보존' if ko else 'exact model identifier not retained')),
      ('확인 가능한 에이전트 역할' if ko else 'Identifiable agent roles',
       'Codex: 조사·국문 집필·통합. entropy_flow_review: 정보·물리 수지 감수. sustainable_agent_governance: 공식 측정·거버넌스 조사와 원고 감수. energy_figures: 결정론적 도표. energy_reader_review: 기획 설명 없는 독자 관점 감수. energy_publication_production: 번역·한영 도표·출판 출력과 시각 검토.' if ko else
       'Codex: research, Korean writing and integration. entropy_flow_review: information and physical balances. sustainable_agent_governance: measurement and governance sources and manuscript review. energy_figures: deterministic figures. energy_reader_review: independent reader review without a separate planning brief. energy_publication_production: translation, bilingual figures, production and visual checks.'),
      ('편집·검수 방법서 기본판' if ko else 'Editorial/checking method','AI Tech Review Editorial Harness '+('기본판 2026.08' if ko else 'base edition 2026.08')),
      ('이번에 적용한 보완' if ko else 'Applied supplements','2026-10-22 '+('과학 설명 준칙; 2026-11-06 문장·캡션; 2026-11-11 독자 친화성; 2026-11-16 독자 흐름 보완' if ko else 'scientific explanation; 2026-11-06 prose/captions; 2026-11-11 reader-friendly explanation; 2026-11-16 reader flow')),
      ('공방 조직·운영 근거' if ko else 'Atelier organization/operations','그림 5는 SCI·OECD·작업 단위 평가에 근거한 리뷰의 운영 제안. 실제 플랫폼 구현·전력 계측 결과와 구별한다.' if ko else 'Figure 5 is a workflow proposal informed by SCI, OECD principles and task-level evaluation; it is distinct from a measured platform implementation.'),
      ('이번 원고 판본' if ko else 'Current manuscript','제1판 · 2026-11-22. 조사·국문 초안 2026-11-20; 한영 출판판 2026-11-22.' if ko else 'First edition · 2026-11-22. Research and Korean draft: 2026-11-20; bilingual publication edition: 2026-11-22.'),
      ('검증 범위' if ko else 'Verification scope','11월20일 원문·공식 자료 조사와 물리·거버넌스·독자 감수. 11월22일 원 논문·실측 논문 판본과 SCI·MLPerf 자료 상태 재확인, 한영 주장·수치·13개 참고문헌·도표·출판 출력 검토. 원 연구의 독립 재실행·ATRL 자체 전력 측정 없음.' if ko else 'Primary and official sources and physics, governance and reader review on November 20. Paper editions and SCI/MLPerf status rechecked on November 22; bilingual claims, values, 13 references, diagrams and publication outputs reviewed. No independent rerun of the source experiments or measurement of ATRL power use.'),
      ('사람 검토 수준' if ko else 'Human review level','사람이 주제·관점·기획 방향을 제시하고 게시를 승인했다. 별도의 문장 단위 사람 감수는 기록되지 않았다.' if ko else 'A person set the topic, perspective and editorial direction and approved publication. No separate line-by-line human review is recorded.')]
    dl=''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in rows)
    note='논문과 장치 계측의 수치는 저자 보고값이며, 그림 1·2는 개념·교육 모형, 그림 3·4는 보고값 재도표, 그림 5는 리뷰의 제안이다. 표지는 내장 imagegen의 AI 생성 개념 그림이다.' if ko else 'Paper and hardware measurements are author-reported. Figures 1–2 are conceptual/educational models, Figures 3–4 replot reported values, and Figure 5 is a review proposal. The cover is a conceptual illustration generated with built-in imagegen.'
    title='작성·검증 정보' if ko else 'How this review was made'
    methods='작성·검증 원칙' if ko else 'Methods and verification'
    return f'<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure"><h2>{title}</h2><dl>{dl}</dl><p>{note}</p><p><a href="https://infant83.io/AI_Tech_Review/methods/">{methods}</a></p></section><!-- End AI Tech Review Authoring Disclosure -->'

CSS = '''
:root{--paper:#f7f4eb;--ink:#293d42;--muted:#586865;--teal:#316a67;--line:#d6d9cc;--wash:#edefe5}
*{box-sizing:border-box}html{scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif;font-size:18px;line-height:1.9;word-break:keep-all;overflow-wrap:anywhere}
header{border-bottom:1px solid var(--line);padding:19px 32px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{font-size:12px;font-weight:700;letter-spacing:.1em;text-decoration:none}.header-links{display:flex;gap:22px;font-size:12px}.header-links a{text-decoration:none}.paper{max-width:960px;margin:auto;padding:52px 64px 70px}.issue-meta{font-size:11px;color:var(--teal);letter-spacing:.04em;margin-bottom:17px}h1{font-size:42px;line-height:1.35;letter-spacing:-.04em;font-weight:700;margin:0 0 22px;text-wrap:balance}p{margin:0 0 23px}h2{font-size:26px;line-height:1.45;letter-spacing:-.03em;margin:58px 0 25px;border-top:1px solid var(--line);padding-top:20px;text-wrap:balance}p.dek{font-size:20px;line-height:1.65;color:var(--teal);margin-bottom:20px}.byline-disclosure{font-size:11px;color:var(--muted);line-height:1.85;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:12px 0;margin:23px 0 28px}a{color:var(--teal);text-underline-offset:3px;text-decoration-thickness:1px}.cite{font-size:.76em;white-space:nowrap;vertical-align:super;line-height:0}.cite a{text-decoration:none}
figure{margin:34px -30px 39px;break-inside:avoid}figure img{display:block;width:100%;height:auto}figure picture{display:block}figure figcaption{font-size:12px;line-height:1.8;color:var(--muted);padding:12px 10px 0}.hero{margin:31px -30px 37px}.hero img{border-radius:3px}.figure-larger{white-space:nowrap;margin-left:.5em;font-weight:700}.equation{font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif;font-size:22px;text-align:center;background:var(--wash);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:21px 10px;margin:25px 0 29px;break-inside:avoid}.theory-note{font-size:15px;line-height:1.9;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:27px 0 32px;padding:14px 0}.theory-note summary{font-weight:700;color:var(--teal);cursor:pointer}.theory-note p{margin:17px 0 2px}.references{font-size:13px;line-height:1.8}.references p{margin-bottom:18px;word-break:normal}.authoring-disclosure{margin-top:40px;padding:24px 25px;background:var(--wash);border-top:2px solid var(--teal);font-size:12px;line-height:1.8}.authoring-disclosure h2{font-size:19px;border:0;padding:0;margin:0 0 17px}.authoring-disclosure dl{margin:0}.authoring-disclosure dl>div{display:grid;grid-template-columns:145px 1fr;gap:15px;margin:12px 0}.authoring-disclosure dt{font-weight:700}.authoring-disclosure dd{margin:0}.authoring-disclosure p{margin:17px 0 0}.downloads{display:flex;gap:22px;margin-top:25px;font-size:13px}.footer{font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:18px;margin-top:30px}
@media(max-width:760px){body{font-size:17px;line-height:1.9}header{padding:17px 20px;flex-wrap:wrap}.brand{font-size:10px}.header-links{font-size:11px;gap:16px}.paper{padding:34px 21px 50px}h1{font-size:31px;line-height:1.4}h2{font-size:23px;margin-top:44px}p.dek{font-size:17px}.hero{margin:27px -21px 31px}.hero figcaption{padding-left:21px;padding-right:21px}figure{margin:29px -8px 34px}figure figcaption{font-size:12px;padding-left:8px;padding-right:8px}.equation{font-size:19px}.authoring-disclosure{padding:19px 20px}.authoring-disclosure dl>div{grid-template-columns:1fr;gap:3px;margin:15px 0}.references{font-size:12px}}
@media print{@page{size:A4;margin:17mm 17mm 19mm}html[lang="en"] body{font-size:9.6pt;line-height:1.6}body{background:white;color:var(--ink);font-size:10pt;line-height:1.66}header,.downloads,.footer,.figure-larger{display:none}.paper{max-width:none;margin:0;padding:0}.issue-meta{font-size:7pt;margin-bottom:10pt}h1{font-size:25pt;line-height:1.35;margin-bottom:12pt}p.dek{font-size:11.5pt;line-height:1.6;margin-bottom:12pt}p{margin:0 0 10.5pt;orphans:3;widows:3}h2{font-size:15.8pt;line-height:1.4;padding-top:9pt;margin:22pt 0 10pt;break-after:avoid}h2+p{break-inside:avoid}.byline-disclosure{font-size:7pt;padding:7pt 0;margin:12pt 0 15pt}.hero{margin:16pt 0 18pt}.hero img{max-height:82mm;object-fit:contain}figure{margin:15pt 0 18pt;break-inside:avoid}figure picture img{max-height:142mm;object-fit:contain}figure figcaption{padding:6pt 0 0;font-size:7.5pt;line-height:1.65}.equation{font-size:12pt;padding:10pt 8pt;margin:13pt 0 16pt}.theory-note{font-size:8.5pt;line-height:1.7;padding:9pt 0;margin:14pt 0 17pt;break-inside:avoid}.theory-note summary{font-size:9pt}.theory-note p{margin:9pt 0 0}.references{font-size:8pt;line-height:1.7}.references p{margin-bottom:10pt;break-inside:avoid}.authoring-disclosure{font-size:7.4pt;line-height:1.5;padding:10pt 13pt;margin-top:16pt;break-inside:auto}.authoring-disclosure h2{font-size:12pt;margin-bottom:10pt}.authoring-disclosure dl>div{grid-template-columns:92pt 1fr;gap:9pt;margin:3.5pt 0;break-inside:avoid}.authoring-disclosure p{margin-top:6pt}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''

def build():
    license_text=(ART/'font-license.txt').read_text().replace('*/','')
    css='/* '+license_text+' */\n'+font_css()+'\n'+CSS
    results=[]
    for lang in ['ko','en']:
        ko=lang=='ko'; source=ROOT/'reports'/f'review_{lang}.md'
        text=source.read_text(encoding='utf-8')
        if re.search(r'/Users/|file://|<script\b',text):raise ValueError('Private or executable source input')
        lines=text.splitlines();title=lines[0][2:];dek=lines[2].strip('*')
        text=text.replace(lines[2],f'<p class="dek">{esc(dek)}</p>',1)
        body=markdown.markdown(text,extensions=['tables','sane_lists'])
        head,refs=body.split('<h2>'+('참고문헌' if ko else 'References')+'</h2>',1)
        assert len(re.findall(r'id="ref-\d+"',refs))==13
        def cite(m):
            return '<span class="cite">['+','.join(f'<a role="doc-biblioref" href="#ref-{n.strip()}">{n.strip()}</a>' for n in m[1].split(','))+']</span>'
        head=re.sub(r'\[(\d+(?:,\s*\d+)*)\]',cite,head)
        head=head.replace('[8, Table I]','<span class="cite">[<a role="doc-biblioref" href="#ref-8">8</a>, Table I]</span>')
        body=head+'<h2 id="references">'+('참고문헌' if ko else 'References')+'</h2><div class="references">'+refs+'</div>'
        body=body.replace('../artifacts/figures/','').replace('../artifacts/','')
        def larger(m):
            filename=re.search(r'src="([^"]+\.svg)"',m[0])[1]
            label='크게 보기' if ko else 'View larger'
            return m[0].replace('</figcaption>',f' <a class="figure-larger" href="{filename}" target="_blank" rel="noopener">{label}</a></figcaption>')
        body=re.sub(r'<figure(?![^>]*class="hero")[\s\S]*?</figure>',larger,body)

        byline=f'<p class="byline-disclosure">'+('책임 편집: 김현중 · AI 보조 작성: Codex' if ko else 'Responsible editor: Hyun-Jung Kim · AI assistance: Codex')+f' · {DATE} · '+('조사·초안 2026-11-20 / 판본·출판 확인 2026-11-22' if ko else 'Research/draft 2026-11-20 / edition and production checks 2026-11-22')+' · <a href="#authoring-disclosure">'+('작성·검증 정보' if ko else 'Production and verification')+'</a></p>'
        body=re.sub(r'(<p class="dek">.*?</p>)',lambda m:m[0]+byline,body,count=1)
        url=BASE+('' if ko else 'en/');other=BASE+('en/' if ko else '')
        desc=('AI에게 일을 맡기면 짧은 결과 뒤로 탐색·계산·검증과 실패한 시도가 지나간다. 정보와 물리적 에너지의 흐름을 따라가며, 검증된 성과와 자원 예산·환경 부담을 함께 판단할 기준을 살핀다.' if ko else 'A coding agent can spend far more computation than its final edit reveals. Following information and physical energy through searching, memory, verification and failure shows how reliable results, resource budgets and environmental costs can be evaluated together.')
        top='<header><a class="brand" href="https://infant83.io/AI_Tech_Review/">'+BRAND.upper()+'</a><nav class="header-links" aria-label="'+('언어와 다운로드' if ko else 'Language and downloads')+'"><span lang="'+lang+'" aria-current="page">'+('한국어' if ko else 'English')+'</span><a href="'+other+'" hreflang="'+('en' if ko else 'ko')+'">'+('English' if ko else '한국어')+'</a><a href="review_'+lang+'.pdf">PDF ↓</a><a href="https://infant83.io/AI_Tech_Review/methods/">'+('작성 원칙' if ko else 'Methods')+'</a></nav></header>'
        document=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="author" content="{'김현중' if ko else 'Hyun-Jung Kim'}"><meta name="evidence-cutoff" content="{DATE}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}hero.png"><meta property="article:published_time" content="{DATE}"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ko" href="{BASE}"><link rel="alternate" hreflang="en" href="{BASE}en/"><link rel="alternate" hreflang="x-default" href="{BASE}"><link rel="stylesheet" href="review.css"></head><body>{top}<main class="paper"><div class="issue-meta">RESEARCH LETTER · {DATE} · {'정보 · 계산 · 에너지' if ko else 'INFORMATION · COMPUTATION · ENERGY'}</div><article>{body}{disclosure(lang)}</article><div class="downloads"><a href="review_{lang}.pdf">{'한국어 PDF 내려받기' if ko else 'Download English PDF'}</a><a href="{other}">{'English version' if ko else '한국어판'}</a></div><footer class="footer">{BRAND} · {DATE}</footer></main></body></html>
'''
        dest=DIST/('' if ko else 'en');dest.mkdir(parents=True,exist_ok=True)
        assets=set(re.findall(r'(?:src|srcset)="([^"#]+)"',document))
        expected={'hero.png'}|{f'fig{n}_{variant}'+('' if ko else '_en')+'.svg' for n in range(1,6) for variant in ['desktop','mobile']}
        assert assets==expected,(assets,expected)
        for name in sorted(assets):
            src=ART/name if name=='hero.png' else ART/'figures'/name
            if name.endswith('.svg'):(dest/name).write_text(embed_svg(src),encoding='utf-8')
            else:shutil.copy2(src,dest/name)
        (dest/'review.css').write_text(css,encoding='utf-8');(dest/'index.html').write_text(document,encoding='utf-8')
        (ART/f'review_{lang}.html').write_text(document,encoding='utf-8')
        results.append({'language':lang,'title':title,'subtitle':dek,'description':desc,'date':DATE,'html_sha256':sha(document.encode()),'assets':sorted(assets),'references':13})
    (ART/'production-html-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False))

if __name__=='__main__':build()
