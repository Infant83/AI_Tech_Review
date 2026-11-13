# -*- coding: utf-8 -*-
"""Build a compact PDF series index and its explicit public unit registry."""
import hashlib
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://infant83.io/AI_Tech_Review/'
TITLE = 'Classiq QAE 온보딩 시리즈'
EN_TITLE = 'Classiq QAE Onboarding Series'
SUMMARY = ('고객의 질문을 계산 문제로 옮기는 데 필요한 양자컴퓨팅의 원리와 수학을 공부합니다. '
           '상태·측정과 에너지 최적화부터 입출력·반복을 포함한 계산 비용까지, 회차별 PDF에서 유도와 문제·해설을 읽고 필기할 수 있습니다.')
EN_SUMMARY = ('Study the quantum principles and mathematics needed to turn a customer’s question into a computational problem. '
              'This independent Korean series covers quantum states, measurement, energy optimization and the total cost of computation, including input/output and repeated runs, using PDFs with derivations, exercises and worked answers.')
INDEX_UPDATED = '2026-11-13'
PLANNED_NEXT = dict(id='L008', status='planned-not-published', topic='Python SDK·Studio·Qmod 프로그램 구조')
DETAILS = {
    'L001': dict(
        short='문제 명세와 첫 검산', en='Problem specifications and first checks',
        summary='고객이 원하는 결과를 입력·출력·허용오차로 명세하고, 두 준위 모형의 고유값과 변분 상태의 에너지 기댓값을 비교합니다.',
        summary_en='Specify the desired result through inputs, outputs and tolerances, then compare the eigenvalues of a two-level model with the energy expectation of a variational state.',
        topics=['문제 명세', '고전 기준선', 'Hamiltonian', 'VQE', '제약·벌점', '금융·전자구조'],
        exercise_count=6, exercise_page=20, answer_page=21, glossary_page=22, reference_page=23,
        intro='고객이 원하는 물성이나 비용을 먼저 입력·출력·허용오차로 적는다. 두 준위 Hamiltonian의 정확 고유값과 변분 상태의 기댓값을 비교한 뒤, 같은 비교 조건을 최적화·금융·AMS/ADF·OLED 사례에 적용한다.'),
    'L002': dict(
        short='복소 벡터·기저·텐서곱', en='Complex vectors, bases and tensor products',
        summary='복소 내적과 기저 변환을 익히고, 텐서곱으로 두 큐비트 상태를 구성합니다. 기저를 바꾼 좌표와 실제 상태의 변화를 구별합니다.',
        summary_en='Learn complex inner products and changes of basis, then construct two-qubit states with tensor products. Distinguish a change of coordinates from a change of state.',
        topics=['복소 내적', '정규화', '상대 위상', '기저 변환', '텐서곱', 'AO 중첩 행렬'],
        exercise_count=8, exercise_page=16, answer_page=16, glossary_page=18, reference_page=19,
        intro='복소 내적의 켤레와 정규화에서 출발해 같은 상태의 좌표를 바꾸는 일과 상태 자체를 바꾸는 일을 구별한다. 두 큐비트의 계 순서와 텐서곱을 계산하고, 비직교 AO 기저의 겹침 행렬을 선택 읽기로 연결한다.'),
    'L003': dict(
        short='관측량·Pauli·유니터리', en='Observables, Pauli operators and unitaries',
        summary='에너지 행렬을 관측량으로 읽고 유니터리 시간발전으로 옮기는 과정을 다룹니다. Euler·Trotter 근사의 오차를 작은 행렬로 확인합니다.',
        summary_en='Study an energy matrix as an observable and use it to construct unitary time evolution. Examine Euler and Trotter approximation errors with small matrices.',
        topics=['선형 연산자', 'Hermitian', '고유값', 'Pauli 전개', '시간발전', 'Euler·Trotter'],
        exercise_count=8, exercise_page=15, answer_page=15, glossary_page=17, reference_page=18,
        intro='같은 에너지 행렬을 관측량으로 읽을 때와 게이트로 구현할 때 필요한 검사를 나눈다. 고유공간의 측정 확률, Pauli 전개, 정확한 시간발전과 세 회전 분해를 유도한 뒤 Euler 근사와 Trotter 곱공식의 오차를 비교한다.'),
    'L004': dict(
        short='밀도행렬·측정·얽힘', en='Density matrices, measurement and entanglement',
        summary='한 기저의 확률표가 같아도 양자상태는 다를 수 있습니다. 밀도행렬과 부분추적을 익히고, Bell 상태와 고전 혼합을 상관·얽힘 증인으로 구별합니다.',
        summary_en='Quantum states can differ even when one measurement basis gives the same probabilities. Learn density matrices and partial traces, then distinguish a Bell state from a classical mixture through correlations and an entanglement witness.',
        topics=['밀도행렬', '측정', '순도', '부분추적', 'Bell 상태', '얽힘 증인'],
        exercise_count=8, exercise_page=13, answer_page=14, glossary_page=15, reference_page=16,
        intro='한 기저의 확률표만으로 상태 전체를 정할 수 있는지 묻는다. 중첩과 고전 혼합을 밀도행렬로 표현하고 부분추적·Pauli 상관·얽힘 증인으로 Bell 상태와 분리 혼합을 비교한다.'),
    'L005': dict(
        short='확률·추정·샷·신뢰구간', en='Shot budgets, estimation and confidence intervals',
        summary='허용오차와 신뢰수준을 정해 필요한 샷 수를 계산합니다. 신뢰구간의 경계 사례를 살피고, 에너지 측정과 얽힘 검출에 표본 예산을 적용합니다.',
        summary_en='Calculate shot budgets from a chosen error tolerance and confidence level. Examine confidence intervals at the boundaries, then apply sampling budgets to energy estimation and entanglement detection.',
        topics=['Bernoulli·이항분포', '표준오차·편향', 'Hoeffding', 'Clopper–Pearson', '샷 배분', '얽힘 검출'],
        exercise_count=8, exercise_page=13, answer_page=13, glossary_page=15, reference_page=16,
        intro='반복 측정의 통계 오차와 샷을 늘려도 남는 편향을 구별한다. 고정 샷 신뢰구간의 포함률과 경계 실패를 확인하고, 에너지 측정의 샷 배분과 얽힘 검출의 신뢰 상한을 유도한다.'),
    'L006': dict(
        short='변분 원리·최적화·선택 편향', en='Variational bounds, optimization and selection bias',
        summary='같은 Hamiltonian의 정확한 에너지 기댓값이 바닥에너지보다 낮아질 수 없는 이유를 증명합니다. 수치 최적화와 유한 샷 추정을 비교하고, 가장 낮은 추정값을 고를 때 생기는 편향과 새 표본 검증을 살핍니다.',
        summary_en='Prove why the exact energy expectation of a fixed Hamiltonian cannot fall below its ground energy. Compare numerical optimization with finite-shot estimation, then examine bias from selecting the lowest estimate and validation with fresh samples.',
        topics=['Rayleigh 몫', '변분 원리', '수치 최적화', '선택 편향', '검증 표본', '비직교 기저·DFT'],
        exercise_count=8, exercise_page=12, answer_page=13, glossary_page=14, reference_page=15,
        intro='같은 Hamiltonian의 변분 상한을 고유값 전개로 증명하고 상태족 제한과 최적화 오차를 나눈다. 두 준위 모형에서 정확해·경사하강법·유한 샷 추정을 비교한 뒤, 최소 추정값 선택의 하향 편향과 새 표본 검증을 다룬다.'),
    'L007': dict(
        short='오라클·Grover·입출력 비용', en='Oracle queries, input/output and total cost',
        summary='오라클 질의 수의 개선과 실제 계산 시간의 차이를 살핍니다. Grover 회전과 역계산을 익히고, 입력 준비·반복 측정·고전 처리를 포함한 가상 비용 모형을 같은 조건에서 비교합니다.',
        summary_en='Distinguish fewer oracle queries from a shorter end-to-end computation. Learn Grover rotations and uncomputation, then compare a hypothetical cost model that includes input preparation, repeated measurements and classical processing under matched assumptions.',
        topics=['계산 복잡도', '오라클·역계산', 'Grover 회전', '상태 준비', '입출력·샷 예산', '전체 비용·상각'],
        exercise_count=8, exercise_page=12, answer_page=13, glossary_page=14, reference_page=15,
        intro='후보 수와 입력 길이, 오라클 질의·게이트·깊이·전체 시간을 구별한다. Grover 회전과 역계산을 유도하고 상태 준비·출력 통계·샷 예산을 전체 비용에 연결한다. 같은 입력·정확도·성공기준의 가상 비용 비교이며 실측 속도나 실용 도입 임계값을 뜻하지 않는다.'),
}
REFERENCES = [
    ('Classiq, Quantum Application Engineer (accessed 5 November 2026).', 'https://www.classiq.io/positions/position-84_27e'),
    ('Classiq, Qmod Tutorial - Part I (accessed 5 November 2026).', 'https://docs.classiq.io/getting-started/classiq_tutorial/Qmod_tutorial_part1'),
    ('Classiq, Quantum Types (accessed 5 November 2026).', 'https://docs.classiq.io/qmod-reference/language-reference/quantum-types'),
    ('Classiq, Observe (accessed 5 November 2026).', 'https://docs.classiq.io/user-guide/execution/observe'),
    ('IBM Quantum Learning, Quantum information, Basics of Quantum Information: Single systems (accessed 5 November 2026).', 'https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information'),
    ('J. Watrous, The Theory of Quantum Information (Cambridge University Press, Cambridge, 2018).', 'https://cs.uwaterloo.ca/~watrous/TQI/'),
    ('J. Preskill, Lecture Notes for Ph219/CS219: Quantum Information, Chapter 2: Foundations I: States and Ensembles (July 2015).', 'https://www.preskill.caltech.edu/ph219/chap2_15.pdf'),
    ('A. M. Childs, Y. Su, M. C. Tran, N. Wiebe, and S. Zhu, Theory of Trotter error with commutator scaling, Phys. Rev. X 11, 011020 (2021).', 'https://doi.org/10.1103/PhysRevX.11.011020'),
]
CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#faf9f6;color:#20313c;font:17px/1.8 system-ui,-apple-system,sans-serif}header,main,footer{max-width:980px;margin:auto;padding:28px}header{padding-top:42px;border-bottom:1px solid #d9dedc}h1{font:700 clamp(29px,5vw,43px)/1.3 Georgia,serif;margin:16px 0}h2{font-size:25px;line-height:1.4;margin-top:0}h3{font-size:21px;line-height:1.5;margin:10px 0 16px}a{color:#096e6b;text-underline-offset:3px}nav,.actions,.pdf-sections{display:flex;flex-wrap:wrap;gap:8px 12px}.eyebrow{color:#69776e;font-size:13px;letter-spacing:.06em}.meta,.pdf-sections{color:#5c6c70;font-size:14px}section{margin-bottom:38px;scroll-margin-top:24px}article{background:white;border:1px solid #d9dedc;padding:24px;margin:16px 0;border-radius:10px;scroll-margin-top:24px}.unit-summary{font-size:15px;line-height:1.75;color:#5c6c70;margin:0 0 12px}.actions a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px;padding:2px 0;border:0;text-decoration:none;font-size:13px;font-weight:650}.actions .primary{color:#096e6b}.actions a:hover{text-decoration:underline;text-underline-offset:4px}.pdf-sections{margin-top:12px;gap:4px 20px}.pdf-sections a{display:inline-flex;align-items:center;min-height:44px}details{border-top:1px solid #d9dedc;padding-top:16px}summary{cursor:pointer;font-weight:650;min-height:44px}details p{font-size:14px;color:#5c6c70}ol.references{padding-left:24px;font-size:14px}.references li{padding:6px 0;overflow-wrap:anywhere}code{overflow-wrap:anywhere}footer{border-top:1px solid #d9dedc;font-size:14px}header p,article p,footer{word-break:keep-all;overflow-wrap:anywhere}@media(max-width:600px){body{font-size:16px}header,main,footer{padding:24px 18px}header{padding-top:28px}article{padding:18px}h2{font-size:23px}h3{font-size:20px}.actions{gap:0 16px}.actions a{font-size:13px;padding:2px 0}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}'''


