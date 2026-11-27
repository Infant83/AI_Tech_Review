"""Build only the reviewed bilingual course guide and explicit PDF registry.

PDF bytes, archive imports and publication are owned by the existing publisher.
This command verifies the frozen public PDF hashes before writing guide assets.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parent
DATE = "2026-11-27"
SERIES_ID = "photonic-fault-tolerant-computing"
OWNER_ID = f"{DATE}-{SERIES_ID}-notes-ko"
BASE_URL = "https://infant83.io/AI_Tech_Review/"
PUBLIC_TEXT = {'course': {'title_ko': '큐비트에서 광자 내결함성 계산까지',
            'title_en': 'From Qubits to Photonic Fault-Tolerant Computing',
            'topic_ko': '양자정보·오류정정·광자 양자컴퓨팅',
            'topic_en': 'Quantum information, error correction and photonic computing',
            'summary_ko': '상대 위상과 측정에서 출발해 오류정정, 논리연산과 매직 상태, 2차원 컬러 코드, 측정기반 계산과 광자 융합을 잇는 7단계 자습 강의입니다. '
                          '코드·회로·디코더·광원과 제어를 함께 보며 신뢰성과 자원 비용을 판단합니다.',
            'summary_en': 'A seven-level self-study course from phase and measurement through error '
                          'correction, logical operations, magic states, 2D color codes, measurement-based '
                          'computing and photonic fusion. It connects codes, circuits, decoders, photon '
                          'sources and control to the reliability and resource costs of a computation.',
            'archive_id': '2026-11-27-photonic-fault-tolerant-computing-notes-ko',
            'date': '2026-11-27',
            'language': 'ko',
            'format_note_ko': '독립 자습용 저술이며 실제 강연이나 문답의 채록이 아닙니다. 한국어 PDF 통합본과 단계별 분리본을 제공합니다.',
            'format_note_en': 'An independently authored self-study monograph, rather than a transcript of a '
                              'live lecture or Q&A. Korean PDFs are available as a compilation and seven '
                              'separate levels.'},
 'levels': [{'unit': 1,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l001-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '양자정보의 기초 토대',
             'title_en': 'Foundations of Quantum Information',
             'topic_ko': '상태·측정·얽힘·회로',
             'topic_en': 'States, measurements, entanglement and circuits',
             'summary_ko': '상대 위상이 측정 확률을 바꾸는 간섭에서 출발해 블로흐 구, 사영 측정, 벨 얽힘과 텔레포테이션을 계산합니다. 게이트의 작용과 측정 결과를 '
                           '연결하며 다음 단계에서 보호할 양자정보를 정의합니다.',
             'summary_en': 'Starting with interference, this level shows how relative phase changes '
                           'measurement probabilities. Bloch vectors, projective measurements, Bell '
                           'entanglement and teleportation connect gate operations to the quantum '
                           'information that later levels protect.'},
            {'unit': 2,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l002-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '노이즈와 내결함성의 필요성',
             'title_en': 'Noise and the Need for Fault Tolerance',
             'topic_ko': '밀도 연산자·채널·임계값',
             'topic_en': 'Density operators, channels and thresholds',
             'summary_ko': '환경과의 상관관계가 결맞음을 약화시키는 과정을 밀도 연산자와 양자채널로 표현합니다. 복제 불가능성과 연속적인 오류를 검토하고, 잡음 가정 아래 '
                           '보호 자원을 늘려 논리 실패를 줄이는 임계값 정리의 뜻을 설명합니다.',
             'summary_en': 'Density operators and quantum channels describe how correlations with the '
                           'environment weaken coherence. No-cloning, continuous errors and a simple '
                           'concatenation model explain how added protection can reduce logical failure '
                           'under specified noise assumptions.'},
            {'unit': 3,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l003-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '양자오류정정의 핵심 원리',
             'title_en': 'Core Principles of Quantum Error Correction',
             'topic_ko': '부호화·신드롬·디코딩',
             'topic_en': 'Encoding, syndromes and decoding',
             'summary_ko': '반복·쇼어·스틴 코드로 논리정보를 읽지 않고 오류의 흔적만 얻는 방법을 익힙니다. 안정자와 정정 조건에서 패리티 회로, 플래그, 디코딩으로 '
                           '이어지며 코드 거리·회로 안전성·고전 처리 속도를 함께 살핍니다.',
             'summary_en': 'Repetition, Shor and Steane codes show how to reveal error syndromes while '
                           'preserving logical information. Stabilizers and correction conditions lead to '
                           'parity circuits, flags and decoding, with separate attention to code distance, '
                           'circuit safety and classical processing.'},
            {'unit': 4,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l004-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '논리연산과 매직 상태',
             'title_en': 'Logical Operations and Magic States',
             'topic_ko': '횡단 게이트·격자수술·자원 비용',
             'topic_en': 'Transversal gates, lattice surgery and resource costs',
             'summary_ko': '부호화를 유지하는 횡단 게이트와 공동 논리 측정을 계산하고, Eastin–Knill 정리가 남기는 보편성의 제약을 살핍니다. 매직 상태 '
                           '주입·증류와 오류 예산을 통해 큐비트 수뿐 아니라 공장 처리량과 계산 시간까지 비교합니다.',
             'summary_en': 'Transversal gates and joint logical measurements perform operations within an '
                           'encoded space. The Eastin–Knill restriction motivates magic-state injection and '
                           'distillation, linking failure budgets to physical qubits, factory throughput and '
                           'computation time.'},
            {'unit': 5,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l005-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '위상 양자코드와 2차원 컬러 코드',
             'title_en': 'Topological Quantum Codes and 2D Color Codes',
             'topic_ko': '국소 검사·횡단 Clifford·회로와 디코더',
             'topic_en': 'Local checks, transversal Clifford gates, circuits and decoders',
             'summary_ko': '표면코드의 오류 사슬과 컬러 코드의 세 색 면 검사를 비교합니다. 7큐비트 예제로 횡단 위상 게이트의 부호 조건을 확인하고, 높은 검사 가중치와 '
                           '색·시간 상관관계가 회로 및 디코더 설계에 주는 비용을 설명합니다.',
             'summary_en': 'Surface-code error chains are compared with the three-color face checks of color '
                           'codes. A seven-qubit example exposes the phase conditions of transversal gates, '
                           'while check weight and correlations across colors and time connect circuit '
                           'design to decoding costs.'},
            {'unit': 6,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l006-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '측정기반 양자컴퓨팅',
             'title_en': 'Measurement-Based Quantum Computing',
             'topic_ko': '그래프 상태·적응형 측정·파울리 프레임',
             'topic_en': 'Graph states, adaptive measurements and Pauli frames',
             'summary_ko': '한 비트 텔레포테이션의 측정 분기를 직접 전개한 뒤 그래프 상태와 파울리 프레임으로 확장합니다. 앞선 결과에 맞춰 측정각을 바꾸는 계산으로 '
                           '무작위 분기를 같은 논리연산에 맞추고, 회로를 측정 패턴으로 옮깁니다.',
             'summary_en': 'One-bit teleportation is derived branch by branch and extended to graph states '
                           'and Pauli frames. Adaptive measurement angles align random outcomes with the '
                           'same logical operation, providing a route from circuits to measurement '
                           'patterns.'},
            {'unit': 7,
             'archive_id': '2026-11-27-photonic-fault-tolerant-computing-l007-notes-ko',
             'date': '2026-11-27',
             'language': 'ko',
             'title_ko': '광자 플랫폼과 위상학적 MBQC',
             'title_en': 'Photonic Platforms and Topological MBQC',
             'topic_ko': '융합·손실·RHG·FBQC',
             'topic_en': 'Fusion, loss, RHG and FBQC',
             'summary_ko': '광자 간섭과 Bell 융합의 성공·실패·손실이 남기는 정보를 구별하고 RHG의 셀 패리티로 오류 추론을 연결합니다. 융합기반 계산과 양자점 '
                           '광원의 2026년 청사진을 통해 광학 깊이·피드포워드·자원 공급을 함께 검토합니다.',
             'summary_en': 'Photon interference and Bell fusion distinguish successful outcomes, heralded '
                           'failures and loss. RHG cell parities connect these records to error inference; '
                           'fusion-based computing and a 2026 quantum-dot blueprint then bring optical '
                           'depth, feedforward and resource supply into one design problem.'}],
 'reading_path': {'order': [1, 2, 3, 4, 5, 6, 7],
                  'sections': 28,
                  'quiz_count': 4,
                  'quiz_distribution': {'1': 2, '2': 1, '3': 1, '4': 0, '5': 0, '6': 0, '7': 0},
                  'glossary': 'No standalone glossary; bilingual terms appear on first use; compilation page '
                              '2 has a notation guide.',
                  'prerequisites_ko': '고등학교 수준의 복소수와 행렬 곱셈',
                  'prerequisites_en': 'High-school complex numbers and matrix multiplication'}}

# Filled from the completed, separately recorded scientific/source review.
DISCLOSURE = {'ko': ['책임 편집자는 김현중이며, AI 보조에는 OpenAI Codex를 사용했다. 이번 아카이빙에서 편집부(AEDAUT)의 ftqc_science가 과학 검토와 별도 계산을, '
        'ftqc_pdf가 공개판 보존·링크·조판 검수를, pqc_archive_structure가 한영 학습 안내와 자료 연결을 맡았고 root가 발행을 통합했다. 정확한 모델 식별자는 '
        '미보존이다.',
        '별도로 작성한 Python 표준 라이브러리 검산 32항목(유한 입력·분기·이진 패턴 808건)을 실행했다. 최대 4큐비트의 상태벡터·16차원 이하 행렬, 7·15자리의 짧은 이진 '
        '패턴과 스칼라 계산으로 텔레포테이션·채널·신드롬·측정형 CNOT·매직 상태 주입·컬러 코드의 위상 부호·MBQC 적응 분기·Bell 융합·RUS·RHG 셀 경계를 점검했다. '
        '원저자가 보고한 94개 검산 묶음은 기록만 검토했으며 이번에 재실행하지 않았다. 디코더·임계값 시뮬레이션, SDK·QPU·광학 장치 실험은 수행하지 않았다. 사람의 원고 감수는 '
        '별도로 확인되지 않았다.',
        '편집 기준은 ATRL Editorial Method 2026.08, 과학 설명과 시각 전달 준칙 1.0 및 APS 참고문헌 기준이다.'],
 'en': ['Hyun-Jung Kim is the responsible editor, with AI assistance from OpenAI Codex. For this archival '
        'edition, AEDAUT’s ftqc_science reviewed the science and ran separate calculations; ftqc_pdf '
        'reviewed public PDF preservation, links and layout; pqc_archive_structure prepared the bilingual '
        'course guide and document connections; root integrated publication. The exact model identifier was '
        'not retained.',
        'A separately written Python standard-library check set passed 32 named items covering 808 finite '
        'inputs, branches and binary patterns. It used at most four-qubit state vectors and matrices of '
        'dimension 16, short 7-/15-position binary patterns and scalar arithmetic to check teleportation, '
        'channels, syndromes, measurement-based CNOT, magic-state injection, color-code phase signs, '
        'adaptive MBQC branches, Bell fusion, truncated RUS and RHG cell boundaries. The original author’s '
        'reported 94-check set was reviewed as an existing record and was not rerun. No full decoder or '
        'threshold simulation, SDK/QPU run or physical optical experiment was performed. A separate human '
        'manuscript review was not established.',
        'Editorial standards: ATRL Editorial Method 2026.08, Scientific Explanation and Visual Communication '
        'Direction 1.0, and APS reference style.']}
REFERENCES = [{'citation': 'J. Preskill, Lecture Notes for Physics 219: Quantum Information, Chapter 2: Foundations I '
              '(California Institute of Technology, 2015).',
  'url': 'https://www.preskill.caltech.edu/ph219/chap2_15.pdf',
  'levels': [1, 2]},
 {'citation': 'D. Gottesman, Stabilizer codes and quantum error correction, Ph.D. thesis, California '
              'Institute of Technology (1997).',
  'url': 'https://arxiv.org/abs/quant-ph/9705052',
  'levels': [3]},
 {'citation': 'B. Eastin and E. Knill, Restrictions on transversal encoded quantum gate sets, Phys. Rev. '
              'Lett. 102, 110502 (2009).',
  'url': 'https://doi.org/10.1103/PhysRevLett.102.110502',
  'levels': [4]},
 {'citation': 'S. Bravyi and A. Kitaev, Universal quantum computation with ideal Clifford gates and noisy '
              'ancillas, Phys. Rev. A 71, 022316 (2005).',
  'url': 'https://doi.org/10.1103/PhysRevA.71.022316',
  'levels': [4]},
 {'citation': 'H. Bombín and M. A. Martin-Delgado, Topological quantum distillation, Phys. Rev. Lett. 97, '
              '180501 (2006).',
  'url': 'https://doi.org/10.1103/PhysRevLett.97.180501',
  'levels': [5]},
 {'citation': 'S.-H. Lee, A. Li, and S. D. Bartlett, Color code decoder with improved scaling for correcting '
              'circuit-level noise, Quantum 9, 1609 (2025).',
  'url': 'https://doi.org/10.22331/q-2025-01-27-1609',
  'levels': [5]},
 {'citation': 'R. Raussendorf, D. E. Browne, and H. J. Briegel, Measurement-based quantum computation on '
              'cluster states, Phys. Rev. A 68, 022312 (2003).',
  'url': 'https://doi.org/10.1103/PhysRevA.68.022312',
  'levels': [6]},
 {'citation': 'R. Raussendorf, J. Harrington, and K. Goyal, Topological fault-tolerance in cluster state '
              'quantum computation, New J. Phys. 9, 199 (2007).',
  'url': 'https://doi.org/10.1088/1367-2630/9/6/199',
  'levels': [6, 7]},
 {'citation': 'S. Bartolucci, P. Birchall, H. Bombín, H. Cable, C. Dawson, M. Gimeno-Segovia, E. Johnston, '
              'K. Kieling, N. Nickerson, M. Pant, F. Pastawski, T. Rudolph, and C. Sparrow, Fusion-based '
              'quantum computation, Nat. Commun. 14, 912 (2023).',
  'url': 'https://doi.org/10.1038/s41467-023-36493-1',
  'levels': [7]},
 {'citation': 'M. L. Chan, A. A. Capatos, P. Lodahl, A. S. Sørensen, and S. Paesani, Practical blueprint for '
              'low-depth photonic quantum computing with quantum dots, arXiv:2507.16152v2 (2026).',
  'url': 'https://arxiv.org/abs/2507.16152v2',
  'levels': [7]}]


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_public_editions(report_path: Path, pdf_dir: Path) -> dict[str, dict]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise ValueError("Completed public PDF QA is required")
    expected = {OWNER_ID, *(level["archive_id"] for level in PUBLIC_TEXT["levels"])}
    indexed = {}
    for edition in report.get("editions", []):
        identifier = edition.get("identifier")
        if identifier not in expected or identifier in indexed:
            raise ValueError("Public PDF report contains an unexpected or duplicate edition")
        pages, checksum = edition.get("public_pages"), edition.get("public_sha256")
        filename = edition.get("file")
        if (type(pages) is not int or pages < 1 or filename != identifier + ".pdf"
                or not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum)):
            raise ValueError("Public PDF report is incomplete")
        source = pdf_dir / filename
        if source.is_symlink() or not source.is_file():
            raise ValueError("Missing frozen public PDF")
        payload = source.read_bytes()
        if (hashlib.sha256(payload).hexdigest() != checksum
                or len(payload) != edition.get("public_bytes")):
            raise ValueError("Public PDF bytes differ from the completed QA report")
        indexed[identifier] = {"pages": pages, "sha256": checksum}
    if set(indexed) != expected:
        raise ValueError("Public PDF report must cover the compilation and all seven levels")
    return indexed


def course_registry(editions: dict[str, dict]) -> dict:
    course = PUBLIC_TEXT["course"]
    return {
        "format": "ai-tech-review-course-registry", "version": 1,
        "series_id": SERIES_ID, "updated": DATE,
        "title": course["title_ko"], "title_en": course["title_en"],
        "summary": course["summary_ko"], "summary_en": course["summary_en"],
        "compilation_archive_id": OWNER_ID,
        "compilation_public_pages": editions[OWNER_ID]["pages"],
        "latest_unit": "L007",
        "units": [{
            "id": f"L{level['unit']:03d}", "archive_id": level["archive_id"],
            "date": level["date"], "language": "ko", "status": "available",
            "title": level["title_ko"], "title_en": level["title_en"],
            "summary": level["summary_ko"], "summary_en": level["summary_en"],
            "pdf": level["archive_id"] + ".pdf",
            "public_pages": editions[level["archive_id"]]["pages"],
            "sha256": editions[level["archive_id"]]["sha256"],
        } for level in PUBLIC_TEXT["levels"]],
    }


def actions(identifier: str, language: str, label: str) -> str:
    en = language == "en"
    query = {"id": identifier}
    if en:
        query["lang"] = "en"
    reader = ("../../" if en else "../") + "reader/?" + urlencode(query)
    pdf = ("../../../" if en else "../../") + "archive/files/" + identifier + ".pdf"
    annotation = "Annotate" if en else "필기"
    download = "Download" if en else "다운로드"
    return (f'<div class="lecture-actions"><a class="lecture-primary" href="{escape(reader)}" '
            f'aria-label="{escape(label)} {annotation}">{annotation} →</a>'
            f'<a href="{escape(pdf)}" target="_blank" rel="noopener" '
            f'aria-label="{escape(label)} PDF">PDF ↗</a>'
            f'<a href="{escape(pdf)}" download aria-label="{escape(label)} {download}">{download} ↓</a></div>')


def reviewed_references() -> list[dict]:
    if not REFERENCES or any(not DISCLOSURE[language] for language in ("ko", "en")):
        raise ValueError("Completed scientific disclosure and primary references are required")
    for item in REFERENCES:
        parsed = urlsplit(item["url"])
        if (parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password
                or not item["citation"] or not item["levels"]
                or any(type(level) is not int or not 1 <= level <= 7 for level in item["levels"])):
            raise ValueError("Invalid reviewed primary reference")
    return sorted(REFERENCES, key=lambda item: min(item["levels"]))


def render_page(registry: dict, language: str) -> str:
    en = language == "en"
    suffix = "en" if en else "ko"
    root_prefix = "../../../" if en else "../../"
    course = PUBLIC_TEXT["course"]
    references = reviewed_references()
    title, summary = course["title_" + suffix], course["summary_" + suffix]
    language_href = "../" if en else "en/"
    canonical = BASE_URL + "lectures/" + SERIES_ID + ("/en/" if en else "/")
    # The publisher injects the Korean canonical; each guide owns its navigation.
    english_meta = (f'<link rel="canonical" href="{escape(canonical)}">'
                    f'<meta property="og:type" content="article"><meta property="og:title" content="{escape(title)}">'
                    f'<meta property="og:description" content="{escape(summary)}">'
                    f'<meta property="og:url" content="{escape(canonical)}">') if en else ""
    navigation = ((f'<nav aria-label="Course navigation"><a href="{root_prefix}lectures/en/">← Lecture notes</a>'
                   '<a href="#study-guide">Reading guide</a><a href="#units">Levels</a>'
                   '<a href="#references">References</a><a href="#publication">Preparation and review</a></nav>') if en
                  else (f'<nav aria-label="강의 안내"><a href="{root_prefix}lectures/">← 렉처 노트 목록</a>'
                        '<a href="#study-guide">학습 순서</a><a href="#units">단계별 강의</a>'
                        '<a href="#references">참고문헌</a><a href="#publication">작성과 검수</a></nav>'))
    units = []
    for level, unit in zip(PUBLIC_TEXT["levels"], registry["units"]):
        label = f"Level {level['unit']}"
        reference_links = ' '.join(f'<a href="#ref-{number}">[{number}]</a>'
                                  for number, reference in enumerate(references, 1) if level["unit"] in reference["levels"])
        reference_note = (("Primary references " if en else "원전 ") + reference_links) if reference_links else ""
        pages = f"{unit['public_pages']} pages" if en else f"{unit['public_pages']}쪽"
        units.append(f'''<li id="level-{level['unit']}" data-lecture-unit="{unit['id']}">
        <p class="unit-number">{label} <span>PDF {pages}</span></p>
        <h3>{escape(level['title_' + suffix])}</h3>
        <p class="unit-topic">{escape(level['topic_' + suffix])}</p>
        <p>{escape(level['summary_' + suffix])}</p>
        {actions(unit['archive_id'], language, label)}
        <p class="unit-references">{reference_note}</p></li>''')
    reference_html = ''.join(f'<li id="ref-{number}"><a href="{escape(item["url"])}" target="_blank" rel="noopener">{escape(item["citation"])}</a></li>'
                             for number, item in enumerate(references, 1))
    disclosure = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in DISCLOSURE[language])
    reading = ('''<p>Start with Levels 1–2 to connect quantum states and measurement to noise. Levels 3–5 develop encoding, safe logical operations and the circuit costs of color codes. Levels 6–7 translate these ideas into adaptive measurements and photonic fusion.</p>
      <p>Prerequisites: high-school complex numbers and matrix multiplication. The compilation includes a notation guide on page 2. Four self-check questions appear in Levels 1–3: two, one and one respectively. Follow the derivations in the PDFs with your own calculations.</p>''' if en else '''<p>Level 1·2에서 상태와 측정을 익히고 잡음이 양자정보에 미치는 영향을 살펴봅니다. Level 3–5에서는 부호화와 안전한 논리연산을 거쳐 컬러 코드의 회로 비용으로 나아갑니다. Level 6·7은 이를 적응형 측정과 광자 융합으로 연결합니다.</p>
      <p>복소수와 행렬 곱셈을 알면 시작할 수 있습니다. 통합본 2쪽에는 표기 안내가 있고, Level 1·2·3에는 자기점검 문제가 각각 2개·1개·1개 수록되어 있습니다. PDF의 유도 과정을 직접 계산하며 확인해 보세요.</p>''')
    pages = f"{registry['compilation_public_pages']} pages" if en else f"{registry['compilation_public_pages']}쪽"
    return f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | Agentic Tech Review Letters</title><meta name="description" content="{escape(summary)}">
{english_meta}<link rel="stylesheet" href="{'../' if en else ''}notes.css"></head>
<body class="course-page">{navigation}<header class="course-topbar"><a class="brand" href="{root_prefix}{'en/' if en else ''}">Agentic Tech Review Letters</a><a href="{language_href}" lang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></header>
<main><header class="course-heading"><p class="kicker">{escape(course['topic_' + suffix])}</p><h1>{escape(title)}</h1>
<p class="course-summary">{escape(summary)}</p><p class="byline">{'Responsible editor: Hyun-Jung Kim · AI assistance: OpenAI Codex' if en else '책임 편집자 김현중 · AI 보조 OpenAI Codex'} · {DATE}</p>
<p class="course-facts">{'7 levels · 28 sections · Korean PDFs' if en else '7단계 · 28절 · 한국어 PDF'}</p></header>
<section id="compilation" class="compilation"><h2>{'Combined edition' if en else '통합본'}</h2><p class="pdf-meta">PDF {pages}</p>
<p>{escape(course['format_note_' + suffix])}</p>{actions(OWNER_ID, language, 'Combined edition' if en else '통합본')}</section>
<section id="study-guide"><h2>{'Reading guide' if en else '학습 순서'}</h2>{reading}</section>
<section id="units"><h2>{'Seven levels' if en else '단계별 강의'}</h2><ol class="course-units">{''.join(units)}</ol></section>
<section id="references"><h2>{'Primary references' if en else '참고문헌'}</h2>
<p>{'Full references and citations accompany each PDF. The sources below follow the progression of the seven levels.' if en else '전체 참고문헌과 인용은 각 PDF에 수록했습니다. 아래 원전은 단계별 학습 순서에 맞춰 연결했습니다.'}</p><ol class="references">{reference_html}</ol></section>
<section id="publication"><h2>{'Preparation and review' if en else '작성과 검수'}</h2>{disclosure}</section>
</main><footer><a href="{root_prefix}lectures/{'en/' if en else ''}">{'← Lecture notes' if en else '← 렉처 노트 목록'}</a></footer></body></html>'''


CSS = '''* { box-sizing:border-box; }
:root { color-scheme:light dark; --paper:#f7f7f3; --card:#fff; --ink:#182328; --muted:#5a686a; --line:#d8dfdc; --green:#087f70; }
body { margin:0; color:var(--ink); background:var(--paper); font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans KR",sans-serif; line-height:1.8; }
a { color:var(--green); text-underline-offset:3px; }
a:focus-visible { outline:3px solid var(--green); outline-offset:4px; border-radius:3px; }
.course-page>nav,.course-topbar,main,footer { width:min(860px,calc(100% - 40px)); margin-inline:auto; }
.course-page>nav { display:flex; gap:4px 20px; flex-wrap:wrap; padding-top:14px; font-size:13px; }
.course-page>nav a,.course-topbar a,footer a { display:inline-flex; align-items:center; min-height:44px; }
.course-topbar { display:flex; justify-content:space-between; align-items:center; gap:18px; padding:14px 0; border-bottom:1px solid var(--line); }
.brand { font-family:Georgia,serif; font-size:17px; color:var(--ink); text-decoration:none; }
main { padding-block:38px 24px; }
.course-heading { padding-bottom:25px; }
.kicker { color:var(--green); font-size:13px; font-weight:700; letter-spacing:.04em; }
h1 { font-size:clamp(29px,5vw,44px); line-height:1.35; letter-spacing:-.035em; margin:12px 0 20px; }
h2 { font-size:23px; line-height:1.45; letter-spacing:-.02em; margin:0 0 15px; }
h3 { font-size:21px; line-height:1.5; letter-spacing:-.02em; margin:0 0 8px; }
p { margin:0 0 14px; }
.course-summary { font-size:18px; }
.byline,.course-facts,.pdf-meta,.unit-number,.unit-topic,.unit-references { color:var(--muted); font-size:13px; }
.course-facts { font-weight:650; }
section { padding:30px 0; border-top:1px solid var(--line); }
.compilation { border:1px solid var(--line); border-top:3px solid var(--green); border-radius:10px; background:var(--card); padding:24px 28px; margin:0 0 30px; }
.compilation h2 { margin-bottom:4px; }
.lecture-actions { display:flex; flex-wrap:wrap; align-items:center; gap:0 22px; }
.lecture-actions a { display:inline-flex; align-items:center; justify-content:flex-start; min-height:44px; min-width:44px; padding:2px 0; font-size:13px; font-weight:650; text-decoration:none; }
.lecture-actions a:hover { text-decoration:underline; }
.lecture-primary { color:var(--green); }
.course-units { list-style:none; padding:0; margin:0; }
.course-units>li { padding:24px 0; border-top:1px solid var(--line); scroll-margin-top:20px; }
.unit-number { display:flex; align-items:center; gap:18px; color:var(--green); font-weight:750; margin-bottom:6px; }
.unit-number span { color:var(--muted); font-weight:450; }
.unit-topic { margin-bottom:12px; }
.unit-references { margin:4px 0 0; }
.unit-references a { display:inline-flex; align-items:center; min-height:44px; min-width:30px; }
.references { padding-left:24px; font-size:14px; overflow-wrap:anywhere; }
.references li { padding:5px 0; scroll-margin-top:20px; }
footer { border-top:1px solid var(--line); padding:20px 0 36px; font-size:14px; }
@media(max-width:600px) { .course-page>nav,.course-topbar,main,footer { width:calc(100% - 36px); } main { padding-top:25px; } .course-topbar { align-items:flex-start; } .brand { max-width:230px; font-size:15px; } .course-summary { font-size:16px; } .compilation { padding:20px; } h2 { font-size:21px; } h3 { font-size:19px; } .lecture-actions { gap:0 18px; } }
@media(prefers-color-scheme:dark) { :root { --paper:#101a20; --card:#14242b; --ink:#edf3ef; --muted:#b4c2c0; --line:#34454b; --green:#75d6bd; } }
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa", type=Path, default=ROOT / "reports/pdf-qa.json")
    parser.add_argument("--pdf-dir", type=Path, default=ROOT.parent / "archive/files")
    arguments = parser.parse_args()
    editions = load_public_editions(arguments.qa, arguments.pdf_dir)
    registry = course_registry(editions)
    # Complete both languages and all validation before writing an output file.
    pages = {language: render_page(registry, language) for language in ("ko", "en")}
    destination = ROOT / "dist"
    (destination / "en").mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(pages["ko"], encoding="utf-8")
    (destination / "en/index.html").write_text(pages["en"], encoding="utf-8")
    (destination / "notes.css").write_text(CSS, encoding="utf-8")
    (destination / "unit-registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Course guide and registry prepared from eight verified public PDF editions.")


if __name__ == "__main__":
    main()