def escape(value):
    return html.escape(str(value), quote=True)


def unit_card(unit, english=False):
    prefix = '../' if english else ''
    reader = '../../reader/' if english else '../reader/'
    reader += '?id=' + unit['archive_id'] + ('&amp;lang=en' if english else '')
    pdf = prefix + unit['pdf']
    title = unit['title_en'] if english else unit['title']
    page_label = f"{unit['public_pages']} pages · Korean" if english else f"PDF {unit['public_pages']}쪽 · 한국어"
    actions = (
        ('Read &amp; annotate' if english else '필기하며 읽기', reader, 'primary', ''),
        ('Open PDF' if english else 'PDF 열기', pdf, '', ''),
        ('Download' if english else '다운로드', pdf, '', ' download'),
    )
    buttons = ''.join(f'<a class="{css}" href="{href}"{attr}>{label}</a>' for label, href, css, attr in actions)
    section_links = (
        (f"{unit['exercises']} exercises" if english else f"문제 {unit['exercises']}개", unit['exercise_pdf_page']),
        ('Worked answers' if english else '해설', unit['answer_pdf_page']),
        ('Glossary' if english else '용어색인', unit['glossary_pdf_page']),
    )
    sections = ''.join(f'<a href="{pdf}#page={page}">{label}</a>' for label, page in section_links)
    return f'''<article id="unit-{unit['id'].lower()}">
  <p class="eyebrow">{unit['id']} · <time datetime="{unit['date']}">{unit['date']}</time> · {page_label}</p>
  <h3>{escape(title)}</h3>
  <p class="unit-summary">{escape(unit['summary_en' if english else 'summary'])}</p>
  <div class="actions">{buttons}</div>
  <div class="pdf-sections">{sections}</div>
</article>'''


def course_page(units, english=False):
    language = 'en' if english else 'ko'
    prefix = '../' if english else ''
    home = '../../en/' if english else '../'
    alternate = '../' if english else 'en/'
    title = EN_TITLE if english else TITLE
    summary = EN_SUMMARY if english else SUMMARY
    latest = units[-1]['id']
    total_pages = sum(unit['public_pages'] for unit in units)
    original_pages = sum(unit['original_pages'] for unit in units)
    canonical = BASE + 'lectures/classiq-qae-onboarding/' + ('en/' if english else '')
    refs = ''.join(f'<li id="ref-{i}"><a href="{escape(url)}">{escape(text)}</a></li>' for i, (text, url) in enumerate(REFERENCES, 1))
    metadata = (f'<link rel="canonical" href="{canonical}"><meta property="og:title" content="{title}">'
                f'<meta property="og:description" content="{summary}"><meta property="og:url" content="{canonical}">') if english else ''
    if english:
        guide = (f'Read L001 through {latest} in order. Each PDF contains the full derivations, exercises, worked answers and glossary. '
                 'This independently written Korean course uses QAE to mean Quantum Application Engineer. It is separate from official Classiq training and the '
                 '<a href="../../classiq-talk-series/">Classiq webinar replay notes</a>.')
        scope = f'''<p>The public editions preserve {original_pages} original educational pages and add one disclosure page per unit, giving {total_pages} pages. Personalized context and file-launch actions were removed. Previously published PDF bytes and original page numbers are preserved.</p>
<p>The original source ZIPs for L001–L003 were not retrieved. L004–L007 have local authoring records, which are not republished in this bundle. The original validation suites, including L004's 50, L005's 57, L006's 46 and L007's 48 checks, were not independently rerun for these archive updates. The supplementary script checks 20 finite-matrix conditions from L001–L003 using the Python standard library, with a Frobenius-norm Trotter comparison. No Classiq SDK, synthesis, QPU or molecular/DFT experiment was run.</p>
<p>Responsible editor: Hyun-Jung Kim. AI assistance: OpenAI Codex. Agent public_pdf_qa/auth_audit prepared L001–L003 and their partial recalculation. Agents qae_l004_public, qae_l005_public, qae_l006_public and qae_l007_public checked the respective public editions for privacy, preservation, links and full-page rendering. Agent qae_l005_science separately reviewed L005’s central statistical derivations and selected numerical values. Agent qae_l006_science reviewed L006’s variational, optimization and selection-bias arguments and selected classical calculations. Agent qae_l007_science reviewed L007’s oracle, Grover and total-cost arguments and selected classical calculations; root integrated publication. The qae_course_index agent simplified this index on 6 November 2026. Exact original model and agent identifiers were not retained. Human manuscript review or Classiq approval is not claimed.</p>
<p>References were checked on 5 November 2026 for official web content and source metadata; the books and papers were not newly reread in full. Each PDF retains its detailed references and original source-reading record.</p>'''
        practice = ('<a href="../labs/reference_checks.py" download>Download supplementary code</a> · '
                    '<a href="../labs/results/reference-checks.json">Recorded results</a>')
        future = f"{PLANNED_NEXT['id']} is planned; no lesson or PDF has been published."
    else:
        guide = (f'L001부터 {latest}까지 차례로 선택하세요. 수식·유도·문제·해설·용어색인은 각 회차 PDF에 있습니다. '
                 'QAE는 Quantum Application Engineer를 뜻하며, 이 자료는 공식 Classiq 교육과 별개로 집필한 한국어 독립 학습 과정입니다. '
                 '<a href="../classiq-talk-series/">Classiq 웨비나 다시보기 노트</a>는 별도 시리즈입니다.')
        scope = f'''<p>원판 교육 내용 {original_pages}쪽에 회차별 공개판 안내를 한 쪽씩 더해 총{total_pages}쪽입니다. 개인화 표현·메타데이터·파일 실행 링크를 정리했으며, 기존 공개 회차 PDF의 바이트와 원래 쪽번호를 유지합니다.</p>
<p>L001–L003 원판 ZIP은 수집하지 못했습니다. L004–L007은 로컬 집필·검수 기록을 대조했으며 이 공개 묶음에 원고·ZIP을 추가하지 않았습니다. L004의 원판50개·L005의 원판57개·L006의 원판46개·L007의 원판48개 검사를 포함한 원판 전체 검증을 이번 아카이빙에서 독립 재실행한 것은 아닙니다. 보충 코드는 L001–L003 예제의 작은 행렬20개 조건을 별도로 재계산하며 Trotter 비교에는 Frobenius 노름을 씁니다. Classiq 합성·SDK·QPU나 실제 분자·DFT 실험을 수행한 자료로 표시하지 않습니다.</p>
<p>책임 편집자 김현중 · AI 보조 OpenAI Codex. public_pdf_qa/auth_audit가 L001–L003의 공개판 정제·부분검산을, qae_l004_public·qae_l005_public·qae_l006_public·qae_l007_public이 해당 회차의 공개판 보존·개인정보·링크·전체 조판 검수를 맡았습니다. qae_l005_science는 L005의 핵심 통계 유도와 일부 수치를, qae_l006_science는 L006의 변분·최적화·선택 편향 논증과 일부 고전 계산을, qae_l007_science는 L007의 오라클·Grover·전체 비용 논증과 일부 고전 계산을 별도 검토했고 root가 통합·게시를 담당했습니다. 2026-11-06 회차 선택 화면 개편은 qae_course_index가 수행했습니다. 원 작성 세션의 정확한 모델·에이전트 식별자는 미보존이며, 사람의 원고 감수나 Classiq 승인을 받았다고 주장하지 않습니다.</p>
<p>공식 웹 자료와 서지·판본 정보는 2026-11-05 확인했습니다. 교재·논문 전체를 이번에 다시 정독한 기록은 아닙니다. 회차별 상세 참고문헌과 원판의 읽은 위치는 각 PDF에 보존했습니다.</p>'''
        practice = ('<a href="labs/reference_checks.py" download>보충 코드 다운로드</a> · '
                    '<a href="labs/results/reference-checks.json">실행 결과</a>')
        future = f"{PLANNED_NEXT['id']}는 계획 단계이며 아직 강의나 PDF를 발행하지 않았습니다."
    return f'''<!doctype html>
<html lang="{language}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | AI Tech Review Letters</title><meta name="description" content="{summary}">
{metadata}
<link rel="alternate" hreflang="ko" href="{BASE}lectures/classiq-qae-onboarding/">
<link rel="alternate" hreflang="en" href="{BASE}lectures/classiq-qae-onboarding/en/">
<link rel="alternate" hreflang="x-default" href="{BASE}lectures/classiq-qae-onboarding/">
<link rel="stylesheet" href="{prefix}notes.css?v=20261113-l007">
</head><body>
<header><nav><a href="{home}">{'Lecture notes' if english else '렉처 노트'}</a><a href="{alternate}" lang="{'ko' if english else 'en'}">{'한국어' if english else 'English'}</a></nav>
<p class="eyebrow">{'INDEPENDENT STUDY · KOREAN PDFs' if english else '독립 학습 과정 · 한국어 PDF'}</p>
<h1>{title}</h1><p>{summary}</p>
<p class="meta">L001–{latest} · {f'{len(units)} units · {total_pages} PDF pages' if english else f'{len(units)}회차 · PDF {total_pages}쪽'}</p></header>
<main>
<section id="study-guide"><h2>{'Reading order' if english else '학습 순서'}</h2><p>{guide}</p></section>
<section id="units"><h2>{'Choose a unit' if english else '회차 선택'}</h2>{''.join(unit_card(u, english) for u in units)}</section>
<section id="practice"><h2>{'Supplementary code' if english else '보충 코드'}</h2><p>{practice}</p><p class="meta">{'20 separately recalculated conditions from L001–L003 examples; Python standard library only.' if english else 'L001–L003 예제에서 별도로 재계산한 20개 조건입니다. Python 표준 라이브러리만 사용합니다.'}</p></section>
<section id="references"><details><summary>{'Sources and publication scope' if english else '출처와 작성 범위'}</summary>{scope}<ol class="references">{refs}</ol>
<p><a href="{'../../../' if english else '../../'}methods/">AI Tech Review Editorial Harness 2026.08</a> · <a href="{prefix}unit-registry.json">{'Unit registry' if english else '회차 등록부'}</a></p><p>{future}</p></details></section>
</main><footer><a href="{home}">{'Lecture notes' if english else '렉처 노트 목록'}</a> · <a href="{alternate}">{'Korean series' if english else 'English'}</a></footer>
</body></html>
'''


def main():
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    reports = json.loads((ROOT / 'reports/pdf-production-qa.json').read_text())
    units = []
    for record in reports['units']:
        unit = record['unit']
        detail = DETAILS[unit]
        document_id = Path(record['file']).stem
        if hashlib.sha256((dist / record['file']).read_bytes()).hexdigest() != record['public_sha256']:
            raise ValueError('Public PDF differs from approved edition: ' + record['file'])
        units.append(dict(
            id=unit, date=record['date'], title=record['title'], title_en=detail['en'], archive_id=document_id,
            summary=detail['summary'], summary_en=detail['summary_en'],
            status='available', language='ko', pdf=record['file'], public_pages=record['public_pages'],
            original_pages=record['source_pages'], sha256=record['public_sha256'], topics=detail['topics'],
            exercises=detail['exercise_count'], exercise_pdf_page=detail['exercise_page'], answer_pdf_page=detail['answer_page'],
            glossary_pdf_page=detail['glossary_page'], reference_pdf_page=detail['reference_page']))
    registry = dict(
        format='ai-tech-review-course-registry', version=1, series_id='classiq-qae-onboarding', updated=INDEX_UPDATED,
        title=TITLE, title_en=EN_TITLE, summary=SUMMARY, summary_en=EN_SUMMARY,
        official_Classiq_course=False, latest_unit=units[-1]['id'], units=units,
        planned_next=PLANNED_NEXT,
        source_zip_available=False, original_validation_suite_independently_rerun=False)
    (ROOT / 'unit-registry.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'unit-registry.json', dist / 'unit-registry.json')
    (dist / 'notes.css').write_text(CSS + '\n', encoding='utf-8')
    for name in ['reference_checks.py', 'results/reference-checks.json']:
        target = dist / 'labs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'labs' / name, target)
    (dist / 'index.html').write_text(course_page(units), encoding='utf-8')
    (dist / 'en').mkdir(exist_ok=True)
    (dist / 'en/index.html').write_text(course_page(units, english=True), encoding='utf-8')
    # A presentation-only edit does not rewrite the previous source-check record.
    entries = []
    for unit in units:
        detail = DETAILS[unit['id']]
        entries.append(dict(
            id=unit['archive_id'], date=unit['date'], series='lecture-notes',
            title='Classiq QAE ' + unit['id'] + ': ' + unit['title'],
            summary=detail['intro'] + f' {unit["exercises"]}개 문제와 해설·용어색인, 공개판 안내를 포함한 {unit["public_pages"]}쪽 한국어 독립 학습 노트입니다.',
            language='ko', file='files/' + unit['pdf'], tags=['양자컴퓨팅', 'Classiq', 'QAE', '선형대수', '렉처 노트'],
            public_reviewed=True, title_en='Classiq QAE ' + unit['id'] + ': ' + unit['title_en'],
            summary_en=f'Independent Korean study notes on {unit["title_en"].lower()}, with {unit["exercises"]} exercises, worked answers and a glossary. Public edition: {unit["public_pages"]} pages.',
            source_title='Classiq QAE 독립 학습 과정 · ' + unit['id'] + ' v1.0'))
    (ROOT / 'reports/archive-entries.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Built compact PDF series index and registry for', len(units), 'units')


if __name__ == '__main__':
    main()
