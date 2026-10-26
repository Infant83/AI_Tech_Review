from __future__ import annotations

import argparse
import html
import hashlib
import ipaddress
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit

try:
    from .hub_layout import render_hub, render_card as render_hub_card, render_latest as render_hub_latest, HUB_URL as HUB_PUBLIC_URL
    from .document_archive_site import LIBRARY_ASSET_VERSION, publish_archive, render_learning_teaser, render_library_navigation, validate_archive
    from .site_brand import ICON_ASSET_VERSION, SITE_STYLES_VERSION, render_brand_link
    from .reader_engagement_publish import enrich_site as enrich_reader_engagement, validate_public_artifact as validate_reader_artifact
except ImportError:
    from hub_layout import render_hub, render_card as render_hub_card, render_latest as render_hub_latest, HUB_URL as HUB_PUBLIC_URL
    from document_archive_site import LIBRARY_ASSET_VERSION, publish_archive, render_learning_teaser, render_library_navigation, validate_archive
    from site_brand import ICON_ASSET_VERSION, SITE_STYLES_VERSION, render_brand_link
    from reader_engagement_publish import enrich_site as enrich_reader_engagement, validate_public_artifact as validate_reader_artifact


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
REVIEWS_DIR = SITE_DIR / "reviews"
ASSETS_DIR = SITE_DIR / "assets"
HUB_ASSET_SOURCE_DIR = Path(__file__).resolve().parent / "public_assets"
HUB_PREFERENCES_JS = (HUB_ASSET_SOURCE_DIR / "preferences.js").read_text(encoding="utf-8")
ICON_SOURCE_DIR = ROOT / ".automation" / "assets" / "ai-tech-review-icon" / "generated"
EDITORIAL_HARNESS_NAME = "AI Tech Review Editorial Harness"
EDITORIAL_HARNESS_VERSION = "2026.08"
EDITORIAL_METHODS_HREF = "methods/"


@dataclass(frozen=True)
class PublicTranslation:
    language: str
    subdir: str
    label: str


@dataclass(frozen=True)
class PublicAgent:
    name: str
    role: str
    role_ko: str


@dataclass(frozen=True)
class PublicReview:
    folder: str
    title: str
    subtitle: str
    date: str
    updated: str
    category: str
    tags: tuple[str, ...]
    summary: str
    translations: tuple[PublicTranslation, ...] = ()
    responsible_editor: str = "김현중"
    responsible_editor_en: str = "Hyun-Jung Kim"
    ai_system: str = "AI-assisted workflow; exact system record not retained"
    ai_system_ko: str = "AI 보조 워크플로; 정확한 시스템 기록은 보존되지 않음"
    ai_model: str = "exact model identifier not retained"
    ai_model_ko: str = "정확한 모델 식별자는 보존되지 않음"
    agents: tuple[PublicAgent, ...] = ()
    agent_roles: tuple[str, ...] = ()
    agent_roles_ko: tuple[str, ...] = ()
    verification_scope: tuple[str, ...] = ()
    verification_scope_ko: tuple[str, ...] = ()
    primary_sources_checked: bool = False
    evidence_cutoff: str = ""
    human_review_level: str = "review level not separately retained"
    human_review_level_ko: str = "세부 검토 수준은 별도 기록되지 않음"
    disclosure_note_ko: str = ""
    disclosure_note_en: str = ""

    @property
    def dist_index(self) -> Path:
        return ROOT / self.folder / "dist" / "index.html"

    @property
    def public_dir(self) -> Path:
        return REVIEWS_DIR / self.folder

    @property
    def href(self) -> str:
        return f"reviews/{self.folder}/index.html"

    def translation_dist_index(self, translation: PublicTranslation) -> Path:
        return ROOT / self.folder / "dist" / translation.subdir / "index.html"

    def translation_public_dir(self, translation: PublicTranslation) -> Path:
        return self.public_dir / translation.subdir

    def translation_href(self, translation: PublicTranslation) -> str:
        return f"reviews/{self.folder}/{translation.subdir}/index.html"


REVIEWS: tuple[PublicReview, ...] = (
    PublicReview(
        folder="2026-10-25_quantum-software-platforms-ai-agents",
        title="양자 소프트웨어의 두 경쟁 경로: 회로 합성, AI 에이전트와 생태계의 주도권",
        subtitle="Classiq·Qiskit·CUDA-Q가 자동화하는 일과 남는 책임, 자원 교환과 하드웨어 연동에서 읽는 조건부 전망",
        date="2026-10-25", updated="2026-10-25", category="Quantum Computing",
        tags=("Quantum Software", "Circuit Synthesis", "Classiq", "Qiskit", "CUDA-Q", "AI Agents", "Interoperability"),
        summary="101을 찾으려다 111을 표시한 이상적 양자 계산에서 출발해, 고수준 모델의 합성과 에이전트의 도구 조합이 맡는 일을 설명합니다. 논문의 큐비트·CX 교환과 현행 Qiskit HLS, 하드웨어 연동과 공개성의 차이를 대조하고, 검증된 결과의 총비용에서 생태계 주도권을 읽는 세 가지 조건부 전망을 제시합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, ecosystem analysis, Korean writing, original conceptual cover, independent exact NumPy teaching calculation and publication integration", "1차 자료 종합·생태계 분석·한국어 집필·원본 개념 표지·독립 NumPy 교육 계산 및 게시 통합"),
            PublicAgent("academic_sources", "Qiskit released-code and documentation research, semantic/resource boundaries and independent scientific and bilingual audit", "Qiskit 릴리스 코드·문서 조사·의미와 자원 조건 대조 및 독립 과학·한영 감수"),
            PublicAgent("academic_sources/theory_crosscheck", "independent LLM quantum-code benchmark denominator, configuration and reproducibility checks", "LLM 양자 코드 벤치마크 분모·설정과 재현 범위의 독립 교차 검토"),
            PublicAgent("applications_sources", "Classiq papers, SDK and guarantee-scope audit, reported-data extraction and complete English translation", "Classiq 논문·SDK·보장 범위 감수·보고 데이터 추출 및 영어 전문 번역"),
            PublicAgent("applications_sources/translation_audit", "independent bilingual semantic, numerical, equation and reference correspondence audit", "한영 의미·수치·수식과 참고문헌 대응의 독립 감수"),
            PublicAgent("review_format", "original bilingual responsive figures, math/font typesetting, HTML/PDF production and complete output checks", "원본 한영 반응형 도표·수식과 글꼴 조판·HTML/PDF 제작 및 전체 출력 검수"),
            PublicAgent("publish_audit", "independent cover-semantics and reader-explanation review, metadata, archive and publication audit", "표지 의미·독자 설명의 독립 검토 및 메타데이터·아카이브·출판 감사"),
        ),
        verification_scope=(
            "Qmod language paper and separate synthesis preprint v2; Classiq SDK 1.33.1 static inspection and pinned public examples; Qiskit 2.6.1 released HLS/MCX/Target source, agent interfaces and service lifecycle checked against official documentation",
            "QuantumKatas benchmark denominators, configuration selection and reproduction limits; official Classiq/CUDA-Q, Qiskit/TKET/Quantinuum, Braket and Azure/QIR interoperability documentation; no account, hosted synthesis, LLM benchmark rerun, QPU or cross-platform performance experiment",
            "Independent exact ideal three-qubit NumPy state-vector calculation checks unitarity, normalization and 25/32 versus 1/32 after a single Grover iteration; not a device, compiler or LLM benchmark",
            "Reported Classiq 0.60.0 Figure 3 width/CX data distinguished from current implementations; bilingual manuscripts, conceptual cover, original diagrams, full PDFs, desktop/mobile, metadata, archive hashes and live publication checked",
        ),
        verification_scope_ko=(
            "Qmod 언어 논문과 별개 합성 프리프린트 v2·Classiq SDK1.33.1 정적 검토와 고정 공개 예제·Qiskit2.6.1 릴리스의 HLS/MCX/Target 코드 및 에이전트 인터페이스·서비스 이력을 공식 문서와 대조",
            "QuantumKatas 분모·설정 선택과 재현 한계·Classiq/CUDA-Q와 Qiskit/TKET/Quantinuum 및 Braket·Azure/QIR의 공식 연결 문서 확인; 계정·서비스 합성·LLM 벤치 반복·QPU·플랫폼 간 성능 실험 없음",
            "독립 NumPy 이상적 3큐비트 상태벡터 계산에서 유니터리성·정규화·한 Grover 반복 뒤25/32와1/32 확인; 장치·컴파일러·LLM 벤치마크가 아님",
            "Classiq0.60.0 Fig3의 저자 보고 폭·CX 값을 현재 구현과 구별; 한영 원고·개념 표지·원본 도표·전체 PDF·PC/모바일·메타데이터·아카이브 해시와 공개 게시 확인",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-25",
        human_review_level="topic and deeper technical review requested in the established publication workflow; no line-by-line human approval or comprehension study",
        human_review_level_ko="기존 게시 흐름에서 주제와 기술적 심층 리뷰 요청 반영; 문장 단위 사람 승인·독자 이해도 실험 없음",
        disclosure_note_ko="101/111 예제는 리뷰의 정확 교육 계산입니다. 합성 도표는 프리프린트의 Classiq0.60.0 컴파일 보고이며 현재 플랫폼 순위나 QPU 성능이 아닙니다. 폭 상한45/90과 실제 폭44/47을 구별합니다. 34.4%는 QuantumKatas의 한 범주55/160이며 범용LLM 정확도가 아닙니다. 공개 예제·SDK 라이선스·하드웨어 소유·이식성을 구분하고, 세 전망은 검증된 미래 성과가 아닌 조건부 해석으로 제시했습니다.",
        disclosure_note_en="The 101/111 example is an exact teaching calculation created for this review. The synthesis figure redraws the preprint's Classiq 0.60.0 compilation results, not current platform rankings or QPU performance. Width caps 45/90 differ from actual widths 44/47. QuantumKatas' 34.4% is one category's 55/160, not general LLM accuracy. Public examples, SDK licensing, hardware ownership and portability are distinguished; three scenarios are conditional interpretations, not validated future outcomes.",
    ),
    PublicReview(
        folder="2026-10-23_php-ai-vulnerability-disclosure",
        title="AI 시대의 보안 전환: PHP 사태에서 새 기반의 설계까지",
        subtitle="긴급 패치에서 레거시 전환·에이전트 권한·새 보안 기준과 기업 서비스까지",
        date="2026-10-23", updated="2026-10-23", category="AI Security",
        tags=("AI Security", "Security Architecture", "Legacy Modernization", "Agent Authorization", "PHP2Shell", "Secure by Design"),
        summary="PHP의 메모리 오류와 AI 보조 발견에서 출발해, 같은 기반을 계속 수리하는 능력과 더 안전하고 교체 가능한 기반으로 전환하는 능력을 함께 묻습니다. 제로 트러스트·메모리 안전 로드맵·에이전트 신원과 위임·Secure by Design 및 구매 지침을 대조하고, 이전·검증·이탈 능력을 제공하는 B2B 서비스의 방향을 제안합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        ai_model="exact model identifier not retained", ai_model_ko="정확한 모델 식별자는 보존되지 않음",
        agents=(
            PublicAgent("root", "primary-source synthesis, accessible Korean writing, English manuscript audit, conceptual cover planning and editorial integration", "1차 자료 종합·교양과학 한국어 집필·영어 원고 검토·개념 표지 기획 및 편집 통합"),
            PublicAgent("php_mechanism", "official PHP advisory, mechanism, affected-condition and timeline checks; independent scientific manuscript and figure audit; publication registration", "공식 PHP 권고·원인·영향 조건과 연혁 대조·독립 원고 및 도식 과학 감수·게시 등록"),
            PublicAgent("ai_claims", "AI contribution, reporting claims, sensor observations and implications crosschecks; independent exposition audit and full English translation", "AI 기여·보도 주장·센서 관측 및 후속 논의 대조·독립 설명 검토·영어 전문 번역"),
            PublicAgent("production_setup", "initial-edition original bilingual figures, font and HTML/PDF production and output checks", "초판 원본 한영 설명 도식·글꼴·HTML/PDF 제작 및 출력 검사"),
            PublicAgent("architecture_standards", "primary architecture and security-guidance research; independent scientific and argument audit of the expanded manuscript", "보안 아키텍처·공식 지침 조사 및 확장 원고의 독립 과학·논증 감수"),
            PublicAgent("migration_argument", "legacy modernization, lock-in and B2B research; expanded English manuscript translation and correspondence checks", "레거시 전환·공급자 종속·B2B 역할 조사 및 확장 영어판 번역·대응 검토"),
            PublicAgent("agent_standards", "agent identity, delegation and OAuth standards research; revised font, HTML/PDF production and full output checks", "에이전트 신원·위임·OAuth 표준 조사 및 개편 글꼴·HTML/PDF 제작·전체 출력 검사"),
        ),
        verification_scope=(
            "Official PHP advisories, release notices and manual; memory/request lifetimes, OOM handling, worker privileges, conditional FPM paths and the separate October 23 session advisory",
            "Discovery and maintainer accounts, AWS sensor observations, revised exploitability assessments and reporting frames; research demonstrations, attack attempts and confirmed real-world compromise distinguished",
            "Numerical denominators, CVSS severity, AI-assisted case reports versus controlled model evaluation, bilingual manuscripts, deterministic teaching figures and conceptual cover; no independent attack or exploit reproduction, model benchmark or global loss estimate",
            "Open-design principles, NIST zero-trust guidance, memory-safe roadmaps, government legacy and lock-in guidance, OAuth specifications, ongoing agent-identity work and secure-by-design/demand guidance; architecture and B2B proposals distinguished from measured outcomes",
            "Revised bilingual HTML/PDF assets, metadata, local links, desktop/mobile output and archive consistency; retained conceptual cover and original diagrams; no video produced",
        ),
        verification_scope_ko=(
            "공식 PHP 권고·릴리스 공지·매뉴얼 대조; 메모리와 요청의 수명·OOM 처리·워커 권한·조건부 FPM 경로 및 10월23일 별도 세션 공지 확인",
            "발견·유지보수 측 기록·AWS 센서 관측·공격 성립 범위의 수정 평가와 보도 관점 대조; 연구진의 실증·공격 시도·확인된 실제 침해 구별",
            "수치 분모·CVSS 심각도·AI 보조 사례와 통제된 모델 평가의 차이·한영 원고·결정론적 설명 도식과 개념 표지 검토; 독립 공격·exploit 재현·모델 성능 대조·세계 피해액 추정 없음",
            "공개 설계 원칙·NIST 제로 트러스트·메모리 안전 로드맵·정부 레거시와 종속 관리·OAuth·진행 중인 에이전트 신원 논의·Secure by Design/Demand 대조; 아키텍처와 B2B 제안은 측정 결과와 구별",
            "개편 한영 HTML/PDF 자산·메타데이터·로컬 링크·PC와 모바일 출력 및 아카이브 정합성 확인; 기존 개념 표지·설명 도식 유지, 영상 제작 없음",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-23",
        human_review_level="editorial direction on accessible science writing, architecture transition and enterprise services incorporated; no line-by-line human review or reader comprehension study",
        human_review_level_ko="주제 발전·교양과학 문체·기반 전환과 기업 서비스 관점에 대한 편집 방향 반영; 문장 단위 사람 감수·독자 이해도 평가 없음",
        disclosure_note_ko="기사에서 언급하는 보안 연구용 AI 모델과 이 글의 작성 시스템을 구별하며, 작성 세션의 정확한 모델 식별자는 미보존입니다. PHP 사용 비중은 취약·침해 비율이 아니고, CVSS 점수는 공격 성공 확률이 아닙니다. AWS의 10월17일 관측은 공격 시도이며 8월의 AI 보조 발견보다 늦습니다. 10월23일 공지는 별도 CVE의 드문 세션 설정 경로에 관한 것입니다. 공격자 AI 사용·전 세계 침해 규모·모델의 독자적 기여율은 확인하지 않았으며, 제로 트러스트·현대화 지침·OAuth의 기존 구성요소와 진행 중인 에이전트 표준화를 구별했습니다. 전환·검증·이탈 능력의 B2B 제안은 특정 업체의 현황·시장 예측이나 안전성 보증이 아닙니다.",
        disclosure_note_en="The security-research AI models discussed in the article are distinct from its writing system; the exact model identifier for the writing session was not retained. PHP usage share is neither vulnerability prevalence nor compromise rate, and CVSS severity is not attack success probability. AWS's October 17 observation concerns an attempt and follows the AI-assisted August findings. The October 23 notice concerns a rare session configuration path under a separate CVE. Attacker AI use, global compromise totals and model-only contributions were not established; established guidance and OAuth components are distinguished from ongoing agent standardization. Proposed B2B value in migration, verification and exit capability is not a claim about any company, a market forecast or a security guarantee.",
    ),
    PublicReview(
        folder="2026-10-23_quantum-latent-generative-models",
        title="광양자 샘플링과 생성형 AI: 출발 분포는 분자 설계를 바꾸는가",
        subtitle="광자 간섭의 확률 규칙, 분자 생성의 성과와 고전 기준선, 단백질 설계로 넘어가기 위한 조건",
        date="2026-10-23", updated="2026-10-23", category="Quantum Computing",
        tags=("Photonic Quantum Computing", "Generative Models", "Latent Distributions", "Boson Sampling", "Molecular Design", "Proteína"),
        summary="분자를 제안하는 생성형 AI가 무작위 숫자에서 출발한다는 질문으로 시작합니다. 두 광자의 간섭부터 잠재분포와 표현력의 조건, QM9의 품질 개선과 고전 학습 조정 뒤의 음성 결과를 설명합니다. 제한적인 CPU 예제 실행을 덧붙이고, PT-3 단백질 발표의 designability와 전체 계산비용에 남은 검증 과제를 살펴봅니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, accessible Korean writing, original conceptual cover, scientific editing and publication integration", "1차 자료 종합·교양과학 한국어 집필·원본 개념 표지·과학 편집 및 게시 통합"),
            PublicAgent("academic_sources", "primary-paper, theory, metric, version and claim-scope checks; independent scientific manuscript audit", "원 논문·이론·지표·버전과 주장 범위 대조 및 독립 과학 감수"),
            PublicAgent("academic_sources/theory_crosscheck", "independent mathematical assumptions and theorem-scope crosscheck", "수학적 가정과 정리 적용 범위의 독립 교차 검토"),
            PublicAgent("applications_sources", "limited single-seed CPU training, exact small-case sampler checks and original bilingual explanatory figures", "한 시드의 제한 CPU 학습·작은 정확 사례의 표본기 검사·원본 한영 설명 도표"),
            PublicAgent("review_format", "bilingual math and font typesetting, HTML/PDF production and complete output checks", "한영 수식·글꼴 조판·HTML/PDF 제작과 전체 출력 검사"),
            PublicAgent("publish_audit", "independent explanation and conceptual-cover audit, complete English translation and publication audit", "설명·개념 표지의 의미 독립 감사·영어 전문 번역 및 출판 감사"),
        ),
        verification_scope=(
            "ICML 2026 camera-ready paper, arXiv v3 and official code pinned at b950127d3584561fee4aea4af566bcce697d6946; theoretical inverse/regularity assumptions, Table 4 denominators and standard errors, Appendix H negative results and postselection/cost conditions",
            "Original Proteína model and designability protocol, separate PT-2 peptide study and PT-3 announcement distinguished; no corresponding detailed quantum-Proteína paper or reproducible evaluation confirmed at the evidence cutoff",
            "Limited classical CPU training of a single-loop synthetic-point example with one training seed; exact two-photon and optical-unitary checks; no independent reproduction of the paper's three-loop Figure 1, QM9, QPU or protein experiments",
            "Bilingual manuscripts, original conceptual cover and deterministic figures, all PDF pages, metadata, local assets, mobile output and archive checksums",
        ),
        verification_scope_ko=(
            "ICML 2026 게재본·arXiv v3·b950127d3584561fee4aea4af566bcce697d6946 고정 공식 코드 대조; 역함수와 정규성의 이론 조건·표 4 분모와 표준오차·부록 H 음성 결과·후선택과 비용 조건 확인",
            "원 Proteína 모델의 designability 절차·별도 PT-2 펩타이드 연구·PT-3 발표 구별; 근거 기준일까지 해당 양자 Proteína 확장판의 상세 논문이나 재현 가능한 평가 자료를 확인하지 못함",
            "한 훈련 시드·단일 루프의 합성 점 예제를 고전 CPU에서 제한 학습하고 두 광자 확률·광학 유니터리를 검사; 논문 Figure 1의 3루프·QM9·QPU·단백질 실험 독립 재현 없음",
            "한영 원고·원본 개념 표지와 결정론적 도표·전체 PDF 페이지·메타데이터·자산·모바일 출력과 아카이브 체크섬 확인",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-23",
        human_review_level="topic, writing, public posting and accessible scientific editorial direction requested; no line-by-line human approval or reader comprehension study",
        human_review_level_ko="주제·집필·공개 게시와 교양과학 편집 방향 요청 반영; 문장 단위 사람 승인·독자 이해도 실험 없음",
        disclosure_note_ko="표 4의 1,962개는 10,000회 시도 중 유효하고 서로 다른 분자의 평균 수이고, 오차는 20개 훈련 시드의 표준오차입니다. 가우시안 대비 약 48.6%의 상대 증가와 6.42%포인트 차이를 구별합니다. 광학 표본은 한 고정 회로에서 수집했습니다. CPU 점 예제는 리뷰의 제한 실행이며 논문 실험의 재현이나 양자우위 검정이 아닙니다. PT-3의 20%는 공급자 발표이고, 별도 펩타이드의 실험실 결과와 합치지 않습니다. 개념 표지와 정량 도표를 구분했습니다.",
        disclosure_note_en="Table 4's 1,962 is the mean count of valid, unique molecules per 10,000 attempts; errors are standard errors over 20 training seeds. A roughly 48.6% relative increase over Gaussian is distinct from a 6.42 percentage-point difference. Optical samples came from one fixed circuit. The CPU point example is a limited review run, not a reproduction of the paper's experiments or a quantum-advantage test. PT-3's 20% is a supplier announcement and is not combined with separate peptide laboratory results. The conceptual cover and quantitative figures are distinguished.",
    ),
    PublicReview(
        folder="2026-10-23_neural-representations-interpretability",
        title="신경망을 이해한다는 것: 의미를 읽고 원인을 시험하는 과학",
        subtitle="뉴런·특징·회로의 해석에서 모델 수정과 지속 감사, 신뢰의 조건까지",
        date="2026-10-23", updated="2026-10-23", category="AI Research",
        tags=("Mechanistic Interpretability", "Neural Representations", "Circuit Tracing", "Sparse Autoencoders", "Persona Vectors", "AI Auditing"),
        summary="댈러스의 주도를 답하는 모델의 중간 계산에 개입한 사례에서 출발해 뉴런·특징·회로를 쉽게 설명합니다. 원래 뉴런의 정량 연구와 Goodfire 논쟁, 특징 조절·페르소나 벡터·AuditBench를 연결하며, 모델을 고치고 업데이트 뒤 다시 검사하는 연구가 신뢰와 독립 검증에 던지는 질문을 살펴봅니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, accessible bilingual writing, implications, retained conceptual cover and publication integration", "1차 자료 종합·교양과학 한영 집필·후속 논의 편집·기존 개념 표지와 게시 통합"),
            PublicAgent("deep_mechanisms", "original papers, pinned official code, circuit/intervention/metric checking and independent scientific manuscript audit", "원 논문·고정 공식 코드·회로와 개입·평가 지표 대조 및 독립 과학 감수"),
            PublicAgent("deep_implications", "steering, persona vectors, reasoning faithfulness and auditing research; independent exposition and implications audit", "특징 조절·페르소나·추론 충실도·감사 조사와 독립 설명·후속 논의 감수"),
            PublicAgent("deep_production", "new bilingual teaching diagrams, font and HTML/PDF production and full output checks", "새 한영 교육 도식·글꼴·HTML/PDF 제작과 전체 출력 검수"),
            PublicAgent("research_evidence", "initial-edition source, response, numerical-denominator and bilingual manuscript checking", "초기 리뷰의 원문·반론·수치 분모와 한영 원고 검토"),
            PublicAgent("mechanism_figures", "initial-edition conceptual distinctions and retained bilingual representation diagram", "초기 개념 구분과 이번에 유지한 한영 표현 도식 제작"),
            PublicAgent("pipeline_audit", "initial-edition build investigation and HTML/PDF production checks", "초기 빌드 방식 조사와 HTML/PDF 제작 검수"),
        ),
        verification_scope=(
            "Original circuit-tracing papers; Arora et al. v2 and pinned official code; Goodfire essay and Gao response; feature steering, Persona Vectors v3 and AuditBench v4",
            "Models, feature groups versus native neurons, token-position nodes, intervention targets, held-out evaluation, numerical denominators and reported-result/interpretation/proposal boundaries; no model-training or intervention reproduction",
            "Bilingual manuscripts, three types of original teaching diagrams, retained conceptual cover, all PDF pages, local assets, metadata, mobile output and archive checksums",
        ),
        verification_scope_ko=(
            "회로 추적 원 논문·Arora v2와 고정 공식 코드·Goodfire 에세이와 Gao 반론·특징 조절·Persona Vectors v3·AuditBench v4 대조",
            "모델·특징군과 원래 뉴런·토큰 위치별 노드·개입 대상·분리 평가·수치 분모와 결과/해석/제안 경계 확인; 모델 학습·개입 독립 재현 없음",
            "한영 원고·원본 교육 도식 3종·기존 개념 표지·전체 PDF 페이지·자산·메타데이터·모바일 출력과 아카이브 체크섬 확인",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-23",
        human_review_level="editorial direction to adopt the topic and develop accessible science writing and implications; no line-by-line human review or comprehension study",
        human_review_level_ko="주제 채택·교양과학 문체·후속 논의에 대한 편집 방향 반영; 문장 단위 사람 감수·이해도 평가 없음",
        disclosure_note_ko="CLT 특징군의 도시–주–주도 개입과 원래 MLP 뉴런 연구는 별도 모델·실험입니다. 약 200개는 제한된 문법 과제의 토큰 위치별 회로 노드이며, 90%는 예비적인 뉴런 pole 판정으로 모델 이해율이 아닙니다. 금문교 실험은 가중치 수정이 아닌 활성 조절입니다. AuditBench는 버그 수정 뒤 재실행한 v4를 기준으로 읽었습니다. 모델 수리·지속 감사·독립 검증에 대한 전망은 보고 결과와 구분했습니다.",
        disclosure_note_en="CLT feature-group city–state–capital interventions and native MLP-neuron results concern separate models and experiments. Roughly 200 refers to token-position circuit nodes on limited grammar tasks; 90% is a preliminary neuron-pole judgment, not model understanding. Golden Gate steering changes activations rather than weights. AuditBench uses v4 after corrected data and rerun experiments. Prospects for repair, continuous auditing and independent verification are distinguished from reported results.",
    ),
    PublicReview(
        folder="2026-10-21_sparse-reference-quantum-chemistry",
        title="양자화학의 에너지 차이를 읽는 법: 희소 기준상태와 혼합 추정량",
        subtitle="희소 기준상태가 에너지 측정을 줄이는 원리와 조건, Helios 실험의 정밀도와 정확도",
        date="2026-10-21", updated="2026-10-21", category="Quantum Computing",
        tags=("Quantum Chemistry", "Sparse Reference", "Mixed Estimator", "Measurement Cost", "Helios", "Energy Estimation"),
        summary="에너지 차이가 화학적 판단을 바꾸는 이유에서 출발해 희소 기준상태와 잔차, 혼합 추정량의 유도와 오차를 설명합니다. 독립적인 2준위 실습과 문제·풀이를 거쳐 이상적 약 400회 추정과 실제 QPU 10,000회 측정의 조건, 정밀도와 정확도, 전체 계산비용을 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, bilingual in-depth review writing and topic-led revision, scientific editing, publication integration and live verification", "1차 자료 종합·한영 심층 리뷰 집필·주제 중심 도입 편집·과학 편집·게시 통합 및 공개 페이지 검증"),
            PublicAgent("seminar_science", "original-paper and supplement research, numerical/formula/claim-scope checking and independent manuscript audit", "원 논문·부록 조사·수치와 수식·주장 범위 대조 및 독립 원고 감수"),
            PublicAgent("seminar_production", "original bilingual responsive figures, independently checked two-level calculation and interactive lab, equation/font typesetting and HTML/PDF production and validation", "한영 반응형 설명 그림·독립 2준위 계산과 인터랙티브 실습·수식과 글꼴 조판·HTML/PDF 제작 및 검증"),
            PublicAgent("seminar_cover", "scientific-cover planning, built-in image generation and visual review", "과학 표지 기획·내장 이미지 생성·시각 검수"),
            PublicAgent("seminar_translation", "full English translation of the Korean canonical review, preserving formulas, numerical values and scientific conditions", "한국어 정본 리뷰의 전체 영어 번역·수식과 수치·과학적 조건 보존"),
            PublicAgent("implicit_structure_review", "independent editorial audit of topic-led framing and reader-facing wording", "주제 중심 구성·독자용 표현의 독립 편집 감수"),
            PublicAgent("revision_production", "revised bilingual HTML/PDF regeneration and output checks", "개정 한영 HTML/PDF 재생성과 출력 검수"),
        ),
        verification_scope=(
            "Original arXiv:2610.26689v1 paper and supplement, equations and numerical tables; active spaces, variance estimates, QPU/emulator distinctions, postselection, error metrics and separate SVD-THC logical-resource estimates",
            "Independent synthetic two-level identity, delta-method gradients/variance and optimal shot allocation; no independent reproduction of molecular calculations or QPU experiments",
            "Bilingual manuscripts, original figures, formulas, interactive teaching controls, HTML/PDF metadata and desktop/mobile publication output",
        ),
        verification_scope_ko=(
            "arXiv:2610.26689v1 원 논문·부록의 식과 수치표·활성공간·분산 추정·실제 QPU와 emulator 구분·후선택·오차 지표 및 별도 SVD-THC 논리 자원 추정 대조",
            "독립 합성 2준위 항등식·델타 방법의 미분과 분산·최적 측정 배분 계산; 분자 계산·QPU 실험 독립 재현 없음",
            "한영 원고·원본 그림·수식·인터랙티브 교육 제어·HTML/PDF 메타데이터 및 PC·모바일 게시 출력 확인",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-21",
        human_review_level="editorial feedback on topic-led framing and wording incorporated; no line-by-line human review of the full manuscript",
        human_review_level_ko="주제 중심의 도입·표현에 대한 편집 피드백 반영; 전체 원고의 문장 단위 사람 검토 없음",
        disclosure_note_ko="약 400회는 (6,6) 활성공간의 이상적 측정 분산 추정이고, 10,000회는 (10,10) 활성공간의 실제 Helios-1 QPU 제출 측정 횟수입니다. 두 수를 같은 조건의 속도 향상 비율로 읽지 않습니다. 합성 2준위 실습은 논문 데이터가 아니며, 공통 확률 축척의 상쇄·유한 표본 분산·참조 중첩 조건을 구별합니다. 개념 표지와 정량 교육 도표의 역할을 분리했습니다.",
        disclosure_note_en="Approximately 400 shots is a noiseless measurement-variance estimate in the (6,6) active space; 10,000 is the submitted shot count on the physical Helios-1 QPU in the (10,10) active space. These are not a same-condition speedup ratio. The synthetic two-level lab is not paper data; common probability scaling, finite-sample variance and nonzero reference overlap are distinguished. The conceptual cover and quantitative teaching figures serve separate roles.",
    ),
    PublicReview(
        folder="2026-10-20_jupiter-fault-tolerant-simulation",
        title="104큐비트 프로토콜의 고전 모사: JUPITER로 시험한 매직상태 배양",
        subtitle="매직상태의 역할, 결맞는 오차와 누설, 45비트 부호화 레지스터와 512 TiB 메모리를 설명합니다",
        date="2026-10-20", updated="2026-10-20", category="Quantum Computing",
        tags=("JUPITER", "Magic State Cultivation", "Fault Tolerance", "GPU Simulation", "Quantum Error Correction", "Leakage"),
        summary="JUPITER의 8,192개 GH200으로 모사한 104개 물리 위치의 매직상태 배양 절차를 살펴봅니다. 저장공간 재사용·qutrit packing·상태벡터 메모리를 설명하고, 결맞는 오차와 누설, 수락률과 비용, 소형 교차검증과 전체 실행의 공개 범위를 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, Korean and English writing, scientific editing, publication integration and live verification", "1차 자료 종합·한국어와 영어 집필·과학 편집·게시 통합 및 공개 페이지 검증"),
            PublicAgent("jupiter_sources", "primary-paper and official-source research, numerical/model/claim-scope checking and independent manuscript audit", "원 논문·공식 자료 조사·수치와 모형·주장 범위 대조 및 독립 원고 감수"),
            PublicAgent("jupiter_production", "original bilingual responsive figures, teaching memory calculations, font/equation typesetting and HTML/PDF production and validation", "한영 반응형 설명 그림·교육용 메모리 계산·글꼴과 수식 조판·HTML/PDF 제작 및 검증"),
            PublicAgent("jupiter_cover", "built-in image generation, conceptual-cover export and visual inspection", "내장 이미지 생성·개념 표지 저장 및 시각 검토"),
            PublicAgent("mail_inventory", "recent DQB inventory, attachment comparison and original-PDF archive intake", "최근 DQB 목록·첨부 파일 대조·원본 PDF 아카이브 등록"),
            PublicAgent("jupiter_cover_rework", "new storage-reuse cover concept, built-in image generation and visual checks under scientific cover principles 1.0", "과학 표지 원칙 1.0에 따른 저장공간 재사용 표지 개편·내장 이미지 생성·시각 검사"),
            PublicAgent("cover_update_audit", "independent scientific-correspondence, thumbnail, grayscale and reusable-guidance audit of the revised cover", "개편 표지의 과학적 대응·썸네일·흑백·재사용 지침 독립 검토"),
        ),
        verification_scope=(
            "NVIDIA 2026-10-19 technical account and official release, JSC system documentation, original cultivation and flag papers, and the separate Willow experiment",
            "104 protocol locations versus a 45-bit encoded live register; qutrit mapping, complex128 storage and coherent/stochastic single-qubit teaching calculations; no independent JUPITER run or device experiment",
            "Korean and complete English manuscripts, original diagrams, full PDF page rendering, public metadata, assets, archive checksums and desktop/mobile publication checks",
        ),
        verification_scope_ko=(
            "NVIDIA 2026-10-19 기술 글과 공식 발표·JSC 시스템 자료·원 배양 및 flag 논문·별도 Willow 장치 실험 대조",
            "104개 프로토콜 위치와 45비트 동시 저장 레지스터 구별·qutrit 매핑·complex128 메모리·결맞는 오차와 확률적 오차의 단일 큐비트 교육용 계산; JUPITER 실행·장치 실험 재현 없음",
            "한국어 정본과 전체 영어판·원본 설명 그림·전체 PDF 페이지 렌더링·공개 메타데이터·자산·아카이브 체크섬·PC 및 모바일 게시 화면 검사",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-20",
        human_review_level="recent DQB archiving, separate review and application of cover principles requested; no line-by-line or individual new-cover human review",
        human_review_level_ko="최근 DQB 아카이브·별도 리뷰·표지 원칙 적용 요청 확인; 문장 단위 또는 새 표지의 개별 사람 심사 없음",
        disclosure_note_ko="고전 GPU 모사와 실제 QPU 실험을 구별했습니다. 45비트는 부호화된 동시 저장 레지스터로, 임의의 104큐비트 상태를 압축했다는 뜻이 아닙니다. 약 10^-13 확률 일치는 소형 회로의 교차검증이며 전체 실행의 논리 오류율이 아닙니다. 90% 개선 주장·원 배양의 qubit-rounds·별도 flag 연구·Willow 후선택 실험은 각 출처와 조건에 귀속했습니다. 과학 표지 원칙 1.0을 적용한 새 표지는 시간층의 점유·빈자리·재점유로 측정 후 저장공간 재사용을 상징한 내장 imagegen 개념 그림입니다. 칸과 점의 개수는 물리량을 나타내지 않습니다. 설명 도표와 수치 예시는 직접 제작했습니다.",
        disclosure_note_en="Distinguished classical GPU simulation from physical QPU experiments. The 45-bit quantity is an encoded live register, not compression of an arbitrary 104-qubit state. Approximately 10^-13 probability agreement concerns small-circuit cross-checks, not the full run's logical error rate. Attributed the 90% claim, original cultivation qubit-rounds, separate flag study and postselected Willow experiment to their own sources and conditions. The revised built-in imagegen cover applies scientific cover principles 1.0: occupied, empty and reoccupied bays across time symbolize storage reuse after measurement. Bay and dot counts encode no physical quantity. Diagrams and numerical examples are original teaching material.",
    ),
    PublicReview(
        folder="2026-10-20_quasi-riemann-ai-proof",
        title="준리만가설과 AI 수학: 소수 분포의 경계와 증명의 검증",
        subtitle="제타함수의 영점과 소수 개수의 오차를 잇는 원리부터 7/8·11/12 원고, 메타플렉틱 형식, Lean 검증과 알고리즘 응용의 범위까지",
        date="2026-10-20", updated="2026-10-20", category="AI for Science",
        tags=("AI Mathematics", "Number Theory", "Quasi-Riemann Hypothesis", "Prime Distribution", "L-functions", "Lean", "Formal Verification"),
        summary="제타함수의 영점이 소수 분포의 오차를 제한하는 원리를 설명하고, 7/8·11/12 원고의 성립 범위와 증명 도구를 분석합니다. 공개 Lean 진술·정의·검증 경로와 전문가의 이해를 구분하며, 명시적 소수정리 상계·알고리즘·암호 응용의 조건을 살펴봅니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source synthesis, Korean writing, conceptual cover, scientific editing, publication integration and live verification", "1차 자료 종합·한국어 집필·개념 표지·과학 편집·게시 통합 및 공개 페이지 검증"),
            PublicAgent("academic_sources", "mathematical source research, theorem and formula audit, proof-scope and Mathlib pole-semantics checking", "수학 원전 조사·정리와 수식 감수·증명 범위 및 Mathlib 극점 관례 확인"),
            PublicAgent("applications_sources", "AI-workflow and applications research, English translation, original figures and independent teaching calculations", "AI 연구 절차·응용 조사·영어 번역·설명 도표·독립 교육용 계산"),
            PublicAgent("review_format", "bilingual equation/font typesetting, responsive figures, full HTML/PDF production and publication-output checks", "한영 수식·글꼴 조판·반응형 도표·HTML/PDF 제작 및 게시 출력 검사"),
            PublicAgent("publish_audit", "publication metadata, link, asset and disclosure audit", "공개 메타데이터·링크·자산·작성 공개 정보 감사"),
        ),
        verification_scope=(
            "Quanta 2026-10-19 reporting; the 7/8 and 11/12 manuscripts, family 003 scope, declarations and configurations at openai/math commit 1581d4cbdd69a0faf34b2089614fe2a814316a6a",
            "Euler-product convergence, explicit-formula conditions, exponent extraction, Fiori-Jaskari application bounds, and Mathlib definitions at commit d13f23b723b8a846827a245b89c10fc7d3f11612; no independent full-proof verification or Lean rebuild",
            "Independent teaching power-factor and normalized-bound calculations; bilingual figures, formulas, PDF metadata, desktop/mobile layout and deployed page/PDF links",
        ),
        verification_scope_ko=(
            "Quanta 2026-10-19 보도·7/8 및 11/12 원고·openai/math 커밋 1581d4cbdd69a0faf34b2089614fe2a814316a6a의 family 003 범위·진술·검증 설정 대조",
            "오일러 곱 수렴 영역·명시적 공식 조건·지수 추출·Fiori–Jaskari 응용 상계·Mathlib 커밋 d13f23b723b8a846827a245b89c10fc7d3f11612의 정의 확인; 원증명 전체의 독립 검증·Lean 재빌드 없음",
            "교육용 거듭제곱 인자·정규화 상계의 독립 계산·한영 도표와 수식·PDF 메타데이터·데스크톱 및 모바일·공개 본문과 PDF 링크 검사",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-20",
        human_review_level="topic, writing and public posting explicitly requested; no line-by-line human approval",
        human_review_level_ko="주제·작성·공개 게시 요청 확인; 문장 단위 사람 승인 없음",
        disclosure_note_ko="7/8과 11/12는 서로 다른 원고의 경계이며, 리만가설의 1/2 경계는 해결하지 않습니다. 전문가의 원고 이해·공개 형식화·이 리뷰의 정적 코드 검토와 독립 재실행을 구분합니다. Lean challenge의 자리표시자는 별도 solution의 증명과 다르며, 함수의 극점 관례도 정의까지 대조했습니다. 도표와 수치 예시는 직접 제작한 설명 자료로 실제 영점 측정·완전한 소수 오차의 관측·원증명 재현이 아닙니다. 표지는 내장 imagegen 개념 그림입니다. 실용적 인수분해나 암호 해독 성능을 검증하지 않았습니다.",
        disclosure_note_en="The 7/8 and 11/12 boundaries belong to separate manuscripts and do not settle RH's 1/2 boundary. Distinguished expert understanding, published formalization, static code inspection in this review, and independent execution. A placeholder in a Lean challenge is distinct from its separate solution; pole conventions were checked against definitions. Original diagrams and numerical examples are teaching material, not observed zeros, measured complete prime-counting errors or reproductions of the proof. The built-in imagegen cover is conceptual. No practical factoring or cryptanalytic performance was validated.",
    ),
    PublicReview(
        folder="2026-10-19_quantum-qubit-platforms",
        title="양자 큐비트 플랫폼의 현재와 확장 과제",
        subtitle="마요라나의 보호 검증과 이온·중성원자·초전도의 실현 경로를 논문·제어 성능·투자 흐름으로 비교하다",
        date="2026-10-19", updated="2026-10-19", category="Quantum Computing",
        tags=("Qubit Platforms", "Majorana", "Trapped Ions", "Neutral Atoms", "Superconducting Qubits", "Spin Qubits", "Photonics", "Quantum Error Correction"),
        summary="각 큐비트의 상태 부호화·해밀토니안·제어·얽힘·판독을 설명하고, 마요라나의 패리티 수명·결맞음·보호 검증을 구별합니다. 이온·초전도·중성원자 등 주요 경로의 가까운 실현 가능성과 파급력을 비교하며, 운영 비용·제조 기반·투자 흐름을 함께 평가합니다.",
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "primary-source integration, Korean scientific writing, editing, figure integration and publication verification", "1차 자료 종합·한국어 과학 집필·편집·그림 통합·게시 검증"),
            PublicAgent("atomic_platforms", "trapped-ion and neutral-atom primary-paper research and factual audit", "이온·중성원자 원 논문 조사 및 사실관계 검토"),
            PublicAgent("solid_state", "superconducting, bosonic and semiconductor-spin primary-paper research and factual audit", "초전도·보소닉·반도체 스핀 원 논문 조사 및 사실관계 검토"),
            PublicAgent("photonic_topological", "photonic, defect-center, molecular and Majorana primary-paper research and factual audit", "광자·결함 중심·분자·Majorana 원 논문 조사 및 사실관계 검토"),
            PublicAgent("publication_audit", "publication pipeline inspection and scientific prose review", "게시 파이프라인 점검·과학 문체 검토"),
            PublicAgent("scientific_figures", "original physical-mechanism schematics, evidence diagram and source-checked quantitative figure", "물리 원리 개념도·근거 판독 도식·원문 수치 대조 그래프 제작"),
            PublicAgent("hero_illustration", "built-in image generation, cover export and visual inspection", "내장 이미지 생성·표지 저장 및 시각 검토"),
            PublicAgent("majorana_audit", "updated Majorana primary-source audit and original desktop/mobile evidence diagrams", "마요라나 최신 원문 대조·PC 및 모바일 성과와 검증 도식 제작"),
            PublicAgent("platform_outlook", "feasibility, control, operational costs and near-term milestones review", "실현 가능성·제어·운영 비용·가까운 이정표 검토"),
            PublicAgent("investment_signals", "official financing, public filings, manufacturing commitments and independent-test program audit", "공식 조달·공시·제조 지원·외부 시험 프로그램 사실관계 검토"),
            PublicAgent("physics_atomic", "ion, neutral-atom and molecular mechanism writing, primary-source and diagram audit", "이온·중성원자·분자 물리 원리 집필·원 논문 및 도식 검토"),
            PublicAgent("physics_solid", "circuit, bosonic and spin Hamiltonians, encoding conventions and numerical-model audit", "회로·보소닉·스핀 해밀토니안·부호화 관례·수치 모형 검토"),
            PublicAgent("physics_light_topology", "photonic, defect-center and Majorana physical principles and basis audit", "광자·결함 중심·마요라나 물리 원리·기저 검토"),
        ),
        verification_scope=(
            "Selected publisher and author-manuscript primary sources through 2026-10-19; online publication dates, physical/logical resources, error metrics and postselection conditions",
            "Experimental results, theoretical estimates and simulations distinguished; no independent device experiment or reproduction of published raw data",
            "Conceptual AI-generated cover and original schematics; toric-code chart redraws fitted long-run Z error rates reported in arXiv:2606.04079; public metadata, links, assets and desktop/mobile publication checks",
            "Majorana device and measurement distinctions, July coherent-control experiment and October theory/acceptance updates; official financing instruments and DARPA Stage C status distinguished from validated performance",
            "Original mechanism papers, effective Hamiltonian units and assumptions, readout and code-space conventions; new atomic/encoding diagrams and explicitly parameterized circuit-energy models, with grid and domain checks",
        ),
        verification_scope_ko=(
            "2026-10-19까지의 선정 출판사·저자 공개 1차 자료에서 온라인 공개일·물리 및 논리 자원·오류 지표·후선택 조건 대조",
            "실험 결과·이론적 자원 추정·시뮬레이션 구분; 독립 장치 실험이나 논문 원자료 재현 없음",
            "AI 생성 개념 표지와 직접 제작한 도식; toric-code 그래프는 arXiv:2606.04079에 보고된 긴 실행의 Z 논리 오류 적합값을 재도식화; 공개 metadata·링크·자산·PC 및 모바일 게시 화면 검사",
            "마요라나의 장치·측정량 구분과 7월 결맞는 제어 및 10월 이론·심사 상태 갱신 대조; 공식 조달·지원 수단과 DARPA Stage C 진입을 검증된 성능과 구분",
            "원형 논문에서 물리 원리·유효 해밀토니안의 단위와 근사·판독·부호 공간 대조; 원자·부호화 도식과 매개변수를 명시한 회로 에너지 모형 작성 및 격자·경계 검산",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-19",
        human_review_level="topic, scientific-writing direction and public posting explicitly requested; no separately recorded line-by-line human review",
        human_review_level_ko="주제·과학적 글쓰기 기조·공개 게시 요청 확인; 별도 문장 단위 사람 검토 기록 없음",
        disclosure_note_ko="배열의 자리 수·시간 모드 수·물리 큐비트 수·논리 큐비트 수를 구별했습니다. 오류검출과 후선택, 반복 오류정정, 한 오류축의 반복 부호, 임의 상태의 보호와 논리 게이트를 각각 평가했습니다. 사전공개 논문을 표시했고 Majorana의 패리티 수명과 결맞음 수명, 위상 보호의 검증 범위를 구분했습니다. 표지는 내장 이미지 생성 도구의 개념 일러스트이며 실제 장치 사진이나 성능 자료가 아닙니다. 도식은 직접 작성했으며 정량 그래프는 한 논문의 같은 지표를 재도식화했습니다. 서로 다른 플랫폼의 오류율 순위를 만들지 않았습니다.",
        disclosure_note_en="Distinguished array sites, temporal modes, physical qubits and logical qubits. Separated detection and postselection, repeated correction, single-axis repetition codes, arbitrary-state protection and logical gates. Marked preprints and distinguished Majorana parity lifetime from coherence lifetime and verified topological protection. The built-in image-generated cover is conceptual, not a device photograph or performance evidence. Schematics are original; the quantitative chart redraws one paper's matched metric without ranking unlike platform error rates.",
    ),
    PublicReview(
        folder="2026-10-19_generative-ai-quantum-circuit-design",
        title="생성형 AI를 통한 양자회로 설계와 최적화",
        subtitle="회로 생성 연구와 기업별 기술 자산을 비교하고 범용 에이전트 시대의 플랫폼 경쟁력을 전망합니다",
        date="2026-10-19", updated="2026-10-19", category="Quantum Computing",
        tags=("Generative AI", "Quantum Circuit Synthesis", "Classiq", "Reinforcement Learning", "Quantum Chemistry", "FTQC", "Agentic AI"),
        summary="확산모델·Transformer·강화학습·LLM 에이전트의 양자회로 생성과 최적화를 검토합니다. Classiq와 IBM·NVIDIA·Quantinuum 등의 기술층별 자산을 비교하고, 전문가와 범용 에이전트·공개 도구의 조합을 기준선으로 플랫폼의 방어 가능성과 전체 비용을 평가합니다.",
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "research integration, Korean writing, strategic analysis, publication preparation and deployed-page verification", "조사 통합·한국어 집필·전략 분석·게재 준비·공개 페이지 검증"),
            PublicAgent("papers", "primary-paper research and final factual audit", "원 논문 조사·최종 사실관계 감사"),
            PublicAgent("industry", "company, product and benchmark research and scope audit", "기업·제품·벤치마크 조사·주장 범위 감사"),
            PublicAgent("frontier", "latest-result verification and deterministic workflow diagram", "최신 결과 대조·결정론적 절차 도식 작성"),
            PublicAgent("moat_classiq", "Classiq technical-asset and public-alternative analysis", "Classiq 기술 자산·공개 대안 분석"),
            PublicAgent("moat_compare", "cross-company differentiation and execution-layer comparison", "기업별 차별화·실행 계층 비교"),
            PublicAgent("agent_bypass", "agent-substitution analysis and evaluation-design audit", "에이전트 대체 가능성·평가 설계 감사"),
            PublicAgent("publication_audit", "read-only publication pipeline and public-asset audit", "게시 파이프라인·공개 자산 읽기 감사"),
            PublicAgent("publication_copyedit", "publication prose and claim-boundary review", "게재 문체·주장 범위 검토"),
            PublicAgent("hero_illustration", "built-in image generation, cover export and visual inspection", "내장 이미지 생성·표지 저장 및 시각 검토"),
            PublicAgent("figures_layers", "original technology-layer and agent-path diagrams with source mapping", "기술층·에이전트 경로 도식 제작 및 근거 연결"),
            PublicAgent("evidence_figure", "primary-source value checks and redrawing of three independent result panels", "원문 수치 대조·서로 다른 성과의 독립 패널 재도식화"),
            PublicAgent("agent_visual_audit", "read-only review of expert-agent balance, actions, feedback and independent-checker boundaries in the cover", "표지의 전문가·에이전트 균형과 행동·피드백·독립 검증기 구분 감사"),
            PublicAgent("hero_agent_revision", "built-in cover-image editing to show expert-agent interaction, tool use and iterative revision", "내장 이미지 편집으로 전문가와 에이전트의 상호작용·도구 호출·반복 수정 표현"),
        ),
        verification_scope=(
            "Primary papers, official product documentation and author repositories available through 2026-10-19; publication dates, comparison metrics and execution settings",
            "Circuit-resource estimates, classical simulation and physical-QPU results distinguished; no independent model training, circuit reproduction or product benchmark",
            "Technical-asset analysis and conditional outlook; proposed same-agent platform comparison not executed; AI-generated conceptual cover, original SVG diagrams, redrawn reported values, public metadata, links and desktop/mobile publication checks",
        ),
        verification_scope_ko=(
            "2026-10-19까지 공개된 원 논문·공식 제품 문서·저자 저장소의 공개일·비교 지표·실행 환경 대조",
            "회로 자원 추정·고전 시뮬레이션·실제 QPU 결과 구분; 모델 학습·회로 계산·제품 벤치마크의 독립 재현 없음",
            "기술 자산 분석·조건부 전망; 동일 에이전트의 플랫폼 비교 실험 미실행; AI 생성 개념 표지·직접 작성한 SVG 도식·논문 보고값 재도식화·게시 metadata·링크·데스크톱 및 모바일 공개 페이지 검사",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-19",
        human_review_level="topic, strategic framing and public posting explicitly requested; no separately recorded line-by-line human review",
        human_review_level_ko="주제·전략적 관점·공개 게시 요청 확인; 별도 문장 단위 사람 검토 기록 없음",
        disclosure_note_ko="Anthropic의 39배는 특정 가역회로의 Toffoli 수와 최대 논리 큐비트 수의 곱이며 QPU 실행속도 배수가 아닙니다. ADAPT-GQE의 학습비 제외 비교와 12큐비트 실기기 검증, DQAOA-GPT의 GPU 시뮬레이션을 구분했습니다. QMill의 기능 보존과 Haiqu의 근사 상태 압축을 직접 같은 지표로 비교하지 않았습니다. Q-CTRL 비교 논문의 유료 자문 이해관계를 표시했습니다. 기업의 전략 자산과 향후 시나리오는 공개 기술 자료에 기초한 분석이며 독점 데이터·가격지배력·고객 유지율의 입증이 아닙니다. 표지는 내장 이미지 생성 도구로 제작한 개념 일러스트입니다. 수치 그림은 논문 보고값을 재도식화했으며, 기술층·경로 그림은 직접 작성한 개념도입니다. 그림의 기업 배치는 성능이나 사업적 방어력의 순위가 아닙니다. 정확한 작성 모델 식별자는 미보존입니다.",
        disclosure_note_en="The Anthropic 39x figure is a task-specific Toffoli-count times peak-logical-qubit metric, not measured QPU speed. Distinguished ADAPT-GQE inference comparisons excluding training and its 12-qubit hardware validation from DQAOA-GPT GPU simulations. Exact-function compression and approximate state compression are different tasks. Disclosed the paid-consultancy conflict in the Q-CTRL comparison paper. Strategic assets and future scenarios are analytical interpretations, not demonstrated proprietary-data advantages, pricing power or retention. The conceptual cover uses built-in image generation; the result panels redraw author-reported values, and the layer and pathway diagrams are original conceptual figures. Company placement does not rank performance or defensibility. Exact authoring-model identifier not retained.",
    ),
    PublicReview(
        folder="2026-10-18_materials-dataset-redundancy",
        title="OMat24 데이터 중복성과 국소 화학 환경을 이용한 학습 집합 압축",
        subtitle="원자 환경의 다양성, 예측 오차와 고정밀 기준 계산의 배분",
        date="2026-10-19", updated="2026-10-19", category="AI for Science",
        tags=("OMat24", "Dataset Redundancy", "EnvTok", "MACE", "Machine Learning Force Fields", "Materials AI", "Data Selection"),
        summary="OMat24의 약 0.5% 원자 예산으로 학습한 힘장 연구를 검토합니다. 99% 중복 주장의 분모, 힘·형성에너지 오차 증가와 MD 안정성을 구분하고, 국소 환경을 이용한 선별과 고정밀 라벨링의 적용 조건을 설명합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "source comparison, published-CSV arithmetic, Korean writing, conceptual cover, publication integration and live QA", "원문 대조·공개 CSV 산술·한국어 작성·개념 표지·게시 통합 및 공개 페이지 검증"),
            PublicAgent("identify_paper", "independent paper identification, prior-work research and English adaptation", "독립 논문 식별·선행연구 조사·영어판 작성"),
            PublicAgent("critical_audit", "independent numerical, methodological and evidence-scope audit", "독립 수치·방법론·주장 범위 감사"),
            PublicAgent("publication_build", "deterministic data figures, bilingual typesetting, font subsets, HTML/PDF generation and output QA", "결정론적 수치 도표·한영 조판·글꼴 subset·HTML/PDF 생성 및 출력 검사"),
        ),
        verification_scope=(
            "arXiv:2610.14392v1 main paper and supplementary information, OMat24 and DIRECT primary sources, prior redundancy study, pinned public code and Zenodo API metadata",
            "Arithmetic on author-reported outputs: atom and structure fractions, bulk force-component MAE and EnvTok formation-energy MAE over 466 valid rows; no new DFT, MLFF training or MD reproduction",
            "Bilingual interpretation boundaries, deterministic force-error chart, local assets, embedded-font PDFs, publication metadata, archive registration and desktop/mobile live links",
        ),
        verification_scope_ko=(
            "arXiv:2610.14392v1 본문·보충자료, OMat24·DIRECT 원논문과 중복성 선행연구, 고정 commit의 공개 코드·Zenodo API metadata 대조",
            "저자 공개 결과의 산술 확인: 원자·구조 비율, 벌크 힘 성분 MAE와 유효 466행의 EnvTok 형성에너지 MAE; DFT·힘장 학습·MD의 독립 재현 없음",
            "한영 해석 범위·결정론적 힘 오차 도표·로컬 자산·글꼴 포함 PDF·게시 metadata·아카이브 등록·데스크톱 및 모바일 공개 링크 검사",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-19",
        human_review_level="review preparation and public archiving explicitly requested; no line-by-line human approval",
        human_review_level_ko="리뷰 작성·공개 아카이브 요청 확인; 문장 단위 사람 승인 없음",
        disclosure_note_ko="99%는 모든 분자·재료 데이터의 보편적 중복률이 아닙니다. 원자 수 기준 약 0.55%와 구조 수 기준 약 1.22%를 구분했고, 벌크 힘 성분 MAE와 벡터 오차 크기, MD 평균 진행률과 실행 완료율을 구별했습니다. Li 장벽의 모델별 비수렴 제외·계산 수준·스핀 차이와 전체 기준 모델의 학습 조건 차이를 명시했습니다. OLED 및 고정밀 재라벨링은 후속 적용 제안입니다. 저자 공개 CSV의 산술을 확인했으며 모델을 재학습하지 않았습니다. 표지는 내장 imagegen 개념 그림이고 도표는 공개 수치의 재도식화입니다. 정확한 작성 모델 식별자는 미보존입니다.",
        disclosure_note_en="The 99% headline is not a universal redundancy rate for molecular or materials data. Distinguished approximately 0.55% of atoms from 1.22% of structures, force-component MAE from force-error vector norms, and mean MD trajectory completion from fully completed runs. Recorded model-specific Li nonconvergence exclusions, reference-theory and spin differences, and training-setting differences from the full-data reference. OLED applications and high-accuracy relabeling are proposals. Arithmetic on published CSVs was checked without retraining models. The built-in imagegen cover is conceptual; the chart redraws reported values. Exact authoring-model identifier not retained.",
    ),
    PublicReview(
        folder="2026-10-17_noether-symmetry-conservation",
        title="대칭에서 보존법칙으로: 노터 정리와 과학 계산의 설계 원리",
        subtitle="작용의 대칭에서 보존량을 유도하고, 시뮬레이션과 학습 모형을 설계하고 검사하는 기준으로 연결한다",
        date="2026-10-17", updated="2026-10-22", category="AI for Science",
        tags=("Noether’s Theorem", "Symmetry", "Conservation Laws", "Scientific Computing", "Scientific Machine Learning", "Molecular Dynamics", "Quantum Computing"),
        summary="용수철 계산에서 에너지가 늘어나는 이유를 출발점으로 작용의 대칭과 보존량을 설명합니다. 국소 보존·우주론·구조 보존 적분·HNN/LNN·원자간 퍼텐셜·양자 대칭 검증을 연결하며, 물리 모형·학습 함수·수치 계산의 정확성을 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex", ai_system_ko="OpenAI Codex",
        agents=(
            PublicAgent("root", "synthesis, Korean writing, conceptual cover, original figures and numerical examples; publication integration and live QA", "자료 종합·한국어 작성·개념 표지·설명 그림·계산 예제·게시 통합 및 공개 페이지 검증"),
            PublicAgent("academic_sources", "foundational primary-source research, formula checking and scholarly limitations audit", "기초 원전 조사·수식 확인·학술적 한계 검토"),
            PublicAgent("applications_sources", "scientific-computing and scientific-ML applications research, primary-source checking and English translation", "과학 계산·과학기계학습 응용 조사·1차 출처 확인·영어 번역"),
            PublicAgent("review_format", "repository-format audit, bilingual typesetting, HTML/PDF generation and output QA", "저장소 형식 감사·한영 조판·HTML/PDF 생성·출력 검사"),
            PublicAgent("publish_audit", "publication configuration, asset dependencies and deployment-path audit", "게시 설정·자산 의존성·배포 경로 감사"),
            PublicAgent("explanation_harness_review", "2026-10-22 Korean revision: argument continuity, first-use terms and interpretation of figures", "2026-10-22 한국어 개편: 논리 연결·첫 용어 설명·피규어 해석"),
            PublicAgent("v3_science_visual", "2026-10-22 primary-source recheck, scientific conditions and English revision", "2026-10-22 원전 재대조·과학적 조건 검토·영어 개편"),
            PublicAgent("final_audit", "2026-10-22 explanatory-figure revision, publication-path audit and named-video publication/privacy checks", "2026-10-22 설명 도표 개편·게시 경로 감사·영상 명명 허용목록 및 비공개 정보 검사"),
            PublicAgent("v3_video_renderer", "2026-10-22 bilingual video-abstract rendering, local synthetic narration and encoded-output checks", "2026-10-22 한영 비디오 abstract 렌더링·로컬 합성 내레이션·인코딩 출력 검사"),
            PublicAgent("noether_revision_reader", "2026-10-22 independent reading of the revised Korean argument without planning notes", "2026-10-22 기획 문서 없이 개정 국문 본문의 논지·연결 독립 검토"),
            PublicAgent("noether_output_qa", "2026-10-22 complete bilingual PDF visual inspection, responsive HTML and privacy/link checks", "2026-10-22 한영 PDF 전 페이지 시각 검수·반응형 HTML·비공개 경로 및 링크 검사"),
        ),
        verification_scope=(
            "Quanta source article, original papers and university lecture notes: bibliography, Noether transformation convention, field-theory and general-relativity boundaries, and computational application claims",
            "Independent harmonic-oscillator teaching calculation with three integrators; bilingual formulas and values, deterministic explanatory figures, HTML/PDF and desktop/mobile output checks",
            "Public-review registration, metadata and language/download links, font and figure dependencies, disclosure boundaries and GitHub Pages deployment configuration",
        ),
        verification_scope_ko=(
            "Quanta 출발 기사·원 논문·대학 강의노트의 서지, 노터 변환 관례, 장론·일반상대론의 성립 범위와 계산 응용 주장 대조",
            "세 적분기를 사용한 독립 조화진동자 설명 계산·한영 수식과 수치·결정론적 도표·HTML/PDF·데스크톱 및 모바일 출력 검사",
            "공개 리뷰 등록·metadata·언어 및 PDF 링크·글꼴과 그림 의존성·작성 공개 범위·GitHub Pages 배포 설정 검토",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-22",
        human_review_level="topic, revision and public posting explicitly requested; no line-by-line human approval or reader-comprehension study",
        human_review_level_ko="주제・개편・공개 게시 요청 확인; 문장 단위 사람 승인・독자 이해도 평가 없음",
        disclosure_note_ko="2026-10-22 개편에 공통 설명 준칙 1.0을 적용해 용어의 첫 설명, 문단 연결과 도표 해석을 보완하고 원전을 재대조했습니다. 진동자 계산은 교육 예제로 논문 실험 재현이나 비용을 맞춘 적분기 벤치마크가 아닙니다. HNN의 학습 함수 보존, 실제 에너지의 정확성, 수치 적분 오차와 이산 패리티 검증을 구분했습니다. OLED 연결은 응용 제안이며 독립 실험・양자 우위・소자 성능을 새로 검증하지 않았습니다. 기존 개념 표지 아래 한영 비디오 abstract를 추가했으며, 코드로 그린 과학 도식과 로컬 합성 내레이션을 사용했습니다. 각 언어의 자막과 시각 설명 transcript를 제공합니다. 사람의 청취·발음·이해도 평가는 수행하지 않았습니다. 정확한 작성 모델 식별자는 미보존입니다.",
        disclosure_note_en="The 22 October 2026 revision applies shared explanation guidance 1.0 to first-use terms, argument continuity and figure interpretation, with a primary-source recheck. The oscillator is a teaching calculation, not an experimental reproduction or cost-matched integrator benchmark. Conservation of an HNN's learned function, true-energy accuracy, integration error and discrete parity verification are distinguished. OLED applications remain proposals; no new experiment, quantum advantage or device validation is claimed. A bilingual video abstract below the existing conceptual cover uses scientific diagrams drawn in code and local synthetic narration, with language-specific captions and visual-description transcripts. No human listening, pronunciation or comprehension assessment was performed. Exact authoring-model identifier not retained.",
    ),
    PublicReview(
        folder="2026-10-06_quantum-quasiparticles-and-structured-computation",
        title="엑시톤에서 최적해까지: 물리적 구조가 바꾸는 양자계산 비용",
        subtitle="다중 엑시톤의 Bethe–Salpeter 모형, 구조를 이용한 어닐링·상태준비, 그리고 공정한 검증의 조건",
        date="2026-10-06", updated="2026-10-06", category="Quantum Computing",
        tags=("Excitons", "GW/BSE", "OLED", "FTQC", "D-Wave", "State Preparation", "QML", "QEC"),
        summary="엑시톤·GW/BSE의 물리부터 전체 해밀토니안 모형과의 자원 비교, 큐비트–게이트 절충과 상태준비 비용을 해설합니다. D-Wave의 최적해 다양성, ASPIRE, QML 정규화와 SMP 재분석을 통해 구조를 이용한 개선의 검증 조건을 짚습니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode", ai_system_ko="OpenAI Codex Work Mode",
        agents=(
            PublicAgent("Codex", "lead synthesis, Korean writing, mathematical teaching examples, deterministic figures, typesetting and publication verification", "전체 종합·한국어 작성·설명용 수식·결정론적 도표·조판·게시 검증"),
            PublicAgent("verify_oct6", "BSE and D-Wave primary-source verification", "BSE·D-Wave 원문 수치·자원 조건 검증"),
            PublicAgent("audit_oct6", "ASPIRE, quantum attention and SMP source checking; Korean scientific audit", "ASPIRE·quantum attention·SMP 원문 대조·한국어 과학 감수"),
            PublicAgent("english_oct6", "English adaptation and bilingual numerical integrity", "영어판 작성·한영 수치와 방법 경계 보존"),
            PublicAgent("cover_oct6", "conceptual image direction and visual inspection", "개념 표지 구성·이미지 생성·시각 검수"),
        ),
        verification_scope=(
            "Five arXiv v1 preprints submitted 2026-10-02: methods, reported numbers, resource settings, comparators and execution boundaries",
            "Official SaTQuML dates and non-archival status; paper-level acceptance is author-reported and not independently confirmed",
            "Bilingual equations and HTML, deterministic explanatory SVGs, embedded-font PDFs and public publication links",
        ),
        verification_scope_ko=(
            "2026-10-02 제출 arXiv v1 5편의 방법·보고 수치·자원 설정·기준선·실행 경계 대조",
            "공식 SaTQuML 개최일·non-archival 상태 확인; 논문별 채택 결정은 독립 확인하지 못한 저자 표기",
            "한영 수식·HTML·설명용 SVG·글꼴 포함 PDF·공개 게시 링크 검사",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-06",
        human_review_level="topic, physically literate audience, tone and public posting explicitly requested; no line-by-line human approval",
        human_review_level_ko="주제·물리적 소양을 갖춘 독자·문체·공개 게시 요청 확인; 문장 단위 사람 승인 없음",
        disclosure_note_ko="scientific-stop-slop-ko 감수로 수치·단위·기준선·방법 경계를 보존했습니다. BSE는 미래 내결함성 자원추정, D-Wave는 실제 어닐러, ASPIRE·QML은 고전 모사, SMP는 공개 QPU 자료의 고전 재분석입니다. OLED 적용과 비용 장부는 리뷰어 해석·설명 예제입니다. 워크숍의 개별 OpenReview decision은 접근 제한으로 독립 확인하지 못했습니다. 독립 실험 재현·양자 우위·OLED 소자 성능 검증은 수행하지 않았습니다. 표지는 내장 imagegen 개념 일러스트이며 수식·도표는 결정론적으로 제작했습니다.",
        disclosure_note_en="Applied scientific-stop-slop-ko to preserve values, units, comparators and method boundaries. BSE estimates future fault-tolerant resources; D-Wave runs an actual annealer; ASPIRE and QML use classical simulation; SMP classically re-decodes public QPU data. OLED applications and the cost ledger are reviewer interpretations or teaching examples. The individual OpenReview decision could not be independently checked because of access restrictions. No independent experimental reproduction, quantum-advantage or OLED-device validation was performed. The built-in imagegen cover is conceptual; equations and explanatory figures are deterministic.",
    ),
    PublicReview(
        folder="2026-10-03_vqe-energy-subspaces-and-digital-validation",
        title="VQE의 현재와 다음 단계: 에너지 최소화, 부분공간 계산, 디지털 검증",
        subtitle="분자와 스핀계의 바닥상태를 구하는 원리부터 DecaQ의 400스핀 사례, HI-VQE·SQD와 OLED 응용의 조건까지",
        date="2026-10-03", updated="2026-10-03", category="Quantum Computing",
        tags=("VQE", "DecaQ", "Quantum Chemistry", "HI-VQE", "SQD", "QSCI", "FTQC", "OLED"),
        summary="VQE의 변분 원리·측정 비용·최적화와 부분공간 방법을 연결하고, DecaQ의 400스핀 사례가 검증한 범위를 분석합니다. 같은 규모 수치를 갖는 독립 설명 예제와 두 스핀 인터랙티브 계산으로 상태 표현력과 계산 난도를 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode", ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual technical synthesis, scientific copyediting, original numerical examples, visual direction, interactive explanation and publication verification", "1차 출처 조사·한영 기술 종합·과학 감수·독립 수치 예제·표지 구성·인터랙티브 해설·게시 검증"),),
        verification_scope=(
            "Public LinkedIn post, DecaQ product scope and company release; original VQE and subspace-method papers and current IBM HI-VQE documentation",
            "Independent teaching examples: four-spin dense diagonalization, 400-spin commuting product-state energy and term count, two-spin analytical spectra and variational bounds; not a DecaQ reproduction",
            "Bilingual HTML, protected equations, figures, interactive energy calculations, publication metadata and public links; one authoring agent, no independent review agent",
        ),
        verification_scope_ko=(
            "LinkedIn 공개 본문·DecaQ 제품 범위와 회사 보도자료·VQE 및 부분공간 원 논문·현재 IBM HI-VQE 문서",
            "독립 설명 예제: 4스핀 조밀 대각화·400스핀 가환 곱상태 에너지와 항 수·2스핀 분석적 스펙트럼과 변분 상한; DecaQ 재현 아님",
            "한영 HTML·수식 보호·도표·인터랙티브 에너지 계산·공개 metadata와 링크; 작성 에이전트 1개, 독립 리뷰 에이전트 없음",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-03",
        human_review_level="topic and public posting explicitly requested; no line-by-line human review",
        human_review_level_ko="주제와 공개 게시 요청 확인; 문장 단위 사람 검토 없음",
        disclosure_note_ko="공개 포스트의 첨부 백서는 읽지 못했으므로 정확한 해밀토니안·엔진·실행시간을 독립 확인하지 않았습니다. DecaQ 수치는 작성자 보고이며, 회사는 범용 고전 하드웨어 실행을 설명합니다. 리뷰의 계산 예제는 원 결과의 재현이 아닙니다. HI-VQE·SQD 논문의 실행 경계와 Deep QSCI의 무잡음 고전 시뮬레이션을 구분했습니다. 실제 QPU 실행·양자 우위·OLED 소자 성능을 새로 검증하지 않았습니다. scientific-stop-slop-ko 감수를 적용했고 표지는 내장 imagegen, 정확한 도표는 분석식·SVG로 제작했습니다. 단일 에이전트 작업입니다.",
        disclosure_note_en="The attached white paper was unreadable, so the exact Hamiltonian, engine and runtime were not independently verified. DecaQ numbers are author-reported; the company describes general-purpose classical execution. The review's numerical examples do not reproduce the vendor result. Distinguished HI-VQE and SQD execution evidence from Deep QSCI's noiseless classical simulation. No new physical QPU, quantum-advantage or OLED-device validation was performed. Applied scientific-stop-slop-ko copyediting; the cover uses built-in imagegen and precise figures use analytical formulas and SVG. Single-agent work.",
    ),
    PublicReview(
        folder="2026-10-02_weekly-oled-inverse-design-triplet-state-control",
        title="청색 OLED의 삼중항 준위 제어와 분자 역설계 검증의 연결",
        subtitle="2026년 9월 25일–10월 1일 연구 동향 | bridged resonance 소자, 마스킹 생성, 합성경로, Deep QSCI와 제약 보존 QAOA",
        date="2026-10-02", updated="2026-10-02", category="Materials AI",
        tags=("OLED", "TADF", "Triplet-State Control", "Molecular Inverse Design", "Masked Diffusion", "Synthesizability", "QSCI", "QAOA"),
        summary="청색 OLED의 bridged resonance 설계가 삼중항 상태 제어와 최대 EQE 42.6%를 연결한 직접 근거를 중심으로, 마스킹 분자 생성·합성경로·π 적층 전자구조·제약 보존 QAOA를 하나의 검증 사슬로 읽습니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode", ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual synthesis, scientific copyediting, image direction, deterministic evidence figure, PDF and publication verification", "1차 출처 조사·한영 종합·과학 감수·이미지 구성·결정론적 근거 도표·PDF 및 게시 검증"),),
        verification_scope=(
            "One peer-reviewed Nature Communications article and four arXiv v1 records first published 2026-09-25 through 2026-10-01; metadata, methods, datasets, reported values and execution boundaries",
            "bilingual rendering, verified four-page PDF, metadata, local and reference links, figures and shared thumbnail",
            "single-agent source checking; no independent calculation, synthesis, OLED-device reproduction or QPU execution",
        ),
        verification_scope_ko=(
            "2026-09-25~10-01 처음 공개된 Nature Communications 동료평가 논문 1편과 arXiv v1 기록 4편의 서지·방법·데이터셋·보고 수치·실행 경계",
            "한영 렌더링·검증한 4쪽 PDF·metadata·로컬 및 참고 링크·그림과 공용 썸네일",
            "단일 에이전트 출처 대조; 계산·합성·OLED 소자·QPU 실행의 독립 재현 없음",
        ),
        primary_sources_checked=True, evidence_cutoff="2026-10-01",
        human_review_level="recurring publication authorized; no line-by-line human review",
        human_review_level_ko="정기 공개 게시 요청에 따라 작성; 문장 단위 사람 검토 없음",
        disclosure_note_ko="웹 조사·이전 호 중복 확인·GitHub 연결·로컬 PDF와 링크 검사·내장 imagegen을 사용했습니다. Nature Communications의 색인과 DOI metadata, arXiv 전문 4편을 대조했습니다. 출판사 원문이 인증 경로로 리디렉션되어 청색 OLED 논문의 상세 수치표는 독립 추출하지 못했으며 확인하지 않은 값을 보충하지 않았습니다. 양자 두 연구는 무잡음 고전 시뮬레이션이지 실제 QPU 실행 또는 양자 우위가 아닙니다. OLED 적용안과 주간 실험안은 리뷰어 제안입니다.",
        disclosure_note_en="Used web research, duplicate checking against earlier issues, GitHub publication, local PDF and link checks, and built-in imagegen. Checked the Nature Communications index and DOI metadata plus four full arXiv records. The publisher full text redirected through authentication, so detailed numerical tables for the blue-OLED paper were not independently extracted and unverified values were not added. Both quantum studies use noiseless classical simulation, not physical QPU execution or demonstrated quantum advantage. OLED translations and the weekly experiment are reviewer proposals.",
    ),
    PublicReview(
        folder="2026-10-01_condensed-matter-topology-learning-thermal-computing",
        title="적층 위상질서와 AI의 통계물리: 계층 학습과 열잡음 계산",
        subtitle="JCCM 2026년 9월 선정 논문 6편 — 새로운 위상상, 표본 복잡도와 물리적 계산의 검증 경계",
        date="2026-10-01", updated="2026-10-01", category="AI for Science",
        tags=("Condensed Matter", "Topological Order", "Fractional Quantum Hall", "Statistical Learning", "Thermodynamic Computing"),
        summary="JCCM 9월 선정 논문 6편을 읽고 Fibonacci 위상질서와 무리수 통계각의 차이, 계층 데이터의 학습 문턱, 열잡음 생성·분류 계산을 해설합니다. 무한층 이론·합성 데이터·시뮬레이션 및 에너지 추정의 범위를 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode", ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual synthesis, scientific copyediting, image direction, deterministic schematics and publication verification", "1차 자료 조사·한영 종합·과학 감수·표지 구성·결정론적 설명 그림·게시 검증"),),
        verification_scope=("September 2026 JCCM selection pages and six original-paper arXiv texts; publication and version metadata", "protected formulas, reported accuracy and energy-accounting boundaries; no independent numerical or experimental reproduction", "bilingual HTML, metadata, reference links, generated conceptual cover and three original SVG schematics; one agent, no independent review agent"),
        verification_scope_ko=("JCCM 2026년 9월 공개 추천 페이지와 원 논문 6편의 arXiv 본문·게재 및 버전 정보", "주요 수식·보고 정확도·에너지 산정 범위 대조; 수치 계산·실험의 독립 재현 없음", "한영 HTML·metadata·참고 링크·생성 개념 표지·설명 SVG 3종; 단일 에이전트, 독립 검증 에이전트 없음"),
        primary_sources_checked=True, evidence_cutoff="2026-10-01",
        human_review_level="topic and publication explicitly requested; no separate line-by-line human review",
        human_review_level_ko="주제 및 공개 게시 요청 확인; 별도 문장 단위 사람 검토 없음",
        disclosure_note_ko="공개 추천 페이지와 선정 논문 본문을 대조했습니다. JCCM 해설 PDF는 접근 제한으로 읽지 못했으며, 열역학 계산 두 편의 기술 검토에는 공개 프리프린트를 사용했습니다. 물리 장치·위상상·에너지 이점을 새로 검증하지 않았습니다. 후속 연구안은 리뷰어 제안입니다. scientific-stop-slop-ko 출판 감수를 적용했고 표지는 내장 imagegen으로 생성했습니다. 정확한 작성 모델 식별자는 미보존입니다.",
        disclosure_note_en="Checked the public selection pages against the six original papers. The JCCM commentary PDFs were inaccessible; the two thermodynamic-computing analyses use public preprints. No new device, topological-phase or energy-advantage validation was performed. Follow-up experiments are reviewer proposals. scientific-stop-slop-ko publication copyediting was applied; the cover uses built-in imagegen. Exact authoring-model identifier not retained.",
    ),
    PublicReview(
        folder="2026-09-25_weekly-oled-inverse-design-generative-validation",
        title="광전자 분자 역설계의 신뢰도를 규정하는 생성 검증과 화학적 초기화",
        subtitle="2026년 9월 18–24일 연구 동향 | variable-size 3D 생성의 수정된 DFT 검증, 다중 제약 에이전트, 치환기 효과와 UCCSD-VQE trainability",
        date="2026-09-25", updated="2026-09-25", category="Materials AI",
        tags=("OLED", "Molecular Inverse Design", "Molecular Generation", "Latent Flow", "Chemical Agents", "Substituent Effects", "VQE", "Validation"),
        summary="직접적인 TADF·PhOLED 신작이 없던 주간에 variable-size 3D 생성의 수정된 DFT 검증, 다중 제약 에이전트, 치환기 외삽과 화학적 초기화의 UCCSD-VQE trainability를 함께 읽고, 광전자 분자 역설계의 독립 검증 gate를 제안합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex",
        ai_system_ko="OpenAI Codex",
        agents=(PublicAgent("Codex", "primary-source research, bilingual synthesis, scientific copyediting, image direction, deterministic evidence figure, PDF and publication verification", "1차 출처 조사·한영 종합·과학 감수·이미지 구성·결정론적 근거 도표·PDF 및 게시 검증"),),
        verification_scope=("Four arXiv records posted or meaningfully revised 2026-09-18 through 2026-09-24: version history, methods, datasets, reported numerical results and execution boundaries", "bilingual rendering, verified five-page PDF, metadata, local and reference links, figures and thumbnail consistency", "single-agent source checking; no independent computational reproduction, synthesis or device-level OLED validation"),
        verification_scope_ko=("2026-09-18~24 공개·의미 있게 개정된 arXiv 기록 4편: 버전 이력·방법·데이터셋·보고 수치·실행 경계", "한영 렌더링·검증한 5쪽 PDF·metadata·로컬 및 참고 링크·그림과 썸네일 정합성", "단일 에이전트 출처 대조; 계산 독립 재현·합성·OLED 소자 수준 검증 없음"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-24",
        human_review_level="recurring publication authorized; no line-by-line human review",
        human_review_level_ko="정기 공개 게시 요청에 따라 작성; 문장 단위 사람 검토 없음",
        disclosure_note_ko="웹 조사·기존 브리프 중복 확인·GitHub 연결·로컬 PDF와 링크 검사·내장 imagegen을 사용했습니다. 한 편은 COLM 2026, 한 편은 EMNLP 2026 채택 논문이고 나머지는 프리프린트이며, 직접적인 신규 TADF·PhOLED 논문은 없습니다. VQE 연구는 정확한 고전 수치 계산으로 실제 QPU·샷 잡음·양자 우위를 검증하지 않았습니다. OLED 적용안과 주간 실험안은 리뷰어 제안입니다.",
        disclosure_note_en="Used web research, duplicate checking against earlier briefs, GitHub connection, local PDF and link checks, and built-in imagegen. One item is accepted at COLM 2026, one at EMNLP 2026 and the remainder are preprints; none is a direct new TADF or PhOLED study. The VQE study uses exact classical numerical evaluation and does not demonstrate QPU execution, shot noise or quantum advantage. OLED workflow translations and the weekly experiment are reviewer proposals.",
    ),
    PublicReview(
        folder="2026-09-21_jev-structured-decisions-agent-harnesses",
        title="에이전트의 작은 판단을 빠르게: Jev의 구조화된 결정과 적용 한계",
        subtitle="System One 모델의 인터페이스·확률 보정·초기 평가를 읽고 연구 하네스의 적용 조건을 살피다",
        date="2026-09-21", updated="2026-09-21", category="Agent Systems",
        tags=("Jev", "TypeSafe", "Agent Harness", "Calibration", "Evaluation", "Structured Decisions"),
        summary="Jev의 판단 인터페이스와 초기 평가를 살피고, 7초 항공편 검색의 혼합 모델 구조·요금 계산과 주행 시뮬레이터의 코드 검사를 분석합니다. 빠른 판단을 실제 행동으로 연결하는 조건과 시연의 한계를 설명합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode", ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source review, bilingual writing, scientific copyediting, original figures, aggregate arithmetic and publication checks", "1차 자료 대조·한영 집필·과학 감수·그림 제작·집계값 산술과 게시 검사"),),
        verification_scope=("TypeSafe documentation and release, LangChain experiment and public repository pinned at adfea74905f721ea2594e22804c8c8edf1693163", "reported means, public JSON aggregate variance ratios and five-case/100-repeat design; no live API or benchmark reproduction", "shared LinkedIn post; Jev Ultrafast 1231850 and JevPilot e1beeb1 documentation/code; flight cost arithmetic; trader public page only, no demo execution", "bilingual HTML, generated hero, deterministic SVGs, metadata and local assets; one agent with no independent verification agent"),
        verification_scope_ko=("TypeSafe 공식 문서·발표, LangChain 실험과 adfea74905f721ea2594e22804c8c8edf1693163 시점 공개 저장소", "보고 평균값·공개 JSON 집계 분산 비율·5개 사례 및 100회 반복 설계; API 호출·벤치마크 재현 없음", "공유 LinkedIn 게시물, Jev Ultrafast 1231850·JevPilot e1beeb1 문서·코드, 항공편 요금 산술; 거래 데모 공개 화면만 확인, 데모 실행 없음", "한영 HTML·생성 표지·결정론적 SVG·metadata·로컬 자산; 단일 에이전트, 독립 검증 에이전트 없음"),
        primary_sources_checked=True, evidence_cutoff="2026-09-21",
        human_review_level="topic and conditional publication requested; no separate line-by-line human review",
        human_review_level_ko="주제와 가치 판단 후 게시 요청 확인; 별도 문장 단위 사람 검토 없음",
        disclosure_note_ko="공식 문서와 초기 실험을 대조한 기술 리뷰입니다. API 성능을 새로 측정하지 않았습니다. 코드로 보고값 비율과 그림을 계산했으며 하네스 적용안은 리뷰 제안입니다. scientific-stop-slop-ko 출판 감수를 적용했습니다. 정확한 작성 모델 식별자는 미보존입니다.",
        disclosure_note_en="A technical review of official documentation and an early experiment, without new API measurements. Code computes reported-value ratios and figures; harness applications are reviewer proposals. scientific-stop-slop-ko publication copyediting applied. Exact authoring-model identifier not retained.",
    ),
    PublicReview(
        folder="2026-09-19_transfer-learning-chemical-bayesian-optimization",
        title="과거 실험을 재사용하는 화학 베이지안 최적화: 전이학습의 이점과 한계",
        subtitle="Digital Discovery 게재 연구의 공개 초록·코드와 차원에 맞춘 GP 사전 설정을 읽다",
        date="2026-09-19",
        updated="2026-09-19",
        category="Materials AI",
        tags=("Bayesian Optimization", "Transfer Learning", "Gaussian Process", "Molecular Representation", "Negative Transfer", "OLED"),
        summary="과거 반응 데이터를 새 화학 후보 탐색에 재사용하는 두 단계 전이를 해설합니다. 차원에 맞춘 GP 하이퍼프라이어, 공개 코드의 A–B–C 단계 구분과 음의 전이, OLED 평가 조건을 살피며 본문 미열람에 따른 검토 범위를 명시합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source and code inspection, bilingual writing, scientific copyediting, illustration direction, original SVGs and publication checks", "1차 자료·코드 대조, 한영 집필, 과학 감수, 일러스트 구성, SVG 제작과 게시 검사"),),
        verification_scope=("publication DOI and author announcement; complete Crossref-registered preprint v2 abstract; predecessor publisher abstract and metadata; LogEI abstract", "TL-ChemBO commit a35276c: implementation inspection, stub-based task-label probe and hyperprior construction checks; no BO campaign reproduction", "bilingual HTML, original generated illustration and SVGs, publication metadata and local assets; final journal full text and supplement unavailable"),
        verification_scope_ko=("게재 DOI·저자 발표, Crossref 등록 공개 원고 v2 전체 초록, 선행 연구 출판사 초록·서지, LogEI 초록", "TL-ChemBO a35276c 구현 대조, 의존성을 대체한 단계 라벨 검사와 하이퍼프라이어 구성 확인; 전체 BO 캠페인 재현 없음", "한영 HTML·생성 개념 그림·SVG, 게시 metadata와 로컬 자산; 최종 게재본 본문·보충자료 미열람"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-19",
        human_review_level="topic and publication explicitly requested; no separate line-by-line human review",
        human_review_level_ko="주제 및 공개 게시 요청 확인; 별도 문장 단위 사람 검토 없음",
        disclosure_note_ko="단일 Codex 에이전트가 웹·서지 API·공식 GitHub 코드·내장 imagegen으로 작성했습니다. scientific-stop-slop-ko 출판 감수를 적용했습니다. 독립 검증 에이전트는 사용하지 않았습니다. 출판사와 ChemRxiv의 접근 제한으로 최종 논문·보충자료 성능 수치를 검증하지 않았으며, OLED 평가안은 리뷰 제안입니다.",
        disclosure_note_en="A single Codex agent used web research, bibliographic APIs, official GitHub code and built-in imagegen, with scientific-stop-slop-ko publication copyediting. No independent verification agent was used. Publisher and ChemRxiv access restrictions prevented verification of final article and supplementary performance values. The OLED evaluation design is proposed by this review.",
    ),
    PublicReview(
        folder="2026-09-18_weekly-oled-inverse-design-sparse-excited-state-validation",
        title="희소한 여기상태 조건을 겨냥한 분자 역설계의 검증 기준",
        subtitle="2026년 9월 11–17일 연구 동향 | 생성 공간, 삼중항 환경, DMRG·에이전트 검증과 VQE 누설",
        date="2026-09-18",
        updated="2026-09-18",
        category="Materials AI",
        tags=("OLED", "Excited States", "Molecular Inverse Design", "Singlet Fission", "DMRG", "Active Learning", "VQE", "Validation"),
        summary="직접적인 TADF·PhOLED 신작이 없던 주간에 약 1억 개 생성 구조의 여기상태 선별, 호스트가 지배하는 삼중항 스핀 결맞음, DMRG·에이전트 검증과 대칭 누설 VQE를 함께 읽고 OLED 역설계로 옮길 때 필요한 검증 계층을 제안합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex",
        ai_system_ko="OpenAI Codex",
        agents=(PublicAgent("Codex", "primary-source research, bilingual synthesis, scientific copyediting, image direction, deterministic figures, PDF and publication verification", "1차 출처 조사·한영 종합·과학 감수·이미지 구성·결정론적 도해·PDF 및 게시 검증"),),
        verification_scope=("Eight arXiv preprints posted 2026-09-11 through 2026-09-16: metadata, methods, datasets, reported numerical results and execution boundaries", "bilingual rendering, PDF visual inspection, metadata, local and reference links, figures and thumbnail consistency", "single-agent source checking; no independent computational reproduction or device-level OLED validation"),
        verification_scope_ko=("2026-09-11~16 공개 arXiv 프리프린트 8편: 서지·방법·데이터셋·보고 수치·실행 경계", "한영 렌더링·PDF 시각 검사·metadata·로컬 및 참고 링크·그림과 썸네일 정합성", "단일 에이전트 출처 대조; 계산 독립 재현이나 OLED 소자 수준 검증 없음"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-17",
        human_review_level="recurring publication authorized; no line-by-line human review",
        human_review_level_ko="정기 공개 게시 요청에 따라 작성; 문장 단위 사람 검토 없음",
        disclosure_note_ko="웹 조사·기존 브리프 중복 확인·GitHub 연결·로컬 PDF 및 링크 검사·내장 imagegen을 사용했습니다. 8편 모두 프리프린트이며 직접적인 신규 TADF·PhOLED 논문은 없습니다. 양자 결과는 잡음 없는 상태벡터 시뮬레이션으로 실제 QPU 실행이나 양자 우위를 뜻하지 않습니다. OLED 적용안과 주간 실험안은 리뷰어 제안입니다.",
        disclosure_note_en="Used web research, duplicate checking against earlier briefs, GitHub connection, local PDF and link checks, and built-in imagegen. All eight items are preprints and none is a direct new TADF or PhOLED study. The quantum result is a noiseless statevector simulation, not QPU execution or quantum advantage. OLED workflow translations and the weekly experiment are reviewer proposals.",
    ),
    PublicReview(
        folder="2026-09-13_avatar-scientific-workflow-control",
        title="연구 에이전트는 언제 개입해야 하는가: Avatar가 드러낸 판단의 비용",
        subtitle="과학 워크플로의 복구·자원 확장·종료 판단에서 규칙과 LLM을 비교한 실험",
        date="2026-09-13",
        updated="2026-09-13",
        category="Agent Systems",
        tags=("Scientific Workflows", "Agent Systems", "HPC", "On-premises AI", "Evaluation", "Materials AI"),
        summary="Avatar는 같은 실행 구조에서 규칙과 LLM 판단을 비교합니다. QM9 조회 기반 탐색의 GPU 사용시간 약 40% 감소와 자원 제어의 대기열 악화를 함께 분석하고, 실제 DFT·총비용·강한 기준선 검증이 남은 이유를 설명합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex",
        ai_system_ko="OpenAI Codex",
        agents=(PublicAgent("Codex", "primary-source research, bilingual writing, scientific copyediting, image direction, deterministic SVG, code and publication checks", "1차 출처 조사·한영 집필·과학 감수·이미지 구성·SVG 제작·코드 및 게시 검사"),),
        verification_scope=("Avatar v1 full text: policy placement, workload definitions, dates, numerical comparisons and execution boundaries; Academy and Colmena official documentation", "round-count arithmetic; bilingual rendering, unit tests, public-site validator, metadata, local and reference links, thumbnail consistency", "single-agent source checking; no independent experiment reproduction or separate verification agent"),
        verification_scope_ko=("Avatar v1 본문: 정책 배치·작업 정의·날짜·수치 비교·실행 범위; Academy·Colmena 공식 문서", "회차 비율 산술·한영 렌더링·단위 테스트·공개 사이트 검사·metadata·로컬 및 참고 링크·표지 정합성", "단일 에이전트 출처 대조; 별도 검증 에이전트나 실험 독립 재현 없음"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-12",
        human_review_level="recurring publication authorized; no line-by-line human review",
        human_review_level_ko="정기 공개 게시 요청에 따라 작성; 문장 단위 사람 검토 없음",
        disclosure_note_ko="웹 조사·GitHub 연결·로컬 Python 검사·브라우저 확인·내장 imagegen을 사용했습니다. 정확한 모델 식별자는 미보존입니다. GPU 시간은 저자 보고이며 QM9 조회는 신규 DFT 실행이 아닙니다. 총 추론 비용·일반화는 미확인이고 운영 구조는 후속 제안입니다.",
        disclosure_note_en="Used web research, GitHub connection, local Python checks, browser inspection and built-in imagegen. Exact model identifier not retained. GPU time is author-reported; QM9 lookup is not new DFT execution. Total inference cost and generalization remain unverified; the operational design is proposed.",
    ),
    PublicReview(
        folder="2026-09-13_multiphoton-reservoir-classical-light",
        title="빛의 세기에서 광자 수 분포로: 다광자 저장소 계산을 읽다",
        subtitle="고전광·편광·OAM에서 861개 특징, 측정시간과 고전 시뮬레이션 조건까지",
        date="2026-09-13",
        updated="2026-09-13",
        category="Quantum Computing",
        tags=("Photonic Computing", "Quantum Reservoir", "Classical Light", "Photon Counting", "OAM", "Classical Simulation", "Measurement Cost"),
        summary="고전광과 광자 계수로 만든 저장소의 원리를 설명하고, 보충자료의 함수별 성능·유효차원·약 32분 취득시간을 검토합니다. 검출기 교정과 고전 표본화 조건을 살피며 센싱·재료 응용의 다음 실험을 제안합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual writing, conceptual illustration direction, deterministic figures, scientific copyediting, implementation and publication verification", "1차 출처 조사·한영 집필·개념 일러스트 구성·수식 도표·과학 감수·구현·게시 검증"),),
        verification_scope=("Hong et al. Advanced Science e77225 main article and 15-page Supporting Information; phase-space classical simulation primary paper", "Table S2 transcription, source configurations, feature dimensions, acquisition costs, detector-model limits and sampling-versus-probability distinction", "bilingual HTML, generated conceptual hero, two original SVG figures, CSV data, local links and publication metadata"),
        verification_scope_ko=("Hong 등 Advanced Science e77225 본문·15쪽 보충자료, 위상공간 고전 시뮬레이션 선행 원문", "표 S2 전사·실험별 광원·특징 차원·취득비용·검출 모델 한계·확률 계산과 표본화 구분", "한영 HTML·생성 개념 표지·SVG 도표 2점·CSV·로컬 링크·게시 정보"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-13",
        human_review_level="topic and public publication explicitly requested; no separate line-by-line human review",
        human_review_level_ko="주제 및 공개 게시 요청 확인. 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko="실험 데이터와 시간을 독립 재현하지 않았습니다. 높은 광자 수 계수와 검출 모델의 연결은 추가 확인이 필요합니다. 고전 표본화 구성과 응용 방향은 리뷰어의 해석·제안이며, 표지는 생성 개념 그림입니다.",
        disclosure_note_en="Experimental data and timings were not independently reproduced. High-count detection and its model need further reconciliation. The classical sampling construction and applications are editorial analysis and proposals; the generated hero is conceptual.",
    ),
    PublicReview(
        folder="2026-09-11_weekly-oled-inverse-design-excitonic-reliability",
        title="집단 엑시톤과 오차 예산이 규정하는 광여기 분자 역설계의 신뢰도",
        subtitle="2026년 9월 4–10일 연구 동향 | 공액고분자 탈위상, 3D 생성, 실패 탐지, 비단열·양자 자원 평가",
        date="2026-09-11",
        updated="2026-09-11",
        category="Materials AI",
        tags=("OLED", "Exciton Dephasing", "Molecular Inverse Design", "3D Generation", "MLIP Validation", "Nonadiabatic Dynamics", "VQE", "Quantum Error Mitigation"),
        summary="직접적인 TADF·PhOLED 신작이 없던 주간에, 공액고분자의 집단 엑시톤 탈위상 실험을 핵심으로 3D 분자 생성, MLIP 실패 탐지, 비단열 결합, 유효 퍼텐셜, OOD 역설계와 양자 계산의 오차·샷 비용을 함께 평가합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual writing, illustration direction, deterministic evidence figures, scientific copyediting, implementation and publication verification", "1차 출처 조사·한영 집필·일러스트 구성·근거 도표·과학 감수·구현·게시 검증"),),
        verification_scope=("eight arXiv preprints posted or revised 2026-09-04 through 2026-09-10, checked against primary abstract and full-text pages", "reported numerical results, benchmark conditions, QPU versus simulator execution, sampling costs, and OLED translation boundaries", "bilingual HTML, conceptual hero, two reviewer-constructed SVG figures, verified five-page PDF, metadata and local links"),
        verification_scope_ko=("2026년 9월 4–10일 게시·개정된 arXiv 프리프린트 8건의 초록·본문 확인", "보고 수치·벤치마크 조건·QPU와 시뮬레이터 경계·샷 비용·OLED 전이 조건", "한영 HTML·개념 대표 이미지·리뷰어 구성 SVG 2점·검증한 5쪽 PDF·게시 정보·로컬 링크"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-10",
        human_review_level="scheduled publication requested; no separate line-by-line human review",
        human_review_level_ko="정기 게시 요청에 따라 작성. 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko="선정 자료는 모두 프리프린트이며 직접적인 신규 TADF·PhOLED·호스트-도펀트 소자 논문은 없었습니다. 수치를 독립 재현하지 않았고 OLED 적용과 주간 실험안은 리뷰어의 제안입니다. 생성 대표 이미지는 개념 그림입니다.",
        disclosure_note_en="All selected items are preprints, and no directly relevant new TADF, PhOLED, or host–dopant device paper appeared. Numerical results were not independently reproduced; OLED translations and the weekly experiment are reviewer proposals. The generated hero is conceptual.",
    ),
    PublicReview(
        folder="2026-09-11_quantum-ai-brain-frontiers",
        title="양자진공에서 AI 수학 증명과 기억 조절까지",
        subtitle="강한 빛·입자 충돌·Navier–Stokes·신경 자극을 원리와 실험으로 읽는 과학 리뷰",
        date="2026-09-11",
        updated="2026-09-11",
        category="AI for Science",
        tags=("Quantum Vacuum", "Collider Physics", "Quantum Information", "AI Mathematics", "Navier-Stokes", "Neuroscience", "Memory", "El Nino"),
        summary="진공 복굴절, 충돌의 양자 상관관계, AI가 공개한 유체방정식 증명, 말초 신경 자극과 기억을 깊게 읽습니다. 일러스트 5장·도표 6개·편광 조작 예제로 원리를 설명하고, 확인된 결과와 미검증 주장 및 짧은 엘니뇨 전망을 구분합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual writing, illustration direction, deterministic figures, scientific copyediting, implementation and publication verification", "1차 출처 조사·한영 집필·일러스트 구성·수치 도표·과학 감수·구현·게시 검증"),),
        verification_scope=("20 primary or official references with explicit full-text and abstract boundaries", "physical quantities, mathematical problem scope, execution platform, neural target, observation versus prediction", "bilingual HTML, five original illustrations, six deterministic SVG figures, interactive polarization relation, metadata and local links"),
        verification_scope_ko=("1차·공식 자료 20건의 본문·초록 확인 범위 명시", "물리량·수학 문제 범위·계산 플랫폼·신경 표적·관측과 예측 구분", "한영 HTML·원본 일러스트 5장·SVG 도표 6개·편광 조작 예제·게시 정보·로컬 링크"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-10",
        human_review_level="topic and public publication explicitly requested; no separate line-by-line human review",
        human_review_level_ko="주제 및 공개 게시 요청 확인. 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko="잡지 전문과 신규 얼굴 자극 논문은 확인하지 못했습니다. 관련 선행 연구로 주제를 검토했으며 Lean 전체 증명·벤치마크·실험을 독립 재현하지 않았습니다. 생성 이미지는 개념 그림입니다.",
        disclosure_note_en="Magazine full text and the new facial-stimulation paper were unavailable. Named primary studies support the subject review; full Lean verification, benchmarks and experiments were not reproduced. Generated images are conceptual.",
    ),
    PublicReview(
        folder="2026-09-10_cash-qse-classical-quantum-chemistry",
        title="분자 계산의 일을 나누는 법: CASH-QSE로 이해하는 고전·양자 협업",
        subtitle="전자상관·활성공간·직교 부분공간과 측정비용을 이해하는 심층 리뷰",
        date="2026-09-10",
        updated="2026-09-10",
        category="Quantum Computing",
        tags=("CASH-QSE", "Quantum Chemistry", "CASSCF", "Active Space", "VQE", "Measurement", "OLED"),
        summary="전자상관과 활성공간의 배경부터 고전 기준상태와 양자 보정을 결합하는 원리를 설명합니다. 두 상태 조작 예제, 물·질소의 샷 비교, 불리한 사례와 FCI 의존성을 검토하고 DFT·OLED 연구로의 확장 조건을 살펴봅니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(PublicAgent("Codex", "primary-source research, bilingual writing, mathematical illustration, copyediting, implementation and publication verification", "1차 출처 연구·한영 집필·수학 예제 구성·감수·구현·게시 검증"),),
        verification_scope=("CASH-QSE v1 full text, selected tables and appendices; primary predecessor papers and PySCF documentation", "metric definitions, sampling assumptions, computational platform, numerical counterexamples and classical baselines", "bilingual pages, source data, illustrative two-state eigenproblem, links and publication metadata"),
        verification_scope_ko=("CASH-QSE v1 본문·선별 표·부록, 선행 원문과 PySCF 공식 문서", "지표 정의·샷 가정·계산 플랫폼·불리한 사례·고전 기준선", "한영 페이지·표 데이터·설명용 두 상태 고유값 계산·링크·게시 정보"),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-10",
        human_review_level="topic and public publication requested; no separate line-by-line human review in this task",
        human_review_level_ko="주제 및 공개 게시 요청 확인. 이번 작업에서 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko="분자 벤치마크를 독립 재현하지 않았습니다. 조작 예제는 두 직교 상태의 설명용 모델이며, OLED 적용과 후속 연구 방향은 리뷰의 제안입니다.",
        disclosure_note_en="Molecular benchmarks were not independently reproduced. The interactive example is an educational two-state model; OLED applications and follow-up directions are editorial proposals.",
    ),
    PublicReview(
        folder="2026-09-09_quantum-resource-aware-workflows",
        title="양자 계산의 전체 비용을 설계하다",
        subtitle="오류정정 회로의 공간·시간, QML의 입력과 샷, 분자 계산의 기준 상태를 함께 읽기",
        date="2026-09-09",
        updated="2026-09-09",
        category="Quantum Computing",
        tags=("Resource Estimation", "Fermi-Hubbard", "QPE", "QCBM", "Quantum Machine Learning", "DS-NOCI", "IonQ", "D-Wave"),
        summary="Fermi–Hubbard 컴파일의 active volume, 실제 IonQ SAR 학습, 전력망 QML의 입력 병목과 DS-NOCI 기준 상태를 분석합니다. Superion 256과 Qubits Asia는 제작·행사 단계로 구분하고, 재료·OLED·최적화 연구에서 전체 비용을 비교하는 기준을 제안합니다.",
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(PublicAgent("Codex", "primary-source verification, bilingual writing, figure construction, copyediting, publication and live-page checks", "1차 출처 확인·한영 집필·도표 구성·감수·게시·공개 페이지 확인"),),
        verification_scope=(
            "four arXiv papers and official IonQ and D-Wave announcements available at the evidence cutoff",
            "dates, author attribution, metric definitions, comparison conditions and QPU/simulation/resource-estimate boundaries",
            "bilingual HTML, conceptual hero, original comparison diagrams, corrected Korean PDF, local links and publication metadata",
        ),
        verification_scope_ko=(
            "근거 기준일까지 공개된 arXiv 논문 4건과 IonQ·D-Wave 공식 안내",
            "날짜·저자 표기·지표 정의·비교 조건·QPU와 시뮬레이션 및 자원 추정의 경계",
            "한영 HTML·개념 이미지·비교 도표·교정한 한국어 PDF·파일 링크·게시 metadata",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-09",
        human_review_level="topic and public publication explicitly requested; no separate line-by-line human review in this publication task",
        human_review_level_ko="주제와 공개 게시 요청 확인. 이번 게시 작업에서 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko="논문 계산을 독립 재실행하지 않았습니다. 응용 제안과 연구 간 비교 기준은 리뷰의 해석이며, 연구 수치의 실제 계산 플랫폼과 검증 범위는 본문에 표시했습니다.",
        disclosure_note_en="The computations were not independently rerun. Application suggestions and cross-study evaluation criteria are editorial interpretation; execution settings and evidence limits are stated in the article.",
    ),
    PublicReview(
        folder="2026-09-06_agentic-programs-materials-science",
        title="계산을 맡기는 다음 단계: 재료과학 ‘에이전트 프로그램’은 무엇을 증명했나",
        subtitle="무질서 CIF를 검증 가능한 원자 모델로 바꾸는 DeMARS의 bounded judgment와 아직 남은 재현성 공백",
        date="2026-09-06",
        updated="2026-09-06",
        category="AI for Science",
        tags=("Agentic Programs", "Materials Science", "DeMARS", "Disordered Crystals", "CIF", "MLIP", "Scientific Software", "Verification"),
        summary=(
            "DeMARS가 무질서 결정의 부분 점유 CIF를 계산 가능한 원자 모델로 바꾸면서, LLM 판단을 결정론적 코드와 "
            "물리 검증 사이에 제한하는 방식을 분석합니다. 약 800개 성숙 사례와 100개 외부 테스트가 보여주는 진전, "
            "그리고 코드 비공개·인증/거절 분모 미공개가 남기는 검증 공백을 함께 짚습니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent(
                "Codex",
                "repository audit, primary-source research, candidate scoring, bilingual writing, figures, validation, publication, and live-site verification",
                "저장소 감사·1차 출처 조사·후보 평가·한영 집필·도해·검증·게시·공개 페이지 확인",
            ),
        ),
        verification_scope=(
            "arXiv primary paper, HTML full text, code-availability statement, and cited peer-reviewed context",
            "candidate scoring, prior-hub duplicate check, numerical and chemical-consistency checks, and evidence-boundary review",
            "bilingual HTML, 16:9 conceptual hero, reviewer-constructed SVGs, metadata, links, privacy, and deployed pages",
        ),
        verification_scope_ko=(
            "arXiv 원 논문·HTML 본문·코드 공개 문구와 인용 동료평가 자료",
            "후보 평가·기존 허브 중복 점검·수치와 화학식 일관성·주장 경계 검토",
            "한영 HTML·16:9 개념 대표 이미지·리뷰어 구성 SVG·metadata·링크·개인정보·배포 페이지",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-06",
        human_review_level="recurring scope and publication authority confirmed; no separate line-by-line human review in this run",
        human_review_level_ko="정기 리뷰 범위와 공개 게시 권한 확인. 이번 실행에서 별도 문장 단위 사람 검토는 수행되지 않음",
        disclosure_note_ko=(
            "약 800개 성숙 사례와 100개 외부 테스트는 저자 보고이며 DeMARS를 독립 실행하지 못했습니다. "
            "코드는 아직 공개되지 않았고 인증·거절 분모가 제시되지 않았다는 한계를 본문에 표시했습니다."
        ),
        disclosure_note_en=(
            "The roughly 800 maturation cases and 100 held-out tests are author-reported; DeMARS was not independently run. "
            "The review explicitly records that the code and certification/refusal denominator are unavailable."
        ),
    ),
    PublicReview(
        folder="2026-09-04_quantum-advantage-evidence-ledger",
        title="양자 우위의 경계는 계속 다시 그려진다",
        subtitle="D-Wave 고전 모사, 92큐비트 노이즈 학습, QML·단백질·oscillator–transmon을 하나의 자원 장부로 읽기",
        date="2026-09-04",
        updated="2026-09-04",
        category="Quantum Computing",
        tags=("Quantum Advantage", "D-Wave", "Error Mitigation", "QuanONet", "Quantum MeanFlow", "Protein VQE", "Bosonic QSP", "Resource Accounting"),
        summary=(
            "D-Wave annealing의 고전 t-VMC 재현, self-consistent Pauli noise와 PEC, QuanONet·Quantum MeanFlow, "
            "torsion-space 단백질 VQE, oscillator–transmon potential gate를 같은 증거 장부에 놓습니다. 관측량의 분모, "
            "실행 위치, 회로·shots, 고전 전후처리와 matched baseline을 함께 기록해야 양자 우위와 실용성을 구분할 수 있습니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex (main)", "orchestration, evidence integration, figures, copyediting, and publication", "총괄·근거 통합·도해·감수·게시"),
            PublicAgent("evidence_algorithms", "primary-source audit of t-VMC, Pauli-noise PEC, and QuanONet", "t-VMC·Pauli-noise PEC·QuanONet 1차 출처 감사"),
            PublicAgent("evidence_applications", "primary-source audit of QMF, protein VQE, and oscillator–transmon", "QMF·단백질 VQE·oscillator–transmon 1차 출처 감사"),
            PublicAgent("draft_sep4_review", "bilingual long-form draft", "한영 장문 초안"),
            PublicAgent("repo_publication_audit", "repository and publication-pipeline audit", "저장소·게시 파이프라인 감사"),
        ),
        verification_scope=(
            "six primary research records published or posted through the evidence cutoff",
            "publication status, observable denominator, execution layer, circuit and measurement cost, classical workload, and non-claims",
            "bilingual HTML, hero and quantitative figure, source ledger, PDF, metadata, privacy, links, and deployed pages",
        ),
        verification_scope_ko=(
            "근거 기준일까지 게재·게시된 1차 연구 6건",
            "게재 상태·관측량 분모·실행 계층·회로와 측정비용·고전 계산·미입증 범위",
            "한영 HTML·대표 이미지·정량 도식·근거 원장·PDF·metadata·개인정보·링크·배포 페이지",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-04",
        human_review_level="scope, synthesis direction, and public publication confirmed; line-by-line review not separately retained",
        human_review_level_ko="범위·통합 방향·공개 게시 요청 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko="수치는 원 논문의 분모와 실행 위치까지 재확인했습니다. 연구 간 공통 자원 장부와 개발 제안은 리뷰의 해석이며 원 논문의 공동 결론이 아닙니다.",
        disclosure_note_en="Reported numbers were rechecked with their denominators and execution settings. The cross-study resource ledger and development recommendations are editorial synthesis, not a joint conclusion of the source papers.",
    ),
    PublicReview(
        folder="2026-09-04_weekly-oled-inverse-design-excited-state-reliability",
        title="다중 여기상태를 매끄럽게 학습하는 법: OLED 분자 역설계의 물리 표현과 검증 경계",
        subtitle="2026년 8월 28일-9월 3일 연구 동향: latent Hamiltonian, QED-GW/BSE, 불확실성 기반 선택, 반응 흐름과 양자 기준선",
        date="2026-09-04",
        updated="2026-09-04",
        category="Materials AI",
        tags=("OLED", "Molecular Inverse Design", "Excited-State ML", "GW-BSE", "Active Learning", "Reaction Prediction", "Quantum Annealing", "VQE"),
        summary=(
            "LUSH가 여러 여기상태를 독립적인 scalar 대신 latent Hamiltonian의 고유값과 연산자로 학습하는 방식을 중심으로, "
            "QED-GW/BSE·AdaptNTK·reaction flow·계층형 생성 연구를 OLED 역설계 관점에서 검토합니다. 직접 OLED 논문이 없었던 "
            "주간이라는 한계와 D-Wave 고전 모사, warm-start QPU sampling의 실행 경계를 분리해 기록합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex", "primary-source screening, evidence integration, bilingual writing, figures, PDF, and publication", "1차 출처 선별·근거 통합·한영 집필·도해·PDF·게시"),
        ),
        verification_scope=(
            "eight newly posted or meaningfully revised preprints in the seven-day window",
            "publication dates, datasets, methods, quantitative findings, execution setting, and non-claims",
            "bilingual HTML, figures, PDF, metadata, links, and deployed pages",
        ),
        verification_scope_ko=(
            "7일 범위의 신규 또는 의미 있게 개정된 프리프린트 8편",
            "게시일·데이터셋·방법·정량 결과·실행 위치·미입증 범위",
            "한영 HTML·도해·PDF·metadata·링크·배포 페이지",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-04",
        human_review_level="recurring scope and publication direction confirmed; line-by-line review not separately retained",
        human_review_level_ko="정기 범위와 발행 방향 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko="이번 호는 단일 Codex 실행에서 작성·검증했습니다. 문헌의 수치와 실행 위치를 원문 결과로, OLED 적용안은 리뷰 제안으로 구분했습니다.",
        disclosure_note_en="This issue was written and checked in a single Codex run. Source-reported numbers and execution settings are separated from proposed OLED translations.",
    ),
    PublicReview(
        folder="2026-09-03_quantum-full-stack-codesign",
        title="큐비트 수를 넘어: 양자컴퓨팅은 시스템 경쟁으로 간다",
        subtitle="D-Wave 분자 생성과 광섬유 transmon 제어부터 IBM·QuEra·IonQ·오류정정 컴파일까지",
        date="2026-09-03",
        updated="2026-09-04",
        category="Quantum Computing",
        tags=("Full-Stack Co-Design", "D-Wave", "Transmon", "IBM Quantum", "QuEra", "IonQ", "Quantum Chemistry", "Fault-Tolerant Compilation"),
        summary=(
            "D-Wave 분자 생성과 광섬유 기반 transmon control을 출발점으로, IBM sampling·kernel 연구, "
            "QuEra·IonQ 응용 PoC, 측정비용과 오류정정 컴파일을 연결합니다. 큐비트 수보다 상태준비·측정·고전 후처리·"
            "논리 라우팅을 함께 최적화하는 full-stack co-design이 개발 방향을 좌우한다는 관점입니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex (main)", "evidence integration, bilingual writing, figures, and publication", "근거 통합·한영 집필·도해·게시"),
            PublicAgent("dwave_evidence", "D-Wave post and primary-source audit", "D-Wave 게시물·1차 출처 감사"),
            PublicAgent("transmon_evidence", "transmon post and primary-source audit", "transmon 게시물·1차 출처 감사"),
            PublicAgent("hub_structure", "review-hub structure and publication audit", "리뷰허브 구조·게시 감사"),
            PublicAgent("recover_sep3_package", "package recovery and public-file validation", "패키지 복구·공개 파일 검증"),
        ),
        verification_scope=(
            "the two forwarded public technical posts and their primary records",
            "the 2–3 September quantum briefs and cited primary papers",
            "execution setting, quantitative denominator, classical workload, non-claims, bilingual pages, and public-file privacy",
        ),
        verification_scope_ko=(
            "전달된 공개 기술 게시물 2건과 연결 1차 출처",
            "9월 2–3일 양자 브리프와 인용 1차 논문",
            "실행 위치·정량 분모·고전 계산·미입증 범위·한영 페이지·공개 파일 개인정보",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-03",
        human_review_level="scope, synthesis direction, and public publication confirmed; line-by-line review not separately retained",
        human_review_level_ko="범위·통합 방향·공개 게시 요청 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko="공개 게시물의 기술 주장만 원 출처와 대조해 사용했으며 비공개 메시지 metadata는 게시물에 포함하지 않았습니다.",
        disclosure_note_en="Only public technical claims were checked against primary sources; private message metadata is not included in the publication.",
    ),
    PublicReview(
        folder="2026-09-01_quantum-error-mitigation-net-benefit",
        title="오류완화는 언제 순이득을 내는가",
        subtitle="판독 반복부호와 IBM Heron 연구가 보여준 정확도·큐비트·샷 비용",
        date="2026-09-01",
        updated="2026-09-01",
        category="Quantum Computing",
        tags=(
            "Quantum Error Mitigation",
            "Measurement Error",
            "Zero-Noise Extrapolation",
            "Shot Allocation",
            "IBM Heron",
            "Photonic Circuits",
            "AI for Quantum",
            "Cavity Materials",
            "OLED",
        ),
        summary=(
            "판독 반복부호가 11배 물리 큐비트와 추가 CNOT으로 얻는 수치 예측, IBM Heron 연구의 실제 작은 회로 실행과 "
            "장치 보정값 기반 ZNE 수치실험을 분리해 읽습니다. 정확도와 함께 shots·추가 회로·2Q depth·postselection·"
            "wall-clock을 기록해야 하는 이유를 설명하고, 광자회로·에너지망·AI-for-quantum·cavity 재료 연구를 각각 평가합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex (main)", "evidence integration, narrative, figures, PDF correction, and publication", "근거 통합·서사·도해·PDF 수정·게시"),
            PublicAgent("verify_mitigation", "primary-source audit of readout mitigation and ZNE", "판독 오류완화·ZNE 1차 출처 감사"),
            PublicAgent("verify_adjacent", "primary-source audit of four adjacent research papers", "인접 연구 4건 1차 출처 감사"),
            PublicAgent("repo_pattern", "repository and publication-pipeline audit", "저장소·게시 파이프라인 감사"),
            PublicAgent("narrative_outline", "human-readable article structure", "독자 중심 글 구조 설계"),
            PublicAgent("pdf_audit", "brief PDF content and layout audit", "브리핑 PDF 내용·조판 감사"),
            PublicAgent("english_draft", "English translation draft", "영문 번역 초안"),
            PublicAgent("boundary_audit", "final bilingual claim-boundary review", "최종 한영 주장 경계 검토"),
        ),
        verification_scope=(
            "two error-mitigation papers and four adjacent primary research papers",
            "publication status, execution setting, circuit scale, quantitative claims, and non-claims",
            "corrected PDF, bilingual HTML and figures, metadata, and local-reference validation",
        ),
        verification_scope_ko=(
            "오류완화 논문 2건과 인접 1차 연구 논문 4건",
            "게재 상태·실행 위치·회로 규모·정량 수치·미입증 범위",
            "수정 PDF·한영 HTML·도해·metadata·로컬 참조 검증",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-09-01",
        human_review_level="topic, writing direction, and publication request confirmed; line-by-line review not separately retained",
        human_review_level_ko="주제·서술 방향·발행 요청 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko=(
            "정확한 모델 식별자는 세션 기록에 남지 않았습니다. 기재한 에이전트명과 역할은 이번 게시 작업에서 "
            "실제로 사용한 구성입니다."
        ),
        disclosure_note_en=(
            "The exact model identifier was not retained in the session record. The listed agent names and roles are the "
            "configuration actually used for this publication."
        ),
    ),
    PublicReview(
        folder="2026-08-31_thermal-quantum-states-exciton-validation",
        title="뜨거운 양자상태를 만들고, 엑시톤을 따라간다",
        subtitle="유한온도 상태는 어떻게 만들고, 양자 시뮬레이터와 OLED 계산은 무엇으로 믿을 수 있는가",
        date="2026-08-31",
        updated="2026-08-31",
        category="Quantum Computing",
        tags=(
            "Thermal State Preparation",
            "Analog Quantum Simulation",
            "Exciton Wavefunction",
            "OLED",
            "Quantum Control",
            "Quantum Hardware",
            "Quantum Optimization",
            "Fourier LCU",
        ),
        summary=(
            "유한온도 Gibbs 상태를 준비하는 방법, 2D XY 시뮬레이터와 고전 계산이 같은 확산계수를 내는지, "
            "α-sexithiophene의 엑시톤이 400 fs 동안 어떻게 수축하는지 설명합니다. 이어서 하드웨어·펄스 설계와 "
            "Fourier-LCU가 회로 연결, 측정 횟수와 고전 집계 비용을 어떻게 맞바꾸는지 살펴봅니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex (main)", "evidence integration, narrative, figures, and publication", "근거 통합·서사·도해·게시"),
            PublicAgent("source_verify", "primary-source and quantitative-claim verification", "1차 출처·정량 주장 검증"),
            PublicAgent("repo_pattern", "repository and publication-pipeline audit", "저장소·게시 파이프라인 감사"),
            PublicAgent("hero_image", "scientific editorial hero generation", "과학 편집형 대표 이미지 생성"),
            PublicAgent("english_draft", "English translation draft", "영문 번역 초안"),
            PublicAgent("boundary_audit", "final bilingual claim-boundary and publication audit", "최종 한영 주장 경계·게시 감사"),
            PublicAgent("post_research", "LinkedIn and Fourier-LCU primary-source verification", "LinkedIn·Fourier-LCU 1차 출처 검증"),
            PublicAgent("repo_audit", "revision scope and publication-file audit", "수정 범위·게시 파일 감사"),
        ),
        verification_scope=(
            "five APS peer-reviewed papers, one IBM Research preprint, and author posts",
            "publication dates, execution locations, quantitative claims, and non-claims",
            "bilingual HTML, figures, PDF, metadata, and local-reference validation",
        ),
        verification_scope_ko=(
            "APS 동료평가 논문 5건, IBM Research 프리프린트 1건과 저자 게시물",
            "게재일·실행 위치·정량 수치·미입증 범위",
            "한영 HTML·도해·PDF·metadata·로컬 참조 검증",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-08-31",
        human_review_level="topic, framing, and publication request confirmed; line-by-line review not separately retained",
        human_review_level_ko="주제·서술 방향·발행 요청 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko=(
            "정확한 모델 식별자는 세션 기록에 남지 않았습니다. 기재한 에이전트명과 역할은 이번 게시 작업에서 "
            "실제로 사용한 구성입니다."
        ),
        disclosure_note_en=(
            "The exact model identifier was not retained in the session record. The listed agent names and roles are the "
            "configuration actually used for this publication."
        ),
    ),
    PublicReview(
        folder="2026-08-30_practical-quantum-computing-stack",
        title="양자컴퓨터가 계산 시스템이 되기까지",
        subtitle="최신 고전 기준선에서 회로 구현·판독·오류정정·제조 기반까지, 실용성을 가르는 다섯 검증 단계",
        date="2026-08-30",
        updated="2026-08-30",
        category="Quantum Computing",
        tags=(
            "Practical Quantum Computing",
            "Kohn-Sham FNO",
            "Quantum Circuit Synthesis",
            "Quantum Readout",
            "Fault Tolerance",
            "Quantum Manufacturing",
            "OLED",
        ),
        summary=(
            "양자컴퓨터의 실용성을 최신 고전 기준선, 회로 구현, 판독, 오류정정 메모리, 제조·배치의 "
            "다섯 검증 단계로 읽습니다. KS-FNO, Classiq challenge, PTSET, FTQC 하한과 Xanadu·Pasqal "
            "소식을 서로 다른 증거 층에 놓고, OLED·재료 PoC에 제한된 양자 커널을 배치하는 기준을 제시합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode with AI Tech Review Editorial Harness v2026.08",
        ai_system_ko="OpenAI Codex Work Mode 및 AI Tech Review Editorial Harness v2026.08",
        agents=(
            PublicAgent("Codex (main)", "orchestration, evidence integration, and publication", "총괄·근거 통합·게시"),
            PublicAgent("repo_audit", "repository and publication-pipeline audit", "저장소·게시 파이프라인 감사"),
            PublicAgent("source_verify", "primary-source and quantitative-claim verification", "1차 출처·정량 주장 검증"),
            PublicAgent("editorial", "bilingual narrative and figure specification", "한영 서사·도해 명세"),
            PublicAgent("boundary_review", "independent evidence-boundary review", "독립 증거 경계 검토"),
            PublicAgent("translation_audit", "English fidelity and terminology audit", "영문 충실도·용어 감사"),
            PublicAgent("public_audit", "public-site and accessibility audit", "공개 사이트·접근성 감사"),
            PublicAgent("deploy_qa", "local and deployed-page verification", "로컬·배포 페이지 검증"),
        ),
        verification_scope=(
            "official challenge specification",
            "three arXiv v1 preprints and full text",
            "Government of Canada release, Pasqal release, and SEC filing",
            "bilingual HTML, figures, PDF, metadata, links, and responsive rendering",
        ),
        verification_scope_ko=(
            "공식 challenge 사양",
            "arXiv v1 프리프린트 3건과 원문",
            "캐나다 정부·Pasqal 발표와 SEC 공시",
            "한영 HTML·도해·PDF·metadata·링크·반응형 렌더링",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-08-30",
        human_review_level="topic, framing, and publication request confirmed; line-by-line review not separately retained",
        human_review_level_ko="주제·서술 방향·발행 요청 확인. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko=(
            "모델의 정확한 식별자는 세션 기록에 남지 않았습니다. 기재된 에이전트명과 역할은 이번 게시 작업에서 "
            "실제로 사용한 멀티에이전트 구성입니다."
        ),
        disclosure_note_en=(
            "The exact model identifier was not retained in the session record. The listed agent names and roles are the "
            "multi-agent configuration actually used for this publication."
        ),
    ),
    PublicReview(
        folder="2026-08-29_quantum-simulation-vibronic-dynamics",
        title="정적 에너지에서 광여기 동역학으로: PennyLane 진동-전자 양자 시뮬레이션의 원리와 연구 전망",
        subtitle="KDC 해밀토니안을 격자 큐비트로 옮기는 방법, 23-wire 고전 시뮬레이션의 계산 경계, TADF·OLED 연구로 확장하기 위한 조건",
        date="2026-08-29",
        updated="2026-08-29",
        category="Quantum Computing",
        tags=("Vibronic Dynamics", "Nonadiabatic Dynamics", "Quantum Simulation", "PennyLane", "Quantum Chemistry", "OLED"),
        summary=(
            "PennyLane 데모가 KDC 진동-전자 해밀토니안을 실공간 격자, QROM, 가역 산술과 2차 Trotter 전개로 "
            "옮기는 방법을 해설합니다. 23-wire CPU 상태벡터 toy simulation과 실제 QPU·분자 계산의 경계를 구분하고, "
            "TADF·OLED의 spin-vibronic 동역학으로 확장하기 위한 검증 단계를 제시합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="OpenAI Codex Work Mode",
        ai_system_ko="OpenAI Codex Work Mode",
        agents=(
            PublicAgent("Codex", "orchestration and editorial integration", "총괄 편집·통합"),
            PublicAgent("Volta", "LinkedIn post and primary-paper research", "LinkedIn 게시물·연결 논문 조사"),
            PublicAgent("Feynman", "disclosure and authoring-standard design", "공개·하네스 기준 설계"),
            PublicAgent("Carson", "repository audit and publication QA", "저장소 감사·게시 QA"),
            PublicAgent("Kierkegaard", "independent final diff review", "독립 최종 차분 검토"),
        ),
        verification_scope=(
            "PennyLane demo and fixed-commit source",
            "peer-reviewed paper and current arXiv version",
            "official documentation",
            "equation, table, link, metadata, and final-HTML rendering",
        ),
        verification_scope_ko=(
            "PennyLane 데모와 고정 commit 코드",
            "동료평가 논문과 최신 arXiv 버전",
            "공식 문서",
            "수식·표·링크·metadata·최종 HTML",
        ),
        primary_sources_checked=True,
        evidence_cutoff="2026-08-29",
        human_review_level="scope, direction, and publication request confirmed; line-by-line review not separately retained",
        human_review_level_ko="범위·방향 확인 및 발행 요청. 문장 단위 검토 여부는 별도 기록되지 않음",
        disclosure_note_ko=(
            "원 리뷰 작성 세션의 전체 에이전트 roster는 보존되지 않았습니다. "
            "기재한 역할은 2026-08-29 공개 보완과 방법 업데이트에서 확인 가능한 역할입니다."
        ),
        disclosure_note_en=(
            "The original article session did not retain a complete agent roster. "
            "The listed roles are the verifiable roles used for the 2026-08-29 public repair and methods update."
        ),
    ),
    PublicReview(
        folder="2026-08-28_weekly-oled-inverse-design-mechanism-aware-labels",
        title="OLED 분자 역설계를 위한 기작 중심 물성 라벨: 이성질체 ISC에서 확장형 DFT·ML까지",
        subtitle="2026년 8월 21–27일 연구 동향: 위치 이성질체의 ISC 기작, 분자간 상호작용, SCF 가속과 양자 계산의 검증 수준",
        date="2026-08-28",
        updated="2026-08-28",
        category="Materials AI",
        tags=("OLED", "TADF", "Molecular Inverse Design", "Spin-Vibronic Coupling", "DFT/ML", "VQE"),
        summary=(
            "이번 주 OLED 광물리 논문은 위치 이성질체별 ISC 속도를 direct SOC, Herzberg-Teller, "
            "spin-vibronic 기여로 분해했습니다. 이를 바탕으로 ΔEST 중심 데이터셋을 state character, "
            "higher triplet, SOC와 promoting mode까지 포함하는 물성 라벨로 확장할 필요성을 검토하고, "
            "DensIP·Kohn-Sham neural operator·closed-loop AI와 VQE 구성요소의 적용 범위를 정리합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
        primary_sources_checked=True,
    ),
    PublicReview(
        folder="2026-08-27_classiq-ashn-circuit-compression",
        title="양자 회로 최적화는 왜 필요한가: Classiq와 AshN을 대표 사례로",
        subtitle="고수준 기능 합성, automatic control skips, native gate·SWAP absorption이 회로 비용을 줄이는 서로 다른 층을 비교합니다",
        date="2026-08-27",
        updated="2026-08-27",
        category="Quantum Computing",
        tags=("Quantum Compilation", "Classiq", "Qmod", "AshN", "Native Gates", "Circuit Depth"),
        summary=(
            "Classiq은 기능 모델에서 함수 구현·ancilla·control pattern을 고르고, AshN은 실제 초전도 QPU의 "
            "native two-qubit gate로 논리 연산과 routing SWAP을 흡수합니다. CX count, mapped depth와 "
            "QPU fidelity를 분리해 두 접근의 공통 원리, 정량 결과, 결합 가능성과 미입증 범위를 검토합니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
        primary_sources_checked=True,
    ),
    PublicReview(
        folder="2026-08-27_dwave-molecular-inverse-design-benchmark",
        title="D-Wave 분자 역설계 실험: QPU가 고른 후보를 DFT까지 확인해 보니",
        subtitle="QM9 5,000개에서 ML·분자 생성·QUBO 선택·QPU 실행·PySCF 검증까지 연결한 계산 스냅샷",
        date="2026-08-27",
        updated="2026-08-27",
        category="Materials AI",
        tags=("Molecular Inverse Design", "D-Wave", "QUBO", "Chemprop", "PySCF", "Active Learning"),
        summary=(
            "Chemprop D-MPNN과 ExtraTrees/Morgan 예측, 세 가지 고전 분자 생성기, 18변수 BQM을 "
            "거쳐 후보 3개를 선택했습니다. D-Wave QPU 결과를 exact 기준과 비교하고 PySCF DFT로 "
            "6개 후보를 재검증했으며, 고정 후보군 replay와 실제 active-learning loop의 증거 경계를 구분합니다."
        ),
        translations=(PublicTranslation(language="en", subdir="en", label="English"),),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
        primary_sources_checked=True,
    ),
    PublicReview(
        folder="2026-08-26_quantum-computing-layers",
        title="재료 계산에서 QRAM까지: 양자 연구를 계산 계층으로 읽는 법",
        subtitle="SiC 색 중심 DFT, 실제 QPU 라우터, 페르미온 회로 컴파일과 QML 시뮬레이션을 같은 기준표 위에서 구분합니다",
        date="2026-08-26",
        updated="2026-08-26",
        category="Quantum Computing",
        tags=("Quantum Computing", "Materials Science", "QRAM", "Qiskit Fermions", "VQE", "QML"),
        summary=(
            "8월 25일 공개된 QRAM router는 실제 초전도 QPU 실험입니다. SiC color-center 연구는 "
            "고전 HSE06/DFT, Qiskit Fermions의 depth 12는 컴파일 결과이며, PAS와 QRC+PIC는 "
            "시뮬레이션입니다. 서로 다른 증거 층을 분리해 성취와 남은 비용을 평가합니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-08-24_oti-iqcc-oled-quantum-emulation",
        title="200 논리 큐비트 OLED 계산, 양자컴퓨터였나?",
        subtitle="OTI Lumionics·SAIT의 JACS iQCC 연구가 입증한 것과 실제 QPU가 아직 입증하지 못한 것을 구분합니다",
        date="2026-08-24",
        updated="2026-08-24",
        category="Materials AI",
        tags=("Quantum Chemistry", "OLED", "iQCC", "Classical Emulation", "Ir/Pt Phosphors"),
        summary=(
            "OTI Lumionics와 SAIT는 양자-native iQCC를 고전 CPU에서 약 200 logical-qubit 규모로 "
            "에뮬레이션해 Ir(III)·Pt(II) 인광체의 T1−S0 갭을 계산했습니다. 실제 QPU 실행이나 "
            "양자 우위가 아니라 미래 하드웨어가 넘어야 할 정확도·규모·고전 tractability 기준선입니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-06-11_QC-based-inverse-design",
        title="양자컴퓨팅은 재료 역설계의 어디를 바꿀 수 있는가",
        subtitle="전자구조 계산부터 물성 학습, 후보 생성, 조합 최적화까지 재료정보학 파이프라인의 양자 삽입점을 점검합니다",
        date="2026-07-11",
        updated="2026-07-12",
        category="Materials AI",
        tags=("Materials Informatics", "Quantum-Classical", "Inverse Design", "Quantum Chemistry", "QML"),
        summary=(
            "재료 역설계를 전자구조·학습·생성·표본추출·최적화의 선택 가능한 전문 계산 모듈로 나눕니다. "
            "QPE·VQE, QML, QCBM·QBM, QUBO를 푸는 QA·QAOA의 역할과 성숙도를 구분하고, "
            "QAE는 장기 확장 모듈로 둡니다. 청색 OLED는 이 구조를 점검하는 첫 유즈케이스입니다."
        ),
    ),
    PublicReview(
        folder="2026-06-17_ai-processor-stack-npu-tpu-gpu-lpu",
        title="AI 처리장치 스택: CPU, GPU, TPU, NPU, LPU는 왜 나뉘는가",
        subtitle="병렬성, 데이터 이동, 지연시간, 전력, 소프트웨어 스택으로 AI 칩의 역할을 다시 읽습니다",
        date="2026-06-17",
        updated="2026-06-17",
        category="AI Hardware",
        tags=("AI Hardware", "AI Accelerators", "GPU/TPU", "NPU/LPU"),
        summary=(
            "NPU, LPU, TPU, GPU, CPU, DPU/IPU, QPU를 새 약어 경쟁이 아니라 workload와 "
            "데이터 경로의 분화로 읽습니다. 메모리 이동, 정밀도, 지연시간, 인프라 오프로드가 "
            "왜 별도 처리장치를 낳는지 정리합니다."
        ),
    ),
    PublicReview(
        folder="2026-06-05_neuromorphic-edge-ai",
        title="뉴로모픽, 항상 켜진 AI의 감각층",
        subtitle="스마트홈·오디오·웨어러블 센서에서 보는 저전력 edge intelligence",
        date="2026-06-05",
        updated="2026-06-23",
        category="AI Hardware",
        tags=("Neuromorphic AI", "Edge AI", "Always-on AI", "AIoT"),
        summary=(
            "ScienceTimes가 소개한 MoS2 인-센서 뉴로모픽 비전 논문을 출발점으로, "
            "뉴로모픽이 스마트홈 presence sensing, 오디오 wake/event detection, 웨어러블, "
            "smart camera 같은 항상 켜진 생활형 edge AI에서 어떤 의미를 갖는지 점검합니다."
        ),
        ai_system="Codex Agent",
        ai_system_ko="Codex Agent",
    ),
    PublicReview(
        folder="2026-05-30_shadow-ai-work-boundary-reconfiguration",
        title="AI Native 시대의 일하는 방식: Shadow AI와 우리",
        subtitle="DX를 이룬 조직에서도 AX가 native하게 흐르지 못할 때, 숨은 AI 활용과 번아웃이 어떻게 생기는지 살펴봅니다",
        date="2026-05-31",
        updated="2026-05-31",
        category="AI Governance",
        tags=("Shadow AI", "AI Governance", "AX", "AI Burnout"),
        summary=(
            "외부 AI 도구의 속도, 회사 내부 silo, 승인·검증 경로의 지연이 만날 때 Shadow AI는 "
            "개인의 일탈이 아니라 조직이 아직 흡수하지 못한 전환 비용으로 나타납니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-05-30_quantum-informed-ai-chaotic-processes",
        title="혼돈계 예측에 양자 prior를 더하면 무엇이 달라질까",
        subtitle="난류와 같은 chaotic process에서 장기 통계를 유지하는 예측을 위해 QIML이 제안한 양자 prior 접근을 살펴봅니다",
        date="2026-05-30",
        updated="2026-05-30",
        category="Quantum AI",
        tags=("Quantum AI", "Scientific ML", "Chaotic Systems", "QIML"),
        summary=(
            "Lev Selector의 AI Updates Weekly에서 포착한 QIML 연구를 출발점으로, 양자 생성 모델이 "
            "혼돈계의 불변 통계를 prior로 압축하고 고전 예측기의 긴 rollout을 안정화할 수 있는지 검토합니다."
        ),
    ),
    PublicReview(
        folder="2026-05-23_ai-scientist-execution-harness",
        title="AI 과학자, 시작의 끝에서",
        subtitle="에르되시 문제 #1196에서 연구 실행 하네스까지, 우리가 이미 기대기 시작한 AI 과학자를 어떻게 준비할 것인가",
        date="2026-05-23",
        updated="2026-05-25",
        category="AI for Science",
        tags=("AI for Science", "AI Scientist", "AI Co-Scientist", "Research Harness"),
        summary=(
            "에르되시 문제 #1196에서 출발해 AI 과학자가 연구의 속도를 높이는 장면과, 그 속도를 "
            "검증 가능한 작업으로 바꾸기 위해 필요한 연구 실행 하네스를 함께 살펴봅니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-05-07_tabpfn-oled-manufacturing-foundation-model",
        title="TabPFN: Foundation model for Tabular inference",
        subtitle="OLED 분자 계산, 공정, SCM, 검사 데이터에서 표 기반 Foundation 모델을 어떻게 읽을 것인가",
        date="2026-05-17",
        updated="2026-05-21",
        category="Materials AI",
        tags=("TabPFN", "OLED", "Materials Informatics", "Data Provenance"),
        summary=(
            "작은 표 데이터에서 빠른 기준 모델을 세우는 TabPFN의 장점과, OLED 연구·제조 데이터에 "
            "적용할 때 함께 보아야 할 계산 조건과 실험 provenance를 살펴봅니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-05-09_ai-updates-weekly",
        title="AI 에이전트를 일하게 하는 기술: 하네스 엔지니어링",
        subtitle="도구 호출, 권한, 기억, 검증, 병합이 에이전트 운영의 기본 조건이 되는 이유",
        date="2026-05-09",
        updated="2026-05-13",
        category="Agent Systems",
        tags=("AI Agents", "Harness Engineering", "Developer Tools", "Governance"),
        summary=(
            "모델 성능만으로는 설명하기 어려운 에이전트 운영 문제를 권한, 메모리, 검증, 승인, "
            "병합의 관점에서 따라갑니다."
        ),
        ai_system="Codex-based GPT-5-family agent harness",
        ai_system_ko="Codex 기반 GPT-5 계열 에이전트 하네스",
    ),
    PublicReview(
        folder="2026-05-06_gpt-5-5-family-post-release-evaluation",
        title="GPT-5.5 기술동향 리포트: 긴 작업 수행 능력과 안전한 활용 조건",
        subtitle="긴 작업 수행 능력, Hallucination 평가, Claude Opus 4.7 비교, 안전한 활용 조건",
        date="2026-05-10",
        updated="2026-05-10",
        category="Frontier Models",
        tags=("GPT-5.5", "Claude Opus", "Agentic AI", "Trust and Safety"),
        summary=(
            "GPT-5.5 계열 모델의 장시간 작업 수행 능력과 외부 평가를 함께 보며, 실제 업무에 "
            "맡길 수 있는 일의 조건을 점검합니다."
        ),
        ai_system="Codex Agent",
        ai_system_ko="Codex Agent",
    ),
)


LOCAL_REF_RE = re.compile(
    r"(?P<prefix>\b(?:src|href|poster)=['\"])(?P<url>[^'\"]+)(?P<suffix>['\"])",
    re.IGNORECASE,
)
LOCAL_HREF_RE = re.compile(r"\s+href=(?P<quote>['\"])(?P<url>[^'\"]+)(?P=quote)", re.IGNORECASE)
INTERNAL_PATH_RE = re.compile(
    r"(?:"
    r"file:///[A-Za-z]:[\\/][^<>'\"\s]+"
    r"|(?<![A-Za-z0-9])[A-Za-z]:[\\/][^<>'\"\s]+"
    r"|(?<![A-Za-z0-9._<:-])/(?:workspace|home|Users|tmp|var|etc|opt|srv|mnt|root|private)"
    r"(?![A-Za-z0-9._-])"
    r"(?:/[^<>'\"`\s)\]}]*)?"
    r")"
)
PUBLIC_REVIEW_FILE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".css",
    ".js",
    ".ico",
    ".pdf",
}
PUBLIC_TEXT_FILE_SUFFIXES = {".svg", ".css", ".js", ".md", ".txt", ".vtt", ".json", ".csv", ".py", ".html"}
# Publication approval is for this article and these final filenames only.
# Keep MP4/VTT/TXT out of the general extension allowlist.
NOETHER_VIDEO_FOLDER = "2026-10-17_noether-symmetry-conservation"
NOETHER_VIDEO_ASSETS = {
    language: {
        "video": f"noether-abstract-{language}.mp4",
        "poster": f"noether-abstract-poster-{language}.webp",
        "captions": f"noether-abstract-{language}.vtt",
        "transcript": f"noether-abstract-transcript-{language}.txt",
    }
    for language in ("ko", "en")
}
PUBLIC_LOCAL_NOTE_RE = re.compile(
    r"\s*<section\b(?=[^>]*\bid=['\"]public-local-references['\"])[^>]*>.*?</section>\s*",
    re.IGNORECASE | re.DOTALL,
)
HTML_LIST_ITEM_RE = re.compile(r"<li\b[^>]*>.*?</li>", re.IGNORECASE | re.DOTALL)
HTML_ANCHOR_RE = re.compile(r"<a\b[^>]*>.*?</a>", re.IGNORECASE | re.DOTALL)
PRIVATE_MESSAGE_METADATA_RE = re.compile(
    r"(?:"
    r"(?:\bGmail\b|\be-?mail\b|\bmail\b|메일|이메일)"
    r".{0,400}?"
    r"(?:\bsubject\b|\btimestamp\b|message-id|\bsent at\b|\breceived at\b|제목|시각|발신|수신)"
    r"|"
    r"(?:\bsubject\b|\btimestamp\b|message-id|\bsent at\b|\breceived at\b|제목|시각|발신|수신)"
    r".{0,400}?"
    r"(?:\bGmail\b|\be-?mail\b|\bmail\b|메일|이메일)"
    r")",
    re.IGNORECASE | re.DOTALL,
)
PRIVATE_URL_RE = re.compile(r"\b(?:https?|ssh|file)://[^\s<>\"']+", re.IGNORECASE)
PRIVATE_IP_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in (
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    )
)
KNOWN_CREDENTIAL_RE = re.compile(
    r"(?:"
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"
    r"|\bgithub_pat_[A-Za-z0-9_]{30,}\b"
    r"|\bgh[pousr]_[A-Za-z0-9]{30,}\b"
    r"|\bsk-proj-[A-Za-z0-9_-]{32,}\b"
    r"|\bsk-[A-Za-z0-9]{32,}\b"
    r"|\bxox[baprs]-[A-Za-z0-9-]{20,}\b"
    r"|\bAIza[0-9A-Za-z_-]{35}\b"
    r")"
)
AUTHORIZATION_CREDENTIAL_RE = re.compile(
    r"(?P<prefix>\bAuthorization\s*[:=]\s*(?:Bearer|Basic)\s+)[A-Za-z0-9._~+/=-]{16,}",
    re.IGNORECASE,
)
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?P<prefix>['\"]?\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|token|"
    r"client[_-]?secret|secret[_-]?key|password|passwd|x-amz-signature|"
    r"x-goog-signature)['\"]?\s*[:=]\s*)"
    r"(?P<quote>['\"]?)(?P<value>[^\s,&'\"]{12,})(?P=quote)",
    re.IGNORECASE,
)
PRIVATE_KEY_BLOCK_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
SMARTY_ENTITY = r"&(?:[rl]squo|[rl]dquo|#821[67]|#x201[89]);"
SMARTY_ENTITY_IN_MATH_RE = re.compile(
    rf"(?:"
    rf"\$\$(?:(?!\$\$).)*?{SMARTY_ENTITY}(?:(?!\$\$).)*?\$\$"
    rf"|(?<!\$)\$(?!\$)[^$\n]*?{SMARTY_ENTITY}[^$\n]*?\$(?!\$)"
    rf"|\\\((?:(?!\\\)).)*?{SMARTY_ENTITY}(?:(?!\\\)).)*?\\\)"
    rf"|\\\[(?:(?!\\\]).)*?{SMARTY_ENTITY}(?:(?!\\\]).)*?\\\]"
    rf")",
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_STYLE_BLOCK_RE = re.compile(
    r"<(?:script|style)\b[^>]*>.*?</(?:script|style)\s*>",
    re.IGNORECASE | re.DOTALL,
)
CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV = "CLOUDFLARE_WEB_ANALYTICS_TOKEN"
PUBLIC_METRICS_ENDPOINT_ENV = "INFANT83_PUBLIC_METRICS_ENDPOINT"
LEGACY_PUBLIC_METRICS_ENDPOINT_ENV = "AI_TECH_REVIEW_PUBLIC_METRICS_ENDPOINT"
DEFAULT_PUBLIC_METRICS_ENDPOINT = ""
PUBLIC_BASE_PATH = "/AI_Tech_Review/"
PUBLIC_BASE_URL = "https://infant83.github.io/AI_Tech_Review/"
PUBLIC_SITE_ID = "ai-tech-review"
CLOUDFLARE_WEB_ANALYTICS_RE = re.compile(
    r"\s*<!-- Cloudflare Web Analytics -->.*?<!-- End Cloudflare Web Analytics -->\s*",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_METRICS_HEAD_RE = re.compile(
    r"\s*<!-- AI Tech Review Public Metrics Styles -->.*?<!-- End AI Tech Review Public Metrics Styles -->\s*",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_METRICS_SCRIPT_RE = re.compile(
    r"\s*<!-- AI Tech Review Public Metrics -->.*?<!-- End AI Tech Review Public Metrics -->\s*",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_ICON_RE = re.compile(
    r"\s*<!-- AI Tech Review Icons -->.*?<!-- End AI Tech Review Icons -->\s*",
    re.IGNORECASE | re.DOTALL,
)
AUTHORING_DISCLOSURE_BLOCK_RE = re.compile(
    r"\s*<!-- AI Tech Review Authoring Disclosure -->.*?"
    r"<!-- End AI Tech Review Authoring Disclosure -->\s*",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_METRICS_CSS_LINK_RE = re.compile(
    r"\s*<link\b(?=[^>]*\bhref=['\"][^'\"]*assets/public-metrics\.css(?:\?[^'\"]*)?['\"])[^>]*>",
    re.IGNORECASE,
)
PUBLIC_METRICS_JS_RE = re.compile(
    r"\s*<script\b(?=[^>]*\bsrc=['\"][^'\"]*assets/public-metrics\.js(?:\?[^'\"]*)?['\"])[^>]*>\s*</script>",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_METRICS_CONFIG_RE = re.compile(
    r"\s*<script\b[^>]*>\s*window\.AI_TECH_REVIEW_METRICS\s*=.*?</script>",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_ICON_LINK_RE = re.compile(
    r"\s*<link\b(?=[^>]*\bhref=['\"](?:data:,|[^'\"]*(?:favicon\.ico|(?:federlicht-favicon|ai-tech-review-icon)\.svg|apple-touch-icon\.png)(?:\?[^'\"]*)?)['\"])[^>]*>",
    re.IGNORECASE,
)
CANONICAL_LINK_RE = re.compile(
    r"\s*<link\b(?=[^>]*\brel=['\"][^'\"]*\bcanonical\b[^'\"]*['\"])[^>]*>",
    re.IGNORECASE,
)
OG_TITLE_RE = re.compile(
    r"\s*<meta\b(?=[^>]*\bproperty=['\"]og:title['\"])[^>]*>",
    re.IGNORECASE,
)


class FirstImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.first_image: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.first_image or tag.lower() != "img":
            return
        attr_map = {name.lower(): value for name, value in attrs}
        src = attr_map.get("src")
        if src:
            self.first_image = src


class VideoEmbedParser(HTMLParser):
    """Collect native-video attributes, independently of surrounding prose."""

    def __init__(self) -> None:
        super().__init__()
        self.videos: list[dict[str, object]] = []
        self.hrefs: list[str] = []
        self.current: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {name.lower(): value or "" for name, value in attrs}
        if tag == "video":
            if self.current is not None:
                raise ValueError("Nested video elements are not supported")
            self.current = {"attrs": values, "sources": [], "tracks": []}
            self.videos.append(self.current)
        elif self.current is not None and tag in {"source", "track"}:
            self.current["sources" if tag == "source" else "tracks"].append(values)
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "video":
            self.current = None


class PageMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.canonical_urls: list[str] = []
        self.alternates: dict[str, str] = {}
        self.language_links: dict[str, str] = {}
        self.current_languages: set[str] = set()
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.og_title = ""
        self.has_hub_link = False
        self.has_authoring_disclosure = False
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self._capture = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "html":
            self.html_lang = values.get("lang", "").strip().lower()
            return
        if tag.lower() in {"title", "h1"}:
            self._capture = tag.lower()
        if tag.lower() == "meta" and values.get("property", "").lower() == "og:title":
            self.og_title = values.get("content", "").strip()
        classes = {part for part in values.get("class", "").split() if part}
        if values.get("id"):
            self.ids.add(values["id"].strip())
        if "authoring-disclosure" in classes:
            self.has_authoring_disclosure = True
        if tag.lower() == "a" and values.get("href"):
            self.hrefs.append(values["href"].strip())
        if tag.lower() == "a" and values.get("href", "").rstrip("/") == PUBLIC_BASE_URL.rstrip("/"):
            self.has_hub_link = True
        if values.get("aria-current", "").lower() == "page" and values.get("lang"):
            self.current_languages.add(values["lang"].strip().lower())
        if tag.lower() == "a" and values.get("hreflang") and values.get("href"):
            self.language_links[values["hreflang"].strip().lower()] = values["href"].strip()
        if tag.lower() != "link":
            return

        rel_values = {part.lower() for part in values.get("rel", "").split()}
        href = values.get("href", "").strip()
        if "canonical" in rel_values and href:
            self.canonical_urls.append(href)
        if "alternate" in rel_values and href and values.get("hreflang"):
            self.alternates[values["hreflang"].strip().lower()] = href

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == self._capture:
            self._capture = ""

    def handle_data(self, data: str) -> None:
        if self._capture == "title":
            self.title_parts.append(data)
        elif self._capture == "h1":
            self.h1_parts.append(data)

    @property
    def title_text(self) -> str:
        return " ".join(" ".join(self.title_parts).split())

    @property
    def h1_text(self) -> str:
        return " ".join(" ".join(self.h1_parts).split())


class DisclosureMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fields: dict[str, str] = {}
        self.field_links: dict[str, list[str]] = {}
        self._section_depth = 0
        self._capture = ""
        self._parts: list[str] = []
        self._current_term = ""
        self._current_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {name.lower(): value or "" for name, value in attrs}
        if tag == "section":
            if self._section_depth:
                self._section_depth += 1
            elif "authoring-disclosure" in values.get("class", "").split():
                self._section_depth = 1
            return
        if not self._section_depth:
            return
        if tag in {"dt", "dd"}:
            self._capture = tag
            self._parts = []
            if tag == "dd":
                self._current_links = []
        elif tag == "a" and self._capture == "dd" and values.get("href"):
            self._current_links.append(values["href"].strip())

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._section_depth and tag == self._capture:
            value = " ".join(" ".join(self._parts).split())
            if tag == "dt":
                self._current_term = value
            elif self._current_term:
                self.fields[self._current_term] = value
                self.field_links[self._current_term] = list(self._current_links)
            self._capture = ""
            self._parts = []
        if tag == "section" and self._section_depth:
            self._section_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._section_depth and self._capture:
            self._parts.append(data)


def is_external_or_anchor(url: str) -> bool:
    stripped = url.strip()
    if not stripped or stripped.startswith("#"):
        return True
    parts = urlsplit(stripped)
    return bool(parts.scheme or parts.netloc) or stripped.startswith(("data:", "mailto:", "tel:", "javascript:"))


def split_local_url(url: str) -> tuple[str, str, str]:
    parts = urlsplit(html.unescape(url))
    return unquote(parts.path), parts.query, parts.fragment


def rebuild_local_url(filename: str, query: str, fragment: str) -> str:
    rebuilt = filename
    if query:
        rebuilt += f"?{query}"
    if fragment:
        rebuilt += f"#{fragment}"
    return rebuilt


def approved_video_assets(review: PublicReview | None, language: str) -> dict[str, str]:
    if review is None or review.folder != NOETHER_VIDEO_FOLDER:
        return {}
    return NOETHER_VIDEO_ASSETS.get(language, {})


def unpublished_local_text_reference(fragment: str, approved_names: Iterable[str] = ()) -> bool:
    approved_names = set(approved_names)
    for match in LOCAL_HREF_RE.finditer(fragment):
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            continue
        local_path = split_local_url(raw_url)[0]
        if local_path in approved_names:
            continue
        suffix = Path(local_path).suffix.lower()
        if suffix in {".md", ".txt", ".json", ".csv", ".py"}:
            return True
        if suffix == ".html" and Path(local_path).name.lower() != "index.html":
            return True
    return False


def strip_private_public_material(
    html_text: str, language: str, approved_names: Iterable[str] = (),
) -> str:
    approved_names = set(approved_names)
    def strip_list_item(match: re.Match[str]) -> str:
        item = match.group(0)
        if PRIVATE_MESSAGE_METADATA_RE.search(item) or unpublished_local_text_reference(item, approved_names):
            return ""
        return item

    def strip_anchor(match: re.Match[str]) -> str:
        anchor = match.group(0)
        if not unpublished_local_text_reference(anchor, approved_names):
            return anchor
        label = "private working file omitted" if language.lower().startswith("en") else "비공개 작업 파일 생략"
        return f'<span class="private-source-omitted">{label}</span>'

    stripped = HTML_LIST_ITEM_RE.sub(strip_list_item, html_text)
    return HTML_ANCHOR_RE.sub(strip_anchor, stripped)


def inject_public_local_note(html_text: str, language: str) -> str:
    html_text = PUBLIC_LOCAL_NOTE_RE.sub("\n", html_text)
    metrics_enabled = bool(public_metrics_endpoint())
    if language.lower().startswith("en"):
        metrics_note = (
            "<p class=\"metrics-disclosure\">Public views and average reading time are recorded only "
            "as aggregate values by page path, without personal identifiers.</p>"
            if metrics_enabled
            else ""
        )
        public_note = (
            "\n<section id=\"public-local-references\" class=\"public-note\">"
            "<p>This public HTML includes the article, figures, and public external references. "
            "Private working notes and message metadata are not published.</p>"
            f"{metrics_note}"
            "</section>\n"
        )
    else:
        metrics_note = (
            "<p class=\"metrics-disclosure\">공개 조회수와 평균 읽은 시간은 개인 식별 정보 없이 "
            "페이지 경로 단위의 집계값으로만 기록합니다.</p>"
            if metrics_enabled
            else ""
        )
        public_note = (
            "\n<section id=\"public-local-references\" class=\"public-note\">"
            "<p>공개 HTML에는 본문, 그림과 공개 외부 참고 링크만 포함합니다. "
            "비공개 작업 메모와 메시지 메타데이터는 게시하지 않습니다.</p>"
            f"{metrics_note}"
            "</section>\n"
        )
    if "</body>" in html_text:
        return html_text.replace("</body>", public_note + "</body>")
    return html_text


def public_asset_names(
    values: Iterable[object], *, review: PublicReview | None = None, language: str = "ko",
) -> list[str]:
    approved_names = set(approved_video_assets(review, language).values())
    return sorted(
        {
            str(value)
            for value in values
            if Path(str(value)).suffix.lower() in PUBLIC_REVIEW_FILE_SUFFIXES
            or str(value) in approved_names
        }
    )


def prune_public_support_files(
    public_dir: Path, *, review: PublicReview | None = None, language: str = "ko",
) -> None:
    approved_names = set(approved_video_assets(review, language).values())
    if not public_dir.exists():
        return
    for support_path in public_dir.iterdir():
        if not support_path.is_file() or support_path.name == "index.html":
            continue
        if support_path.suffix.lower() not in PUBLIC_REVIEW_FILE_SUFFIXES and support_path.name not in approved_names:
            support_path.unlink()


def credential_value_looks_secret(value: str) -> bool:
    lowered = value.lower()
    placeholders = (
        "example",
        "sample",
        "dummy",
        "your_",
        "your-",
        "replace",
        "redact",
        "changeme",
        "placeholder",
    )
    if any(marker in lowered for marker in placeholders) or value.startswith(("${", "{{", "<", "[")):
        return False
    if len(value) < 20:
        return False
    character_classes = sum(
        (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
            any(not character.isalnum() for character in value),
        )
    )
    return character_classes >= 2


def private_url(value: str) -> bool:
    candidate = html.unescape(value).rstrip(".,;!?")
    try:
        parts = urlsplit(candidate)
    except ValueError:
        return False
    if parts.scheme.lower() == "file" or parts.password is not None:
        return True
    hostname = (parts.hostname or "").lower().rstrip(".")
    if not hostname:
        return False
    if hostname == "localhost" or hostname.endswith((".localhost", ".internal", ".local", ".lan")):
        return True
    if hostname == "intranet" or hostname.startswith("intranet."):
        return True
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return any(address in network for network in PRIVATE_IP_NETWORKS)


def sanitize_public_text(text: str) -> str:
    def redact_assignment(match: re.Match[str]) -> str:
        value = match.group("value")
        if not credential_value_looks_secret(value):
            return match.group(0)
        quote = match.group("quote")
        return f'{match.group("prefix")}{quote}[credential removed]{quote}'

    def redact_private_link(match: re.Match[str]) -> str:
        return "[private link removed]" if private_url(match.group(0)) else match.group(0)

    sanitized = PRIVATE_KEY_BLOCK_RE.sub("[private key removed]", text)
    sanitized = AUTHORIZATION_CREDENTIAL_RE.sub(r"\g<prefix>[credential removed]", sanitized)
    sanitized = KNOWN_CREDENTIAL_RE.sub("[credential removed]", sanitized)
    sanitized = CREDENTIAL_ASSIGNMENT_RE.sub(redact_assignment, sanitized)
    sanitized = PRIVATE_URL_RE.sub(redact_private_link, sanitized)
    return INTERNAL_PATH_RE.sub("[local path removed]", sanitized)


def public_text_risks(text: str) -> list[str]:
    risks: list[str] = []
    if INTERNAL_PATH_RE.search(text):
        risks.append("internal path")
    if PRIVATE_MESSAGE_METADATA_RE.search(text):
        risks.append("private message metadata")
    if PRIVATE_KEY_BLOCK_RE.search(text) or AUTHORIZATION_CREDENTIAL_RE.search(text):
        risks.append("credential-like secret")
    if KNOWN_CREDENTIAL_RE.search(text):
        risks.append("credential-like secret")
    if any(
        credential_value_looks_secret(match.group("value"))
        for match in CREDENTIAL_ASSIGNMENT_RE.finditer(text)
    ):
        risks.append("credential-like secret")
    if any(private_url(match.group(0)) for match in PRIVATE_URL_RE.finditer(text)):
        risks.append("private link")
    visible_math_text = SCRIPT_STYLE_BLOCK_RE.sub("", text)
    if SMARTY_ENTITY_IN_MATH_RE.search(visible_math_text):
        risks.append("smart-quote entity inside math")
    if re.search(r"W(?:&rsquo;|')?\s*<em\b", text, flags=re.IGNORECASE):
        risks.append("markdown emphasis inside math")
    return list(dict.fromkeys(risks))


def validate_video_text(source_path: Path) -> None:
    """Fail on private text instead of silently changing a timed/public master."""
    if source_path.stat().st_size > 512 * 1024:
        raise ValueError(f"Video text exceeds the reviewed size limit: {source_path.name}")
    try:
        text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Video text is not UTF-8: {source_path.name}") from error
    risks = public_text_risks(html.unescape(text))
    if risks:
        raise ValueError(f"Unsafe video text in {source_path.name}: {', '.join(risks)}")
    if not text.strip():
        raise ValueError(f"Empty video text: {source_path.name}")
    if source_path.suffix.lower() != ".vtt":
        return
    if not re.match(r"\A\ufeff?WEBVTT(?:[ \t][^\r\n]*)?\r?\n", text):
        raise ValueError(f"Missing WEBVTT header: {source_path.name}")
    timestamp = r"(?:\d{2,}:)?\d{2}:\d{2}\.\d{3}"
    cues = re.findall(rf"^({timestamp})[ \t]+-->[ \t]+({timestamp})(?:[ \t].*)?$", text, re.MULTILINE)
    if not cues or len(cues) != text.count("-->"):
        raise ValueError(f"Invalid video caption timing: {source_path.name}")
    last_end = 0.0
    for start, end in cues:
        def seconds(value: str) -> float:
            parts = value.split(":")
            hours, minutes, secs = (["0"] + parts) if len(parts) == 2 else parts
            if int(minutes) >= 60 or float(secs) >= 60:
                raise ValueError(f"Invalid video caption timestamp: {source_path.name}")
            return int(hours) * 3600 + int(minutes) * 60 + float(secs)
        left, right = seconds(start), seconds(end)
        if left < last_end - .001 or right <= left:
            raise ValueError(f"Unordered video captions: {source_path.name}")
        last_end = right


def mp4_boxes(data: bytes, start: int = 0, end: int | None = None):
    """Read ISO-BMFF box boundaries; media decoding is a separate render QA."""
    end = len(data) if end is None else end
    while start < end:
        if start + 8 > end:
            raise ValueError("Truncated MP4 box header")
        size = int.from_bytes(data[start:start + 4], "big")
        kind = data[start + 4:start + 8]
        header = 8
        if size == 1:
            if start + 16 > end:
                raise ValueError("Truncated extended MP4 box")
            size, header = int.from_bytes(data[start + 8:start + 16], "big"), 16
        elif size == 0:
            size = end - start
        if size < header or start + size > end:
            raise ValueError("Invalid MP4 box size")
        yield kind, start + header, start + size
        start += size


def validate_video_binary(source_path: Path) -> None:
    """Check final-container metadata without depending on a local ffprobe."""
    data = source_path.read_bytes()
    if source_path.suffix.lower() == ".webp":
        if data[:4] != b"RIFF" or data[8:12] != b"WEBP" or int.from_bytes(data[4:8], "little") + 8 != len(data):
            raise ValueError(f"Invalid WebP poster: {source_path.name}")
        offset, image_chunks = 12, 0
        while offset < len(data):
            if offset + 8 > len(data):
                raise ValueError("Truncated WebP poster chunk")
            kind = data[offset:offset + 4]
            size = int.from_bytes(data[offset + 4:offset + 8], "little")
            end = offset + 8 + size
            if end > len(data) or kind not in {b"VP8 ", b"VP8L", b"VP8X", b"ALPH"}:
                raise ValueError(f"Unapproved WebP metadata/chunk in {source_path.name}")
            if kind == b"VP8X" and (size != 10 or data[offset + 8] & 0x2e):
                raise ValueError(f"Poster contains metadata or animation flags: {source_path.name}")
            image_chunks += kind in {b"VP8 ", b"VP8L"}
            offset = end + size % 2
        if offset != len(data) or image_chunks != 1:
            raise ValueError(f"Invalid static WebP poster: {source_path.name}")
        return
    if source_path.suffix.lower() != ".mp4":
        raise ValueError(f"Unapproved video binary: {source_path.name}")
    top = list(mp4_boxes(data))
    kinds = [kind for kind, _, _ in top]
    if any(k not in {b"ftyp", b"moov", b"mdat", b"free"} for k in kinds) or any(kinds.count(k) != 1 for k in (b"ftyp", b"moov", b"mdat")):
        raise ValueError(f"Unexpected MP4 container layout: {source_path.name}")
    if kinds[0] != b"ftyp" or kinds.index(b"moov") > kinds.index(b"mdat"):
        raise ValueError(f"MP4 must use fast start: {source_path.name}")

    def check_handler(start: int, end: int) -> None:
        name = data[start + 24:end].decode("utf-8", errors="replace").rstrip("\0")
        if public_text_risks(name) or name not in {"", "VideoHandler", "SoundHandler", "MetadataHandler"}:
            raise ValueError(f"Unsafe MP4 track metadata: {source_path.name}")

    def walk(start: int, end: int) -> None:
        for kind, left, right in mp4_boxes(data, start, end):
            if kind in {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"edts", b"dinf"}:
                walk(left, right)
            elif kind == b"udta":
                for child, a, b in mp4_boxes(data, left, right):
                    if child != b"meta":
                        raise ValueError(f"Unapproved MP4 user metadata: {source_path.name}")
                    for field, c, d in mp4_boxes(data, a + 4, b):
                        if field == b"hdlr":
                            check_handler(c, d)
                        elif field == b"ilst":
                            for item, e, f in mp4_boxes(data, c, d):
                                if item != b"\xa9too":
                                    raise ValueError(f"Unapproved MP4 metadata field: {source_path.name}")
                                for value, g, h in mp4_boxes(data, e, f):
                                    encoder = data[g + 8:h].decode("utf-8", errors="replace").rstrip("\0")
                                    if value != b"data" or not re.fullmatch(r"Lav[fc][0-9.]+(?: libx264)?", encoder):
                                        raise ValueError(f"Unapproved MP4 encoder metadata: {source_path.name}")
                        else:
                            raise ValueError(f"Unapproved MP4 metadata field: {source_path.name}")
            elif kind == b"hdlr":
                check_handler(left, right)
            elif kind == b"dref":
                references = list(mp4_boxes(data, left + 8, right))
                if len(references) != 1 or int.from_bytes(data[left + 4:left + 8], "big") != 1 or any(
                    entry != b"url " or data[a:b] != b"\0\0\0\1" for entry, a, b in references
                ):
                    raise ValueError(f"MP4 must not contain external data references: {source_path.name}")
            elif kind in {b"meta", b"uuid", b"name"} or kind.startswith(b"\xa9"):
                raise ValueError(f"Unapproved MP4 metadata: {source_path.name}")
    for kind, start, end in top:
        if kind == b"moov":
            walk(start, end)
        elif kind == b"free" and any(data[start:end]):
            raise ValueError(f"Nonempty MP4 padding metadata: {source_path.name}")


def validate_video_embed(
    text: str, directory: Path, review: PublicReview | None, language: str,
) -> set[str]:
    parser = VideoEmbedParser()
    parser.feed(text)
    if not parser.videos:
        return set()
    names = approved_video_assets(review, language)
    if not names or len(parser.videos) != 1:
        raise ValueError("Native video is approved only for the registered Noether abstract")
    record = parser.videos[0]
    attrs = record["attrs"]
    if not {"controls", "playsinline"} <= attrs.keys() or {"autoplay", "loop"} & attrs.keys() or attrs.get("preload") not in {"none", "metadata"}:
        raise ValueError("Video must have reader controls, inline playback and restrained preloading")

    def require_url(value: str, expected: str) -> None:
        if is_external_or_anchor(value) or split_local_url(value)[0] != expected:
            raise ValueError(f"Video reference must use the approved flat filename: {expected}")
    require_url(attrs.get("poster", ""), names["poster"])
    sources = ([attrs["src"]] if attrs.get("src") else []) + [s.get("src", "") for s in record["sources"]]
    if len(sources) != 1:
        raise ValueError("Video must have exactly one approved MP4 source")
    require_url(sources[0], names["video"])
    tracks = record["tracks"]
    if len(tracks) != 1 or tracks[0].get("kind") not in {"captions", "subtitles"} or tracks[0].get("srclang") != language:
        raise ValueError("Video must use its own language's caption timeline")
    require_url(tracks[0].get("src", ""), names["captions"])
    if not any(not is_external_or_anchor(url) and split_local_url(url)[0] == names["transcript"] for url in parser.hrefs):
        raise ValueError("Video requires its approved visual transcript link")
    directory_root = directory.resolve()
    for role, filename in names.items():
        source = directory / filename
        if source.is_symlink() or not source.is_file() or source.resolve().parent != directory_root:
            raise ValueError(f"Missing or nonlocal approved video asset: {filename}")
        if role in {"captions", "transcript"}:
            validate_video_text(source)
        else:
            validate_video_binary(source)
    return set(names.values())


def copy_public_file(source_path: Path, dest_path: Path) -> None:
    if source_path.suffix.lower() == ".vtt" or source_path.name in {
        names["transcript"] for names in NOETHER_VIDEO_ASSETS.values()
    }:
        validate_video_text(source_path)
        shutil.copy2(source_path, dest_path)
        return
    if source_path.suffix.lower() not in PUBLIC_TEXT_FILE_SUFFIXES:
        shutil.copy2(source_path, dest_path)
        return
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Public text support file is not UTF-8: {source_path}") from error
    dest_path.write_text(sanitize_public_text(source_text), encoding="utf-8")
    shutil.copystat(source_path, dest_path)


def cloudflare_web_analytics_snippet(indent: int = 4) -> str:
    token = os.environ.get(CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV, "").strip()
    if not token:
        return ""

    beacon_config = json.dumps({"token": token}, separators=(",", ":"))
    beacon_config = (
        beacon_config.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
    )
    pad = " " * indent
    return (
        f"\n{pad}<!-- Cloudflare Web Analytics -->"
        f"\n{pad}<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
        f"data-cf-beacon='{beacon_config}'></script>"
        f"\n{pad}<!-- End Cloudflare Web Analytics -->"
    )


def public_metrics_endpoint() -> str:
    endpoint = (
        os.environ.get(PUBLIC_METRICS_ENDPOINT_ENV)
        or os.environ.get(LEGACY_PUBLIC_METRICS_ENDPOINT_ENV)
        or DEFAULT_PUBLIC_METRICS_ENDPOINT
    )
    endpoint = endpoint.strip().rstrip("/")
    if not endpoint:
        return ""
    parts = urlsplit(endpoint)
    if (
        parts.scheme.lower() not in {"http", "https"}
        or not parts.netloc
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
    ):
        raise ValueError(
            f"{PUBLIC_METRICS_ENDPOINT_ENV} must be an http(s) URL without credentials"
        )
    return endpoint


def restore_published_analytics() -> None:
    """Retain published, public analytics settings on a newly configured host."""
    index = SITE_DIR / "index.html"
    if not index.exists():
        return
    existing = index.read_text(encoding="utf-8")
    if not (os.environ.get(PUBLIC_METRICS_ENDPOINT_ENV) or os.environ.get(LEGACY_PUBLIC_METRICS_ENDPOINT_ENV)):
        match = re.search(r'window\.AI_TECH_REVIEW_METRICS\s*=\s*(\{[^<]*?\})\s*;', existing)
        if match:
            endpoint = json.loads(match.group(1)).get("endpoint", "")
            if endpoint:
                os.environ[PUBLIC_METRICS_ENDPOINT_ENV] = endpoint
                public_metrics_endpoint()  # Validate before rendering any output.
    if not os.environ.get(CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV):
        match = re.search(r"data-cf-beacon=['\"]([^'\"]+)['\"]", existing)
        if match:
            token = json.loads(html.unescape(match.group(1))).get("token", "")
            if token:
                os.environ[CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV] = token


def public_icon_links(asset_prefix: str = "", indent: int = 4) -> str:
    pad = " " * indent
    version = f"?v={ICON_ASSET_VERSION}"
    prefix = html.escape(asset_prefix, quote=True)
    return (
        f"\n{pad}<!-- AI Tech Review Icons -->"
        f"\n{pad}<link rel=\"icon\" href=\"{prefix}favicon.ico{version}\" sizes=\"any\">"
        f"\n{pad}<link rel=\"icon\" href=\"{prefix}assets/ai-tech-review-icon.svg{version}\" type=\"image/svg+xml\">"
        f"\n{pad}<link rel=\"apple-touch-icon\" href=\"{prefix}assets/apple-touch-icon.png{version}\">"
        f"\n{pad}<!-- End AI Tech Review Icons -->"
    )


def public_metrics_head(asset_prefix: str = "", indent: int = 4) -> str:
    pad = " " * indent
    href = f"{asset_prefix}assets/public-metrics.css"
    return (
        f"\n{pad}<!-- AI Tech Review Public Metrics Styles -->"
        f"\n{pad}<link rel=\"stylesheet\" href=\"{html.escape(href, quote=True)}\">"
        f"\n{pad}<!-- End AI Tech Review Public Metrics Styles -->"
    )


def public_metrics_scripts(asset_prefix: str = "", indent: int = 4) -> str:
    endpoint = public_metrics_endpoint()
    if not endpoint:
        return ""
    config = json.dumps(
        {"endpoint": endpoint, "basePath": PUBLIC_BASE_PATH, "siteId": PUBLIC_SITE_ID},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    config = config.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    script_src = f"{asset_prefix}assets/public-metrics.js"
    pad = " " * indent
    return (
        f"\n{pad}<!-- AI Tech Review Public Metrics -->"
        f"\n{pad}<script>window.AI_TECH_REVIEW_METRICS={config};</script>"
        f"\n{pad}<script defer src=\"{html.escape(script_src, quote=True)}\"></script>"
        f"\n{pad}<!-- End AI Tech Review Public Metrics -->"
    )


def inject_public_metrics(html_text: str, asset_prefix: str = "") -> str:
    html_text = PUBLIC_METRICS_HEAD_RE.sub("", html_text)
    html_text = PUBLIC_METRICS_SCRIPT_RE.sub("", html_text)
    html_text = PUBLIC_METRICS_CSS_LINK_RE.sub("", html_text)
    html_text = PUBLIC_METRICS_CONFIG_RE.sub("", html_text)
    html_text = PUBLIC_METRICS_JS_RE.sub("", html_text)
    head = public_metrics_head(asset_prefix)
    scripts = public_metrics_scripts(asset_prefix)
    if head and "</head>" in html_text:
        html_text = re.sub(r"[ \t\r\n]*</head>", head + "\n  </head>", html_text, count=1)
    if scripts and "</body>" in html_text:
        html_text = re.sub(r"[ \t\r\n]*</body>", scripts + "\n  </body>", html_text, count=1)
    return html_text


def inject_public_icons(html_text: str, asset_prefix: str = "") -> str:
    html_text = PUBLIC_ICON_RE.sub("", html_text)
    html_text = PUBLIC_ICON_LINK_RE.sub("", html_text)
    icons = public_icon_links(asset_prefix)
    if icons and "</head>" in html_text:
        return re.sub(r"[ \t\r\n]*</head>", icons + "\n  </head>", html_text, count=1)
    return html_text


def inject_cloudflare_web_analytics(html_text: str) -> str:
    snippet = cloudflare_web_analytics_snippet()
    if not snippet:
        return html_text
    html_text = CLOUDFLARE_WEB_ANALYTICS_RE.sub("\n", html_text)
    if "</body>" not in html_text:
        return html_text + snippet + "\n"
    return re.sub(r"\n[ \t]*</body>", snippet + "\n  </body>", html_text, count=1)


def metric_path_for_href(href: str) -> str:
    path = f"{PUBLIC_BASE_PATH.rstrip('/')}/{href}".replace("\\", "/")
    return re.sub(r"/index\.html$", "/", path)


def public_url_for_href(href: str) -> str:
    relative = re.sub(r"/index\.html$", "/", href.replace("\\", "/"))
    return f"{PUBLIC_BASE_URL}{relative}"


def asset_prefix_for_public_dir(public_dir: Path) -> str:
    relative = os.path.relpath(SITE_DIR, public_dir).replace("\\", "/")
    return "" if relative == "." else f"{relative.rstrip('/')}/"


def normalize_review_metadata(
    html_text: str,
    review: PublicReview,
    language: str,
    public_dir: Path,
) -> str:
    relative_dir = public_dir.resolve().relative_to(SITE_DIR.resolve())
    href = (relative_dir / "index.html").as_posix()
    canonical_url = public_url_for_href(href)
    metadata = PageMetadataParser()
    metadata.feed(html_text)
    display_title = review.title
    if language.lower().startswith("en"):
        display_title = metadata.h1_text or metadata.title_text or review.title

    normalized = CANONICAL_LINK_RE.sub("\n", html_text)
    normalized = OG_TITLE_RE.sub("\n", normalized)
    tags = (
        f'\n    <link rel="canonical" href="{html.escape(canonical_url, quote=True)}">'
        f'\n    <meta property="og:title" content="{html.escape(display_title, quote=True)}">'
    )
    if re.search(r"</head>", normalized, flags=re.IGNORECASE):
        return re.sub(
            r"[ \t\r\n]*</head>",
            tags + "\n  </head>",
            normalized,
            count=1,
            flags=re.IGNORECASE,
        )
    return normalized


def unique_dest_name(source_path: Path, used_names: set[str]) -> str:
    candidate = source_path.name
    if candidate not in used_names:
        used_names.add(candidate)
        return candidate
    index = 2
    while True:
        candidate = f"{source_path.stem}_{index}{source_path.suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        index += 1


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for item in path.rglob("*"):
        try:
            mode = stat.S_IWRITE | stat.S_IREAD
            if item.is_dir():
                mode |= stat.S_IEXEC
            item.chmod(mode)
        except OSError:
            pass
    path.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    shutil.rmtree(path)


def default_verification_scope(review: PublicReview, language: str) -> tuple[str, ...]:
    is_english = language.lower().startswith("en")
    if review.primary_sources_checked:
        if is_english:
            return (
                "primary and official sources listed in the article",
                "public links and final HTML",
            )
        return ("본문에 기재된 원문·공식 자료", "공개 링크와 최종 HTML")
    if is_english:
        return (
            "original source-verification record not retained",
            "current public links and final HTML checked",
        )
    return ("원 작성 세션의 출처 검증 기록 미보존", "현재 공개 링크와 최종 HTML 확인")


def authoring_disclosure_note(review: PublicReview, language: str) -> str:
    if language.lower().startswith("en"):
        return review.disclosure_note_en or (
            "Missing model, agent, or original verification details are marked as not retained "
            "and are not reconstructed by inference."
        )
    return review.disclosure_note_ko or (
        "보존되지 않은 모델·에이전트·원 작성 세션 검증 정보는 미보존으로 표시하며 "
        "추정해 재구성하지 않습니다."
    )


def provenance_value_is_default(value: object) -> bool:
    if isinstance(value, (list, tuple)):
        return not value or all(provenance_value_is_default(item) for item in value)
    text = str(value or "").strip().casefold()
    return not text or any(
        marker in text
        for marker in (
            "not retained",
            "record not retained",
            "미보존",
            "보존되지 않음",
        )
    )


def historical_disclosure_value(
    fields: dict[str, str] | None,
    labels: tuple[str, ...],
) -> str:
    if not fields:
        return ""
    normalized_labels = {label.casefold() for label in labels}
    for label, value in fields.items():
        if label.casefold() in normalized_labels:
            return value.strip()
    return ""


def render_authoring_disclosure(
    review: PublicReview,
    language: str,
    methods_href: str,
    historical_fields: dict[str, str] | None = None,
) -> tuple[str, str]:
    is_english = language.lower().startswith("en")
    editor = review.responsible_editor_en if is_english else review.responsible_editor
    cutoff = review.evidence_cutoff or review.updated
    if is_english:
        roles = (
            tuple(f"{agent.name} — {agent.role}" for agent in review.agents)
            or review.agent_roles
            or ("individual agent-role roster not retained",)
        )
        scope = review.verification_scope or default_verification_scope(review, language)
        human_review_level = review.human_review_level
    else:
        roles = (
            tuple(f"{agent.name} — {agent.role_ko}" for agent in review.agents)
            or review.agent_roles_ko
            or ("원 작성 세션의 개별 에이전트 역할 기록 미보존",)
        )
        scope = review.verification_scope_ko or default_verification_scope(review, language)
        human_review_level = review.human_review_level_ko
    role_text = "; ".join(roles)
    system_text = (
        f"{review.ai_system}; {review.ai_model}"
        if is_english
        else f"{review.ai_system_ko}; {review.ai_model_ko}"
    )
    historical_system = historical_disclosure_value(
        historical_fields,
        ("AI system", "AI 시스템"),
    )
    configured_system = review.ai_system if is_english else review.ai_system_ko
    configured_model = review.ai_model if is_english else review.ai_model_ko
    if (
        historical_system
        and provenance_value_is_default(configured_system)
        and provenance_value_is_default(configured_model)
    ):
        system_text = historical_system
    historical_roles = historical_disclosure_value(
        historical_fields,
        ("Verifiable agent roles", "확인 가능한 에이전트 역할"),
    )
    configured_roles = roles if review.agents else (
        review.agent_roles if is_english else review.agent_roles_ko
    )
    if historical_roles and provenance_value_is_default(configured_roles):
        role_text = historical_roles
    scope_text = "; ".join(scope)
    note = authoring_disclosure_note(review, language)
    source_check_label = (
        "primary sources checked"
        if review.primary_sources_checked
        else "original verification record not retained"
    )
    source_check_label_ko = (
        "원문 우선 검증"
        if review.primary_sources_checked
        else "원 작성 세션 검증 기록 미보존"
    )
    methods_url = html.escape(methods_href, quote=True)

    if is_english:
        strip = (
            '<p class="byline-disclosure">'
            f'{html.escape(editor)} · AI-assisted · {source_check_label} · '
            f'evidence cutoff {html.escape(cutoff)} · '
            f'<a href="{methods_url}">Methods &amp; agent disclosure</a></p>'
        )
        details = f"""
      <!-- AI Tech Review Authoring Disclosure -->
      <section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="authoring-disclosure-heading">
        <p class="disclosure-kicker">Authorship, AI assistance &amp; verification</p>
        <h2 id="authoring-disclosure-heading">How this review was made</h2>
        <dl>
          <div><dt>Responsible editor</dt><dd>{html.escape(editor)}</dd></div>
          <div><dt>AI system</dt><dd>{html.escape(system_text)}</dd></div>
          <div><dt>Verifiable agent roles</dt><dd>{html.escape(role_text)}</dd></div>
          <div><dt>Editorial harness</dt><dd>{html.escape(EDITORIAL_HARNESS_NAME)} v{html.escape(EDITORIAL_HARNESS_VERSION)} · <a href="{methods_url}">public method</a></dd></div>
          <div><dt>Verification scope</dt><dd>{html.escape(scope_text)}</dd></div>
          <div><dt>Human review record</dt><dd>{html.escape(human_review_level)}</dd></div>
          <div><dt>Evidence cutoff</dt><dd>{html.escape(cutoff)}</dd></div>
        </dl>
        <p class="disclosure-note">{html.escape(note)}</p>
      </section>
      <!-- End AI Tech Review Authoring Disclosure -->
"""
    else:
        strip = (
            '<p class="byline-disclosure">'
            f'{html.escape(editor)} · AI 보조 · {source_check_label_ko} · '
            f'근거 기준일 {html.escape(cutoff)} · '
            f'<a href="{methods_url}">작성 방법·에이전트 공개</a></p>'
        )
        details = f"""
      <!-- AI Tech Review Authoring Disclosure -->
      <section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="authoring-disclosure-heading">
        <p class="disclosure-kicker">Authorship, AI assistance &amp; verification</p>
        <h2 id="authoring-disclosure-heading">작성·검증 정보</h2>
        <dl>
          <div><dt>책임 편집자</dt><dd>{html.escape(editor)}</dd></div>
          <div><dt>AI 시스템</dt><dd>{html.escape(system_text)}</dd></div>
          <div><dt>확인 가능한 에이전트 역할</dt><dd>{html.escape(role_text)}</dd></div>
          <div><dt>편집 하네스</dt><dd>{html.escape(EDITORIAL_HARNESS_NAME)} v{html.escape(EDITORIAL_HARNESS_VERSION)} · <a href="{methods_url}">공개 방법서</a></dd></div>
          <div><dt>검증 범위</dt><dd>{html.escape(scope_text)}</dd></div>
          <div><dt>사람 검토 기록</dt><dd>{html.escape(human_review_level)}</dd></div>
          <div><dt>근거 기준일</dt><dd>{html.escape(cutoff)}</dd></div>
        </dl>
        <p class="disclosure-note">{html.escape(note)}</p>
      </section>
      <!-- End AI Tech Review Authoring Disclosure -->
"""
    return strip, details


def repair_disclosure_fragment_links(
    html_text: str,
    removed_ids: set[str] | None = None,
) -> str:
    metadata = PageMetadataParser()
    metadata.feed(html_text)
    removed_ids = removed_ids or set()
    disclosure_labels = {
        "작성 정보",
        "작성정보",
        "작성·검증 정보",
        "publication information",
        "how this review was made",
        "authorship and disclosure",
    }

    def replace_anchor(match: re.Match[str]) -> str:
        fragment = unquote(html.unescape(match.group("fragment")))
        label = html.unescape(re.sub(r"<[^>]+>", "", match.group("label"))).strip().casefold()
        if fragment in metadata.ids:
            return match.group(0)
        if fragment not in removed_ids and label not in disclosure_labels:
            return match.group(0)
        return f'{match.group("prefix")}#authoring-disclosure{match.group("middle")}{match.group("label")}</a>'

    return re.sub(
        r'(?P<prefix><a\b[^>]*\bhref=["\'])#(?P<fragment>[^"\']+)'
        r'(?P<middle>["\'][^>]*>)(?P<label>.*?)</a>',
        replace_anchor,
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def inject_review_navigation_and_disclosure(
    html_text: str,
    review: PublicReview,
    language: str,
    methods_href: str,
) -> str:
    is_english = language.lower().startswith("en")
    hub_label = "Review hub" if is_english else "리뷰 허브"
    marked_disclosure = AUTHORING_DISCLOSURE_BLOCK_RE.search(html_text)
    has_unmarked_disclosure = marked_disclosure is None and bool(
        re.search(
            r'<section\b[^>]*\bclass=["\'][^"\']*\bauthoring-disclosure\b[^"\']*["\']',
            html_text,
            flags=re.IGNORECASE,
        )
    )
    historical_fields: dict[str, str] | None = None
    removed_ids: set[str] = set()
    if marked_disclosure:
        historical = DisclosureMetadataParser()
        historical.feed(marked_disclosure.group(0))
        historical_fields = historical.fields
        removed_ids = set(
            re.findall(
                r'\bid=["\']([^"\']+)["\']',
                marked_disclosure.group(0),
                flags=re.IGNORECASE,
            )
        )
    has_hub_link = re.search(
        rf'<a\b[^>]*href=["\']{re.escape(PUBLIC_BASE_URL)}["\']',
        html_text,
        flags=re.IGNORECASE,
    )
    if not has_hub_link:
        hub_link = (
            f'<a class="hub-link" href="{PUBLIC_BASE_URL}">{hub_label}</a>\n        '
        )
        html_text = re.sub(
            r'(<div class="topline-actions">\s*)',
            r"\1" + hub_link,
            html_text,
            count=1,
        )
        if 'class="hub-link"' not in html_text:
            fallback_nav = (
                '<nav class="public-fallback-nav" aria-label="AI Tech Review">'
                f'<a class="hub-link" href="{PUBLIC_BASE_URL}">{hub_label}</a>'
                "</nav>"
            )
            html_text = re.sub(
                r"(<body\b[^>]*>)",
                r"\1\n  " + fallback_nav,
                html_text,
                count=1,
                flags=re.IGNORECASE,
            )

    html_text = AUTHORING_DISCLOSURE_BLOCK_RE.sub("\n", html_text)
    html_text = re.sub(
        r'\s*<p class="byline-disclosure">.*?</p>\s*',
        "\n",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    strip, details = render_authoring_disclosure(
        review,
        language,
        methods_href,
        historical_fields,
    )
    with_strip = re.sub(
        r'(<main class="content-grid">)',
        strip + r"\n  \1",
        html_text,
        count=1,
    )
    if with_strip == html_text:
        with_strip = re.sub(
            r"(<main\b[^>]*>)",
            strip + r"\n  \1",
            html_text,
            count=1,
            flags=re.IGNORECASE,
        )
    if with_strip == html_text:
        with_strip = re.sub(
            r"(</header>)",
            r"\1\n  " + strip,
            html_text,
            count=1,
            flags=re.IGNORECASE,
        )
    if with_strip == html_text:
        with_strip = re.sub(
            r"(<body\b[^>]*>)",
            r"\1\n  " + strip,
            html_text,
            count=1,
            flags=re.IGNORECASE,
    )
    html_text = with_strip
    if has_unmarked_disclosure:
        repaired = repair_disclosure_fragment_links(html_text, removed_ids)
        return re.sub(r"[ \t]+(?=\r?$)", "", repaired, flags=re.MULTILINE)
    if '<div class="footer">' in html_text:
        html_text = html_text.replace(
            '<div class="footer">',
            details + '      <div class="footer">',
            1,
        )
    elif re.search(r"</main>", html_text, flags=re.IGNORECASE):
        html_text = re.sub(
            r"</main>",
            details + "    </main>",
            html_text,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        html_text = re.sub(
            r"</body>",
            details + "  </body>",
            html_text,
            count=1,
            flags=re.IGNORECASE,
        )
    repaired = repair_disclosure_fragment_links(html_text, removed_ids)
    return re.sub(r"[ \t]+(?=\r?$)", "", repaired, flags=re.MULTILINE)


def sanitize_for_public(
    html_text: str,
    dist_dir: Path,
    public_dir: Path,
    review: PublicReview,
    language: str = "ko",
    public_identity_dir: Path | None = None,
) -> tuple[str, list[str]]:
    copied: list[str] = []
    source_to_dest: dict[Path, str] = {}
    used_names: set[str] = {"index.html"}
    dist_root = dist_dir.resolve()
    video_files = validate_video_embed(html_text, dist_dir, review, language)

    def replace_ref(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            return match.group(0)

        local_path, query, fragment = split_local_url(raw_url)
        if not local_path:
            return match.group(0)

        source_path = (dist_dir / local_path).resolve()
        suffix = source_path.suffix.lower()
        if suffix in {".mp4", ".vtt"} or Path(local_path).name.startswith("noether-abstract-"):
            if local_path not in video_files:
                raise ValueError("Unapproved video asset filename or path")

        try:
            source_path.relative_to(dist_root)
        except ValueError:
            safe_url = html.escape(raw_url, quote=True)
            return f'data-blocked-ref="{safe_url}"'

        if suffix not in PUBLIC_REVIEW_FILE_SUFFIXES and local_path not in video_files:
            safe_url = html.escape(raw_url, quote=True)
            return f"data-local-ref=\"{safe_url}\""

        if not source_path.exists() or not source_path.is_file():
            safe_url = html.escape(raw_url, quote=True)
            return f"data-missing-ref=\"{safe_url}\""

        if source_path not in source_to_dest:
            dest_name = unique_dest_name(source_path, used_names)
            source_to_dest[source_path] = dest_name
            copy_public_file(source_path, public_dir / dest_name)
            copied.append(dest_name)

        new_url = rebuild_local_url(source_to_dest[source_path], query, fragment)
        return f"{match.group('prefix')}{html.escape(new_url, quote=True)}{match.group('suffix')}"

    sanitized = strip_private_public_material(html_text, language, video_files)
    sanitized = LOCAL_REF_RE.sub(replace_ref, sanitized)
    sanitized = sanitize_public_text(sanitized)
    sanitized = sanitized.replace("<body>", '<body class="public-review">')
    sanitized = inject_public_local_note(sanitized, language)
    identity_dir = public_identity_dir or public_dir
    asset_prefix = asset_prefix_for_public_dir(identity_dir)
    sanitized = normalize_review_metadata(sanitized, review, language, identity_dir)
    sanitized = inject_review_navigation_and_disclosure(
        sanitized,
        review,
        language,
        f"{asset_prefix}{EDITORIAL_METHODS_HREF}",
    )
    sanitized = inject_public_icons(sanitized, asset_prefix)
    sanitized = inject_public_metrics(sanitized, asset_prefix)
    return inject_cloudflare_web_analytics(sanitized), copied


def copy_public_support_files(
    dist_dir: Path, public_dir: Path, copied: list[str], *,
    review: PublicReview | None = None, language: str = "ko",
) -> list[str]:
    del dist_dir, public_dir
    return public_asset_names(copied, review=review, language=language)


def publish_dist_variant(
    dist_index: Path,
    public_dir: Path,
    review: PublicReview,
    language: str,
    public_identity_dir: Path | None = None,
) -> tuple[str, list[str]]:
    public_dir.mkdir(parents=True, exist_ok=True)
    raw_html = dist_index.read_text(encoding="utf-8")
    public_html, copied_assets = sanitize_for_public(
        raw_html,
        dist_index.parent,
        public_dir,
        review,
        language,
        public_identity_dir,
    )
    (public_dir / "index.html").write_text(public_html, encoding="utf-8")
    copied_assets = copy_public_support_files(
        dist_index.parent, public_dir, copied_assets, review=review, language=language,
    )
    return public_html, copied_assets


def refresh_existing_public_variant(
    review: PublicReview,
    public_dir: Path,
    language: str,
) -> str:
    index_path = public_dir / "index.html"
    existing_html = index_path.read_text(encoding="utf-8")
    asset_prefix = asset_prefix_for_public_dir(public_dir)
    video_files = validate_video_embed(existing_html, public_dir, review, language)
    refreshed = strip_private_public_material(existing_html, language, video_files)
    refreshed = sanitize_public_text(refreshed)
    refreshed = inject_public_local_note(refreshed, language)
    refreshed = normalize_review_metadata(refreshed, review, language, public_dir)
    refreshed = inject_review_navigation_and_disclosure(
        refreshed,
        review,
        language,
        f"{asset_prefix}{EDITORIAL_METHODS_HREF}",
    )
    refreshed = inject_public_icons(refreshed, asset_prefix)
    refreshed = inject_public_metrics(refreshed, asset_prefix)
    refreshed = inject_cloudflare_web_analytics(refreshed)
    index_path.write_text(refreshed, encoding="utf-8")
    prune_public_support_files(public_dir, review=review, language=language)
    return refreshed


def existing_translation_entries(
    review: PublicReview,
    existing_entry: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    prior_translations = {
        str(item.get("language")): item
        for item in ((existing_entry or {}).get("translations") or [])
        if isinstance(item, dict) and item.get("language")
    }
    for translation in review.translations:
        public_dir = review.translation_public_dir(translation)
        if not (public_dir / "index.html").exists():
            continue
        refresh_existing_public_variant(review, public_dir, translation.language)
        prior = prior_translations.get(translation.language)
        if prior is not None:
            assets = public_asset_names(prior.get("assets") or [], review=review, language=translation.language)
        else:
            assets = public_asset_names(
                (path.name for path in public_dir.iterdir()
                 if path.is_file() and path.name != "index.html"),
                review=review, language=translation.language,
            )
        href = review.translation_href(translation)
        entries.append(
            {
                "language": translation.language,
                "label": translation.label,
                "href": href,
                "metric_path": metric_path_for_href(href),
                "assets": assets,
            }
        )
    return entries


def build_review_manifest_entry(
    review: PublicReview,
    thumbnail: str,
    copied_assets: list[str],
    translations: list[dict[str, object]],
    existing_entry: dict[str, object] | None = None,
) -> dict[str, object]:
    agents = [
        {"name": agent.name, "role": agent.role, "role_ko": agent.role_ko}
        for agent in review.agents
    ]
    agent_roles = (
        [f"{agent.name} — {agent.role}" for agent in review.agents]
        or list(review.agent_roles)
        or ["individual agent-role roster not retained"]
    )
    agent_roles_ko = (
        [f"{agent.name} — {agent.role_ko}" for agent in review.agents]
        or list(review.agent_roles_ko)
        or ["원 작성 세션의 개별 에이전트 역할 기록 미보존"]
    )
    verification_scope = list(review.verification_scope) or list(
        default_verification_scope(review, "en")
    )
    verification_scope_ko = list(review.verification_scope_ko) or list(
        default_verification_scope(review, "ko")
    )
    entry: dict[str, object] = {
        "folder": review.folder,
        "title": review.title,
        "subtitle": review.subtitle,
        "date": review.date,
        "updated": review.updated,
        "category": review.category,
        "tags": list(review.tags),
        "summary": review.summary,
        "href": review.href,
        "metric_path": metric_path_for_href(review.href),
        "thumbnail": thumbnail,
        "assets": copied_assets,
        "translations": translations,
        "disclosure": {
            "responsible_editor": {
                "name_ko": review.responsible_editor,
                "name_en": review.responsible_editor_en,
            },
            "ai_assistance": {
                "system": review.ai_system,
                "system_ko": review.ai_system_ko,
                "model": review.ai_model,
                "model_ko": review.ai_model_ko,
                "agent_count": len(agents) if agents else None,
                "agents": agents,
                "agent_roles": agent_roles,
                "agent_roles_ko": agent_roles_ko,
            },
            "harness": {
                "name": EDITORIAL_HARNESS_NAME,
                "version": EDITORIAL_HARNESS_VERSION,
                "methods": EDITORIAL_METHODS_HREF,
            },
            "verification": {
                "evidence_cutoff": review.evidence_cutoff or review.updated,
                "primary_source_check": True if review.primary_sources_checked else None,
                "scope": verification_scope,
                "scope_ko": verification_scope_ko,
                "human_review_level": {
                    "ko": review.human_review_level_ko,
                    "en": review.human_review_level,
                },
            },
            "note": {
                "ko": authoring_disclosure_note(review, "ko"),
                "en": authoring_disclosure_note(review, "en"),
            },
        },
    }
    existing_disclosure = (existing_entry or {}).get("disclosure")
    if isinstance(existing_disclosure, dict):
        historical_ai = existing_disclosure.get("ai_assistance")
        disclosure = entry["disclosure"]
        if isinstance(historical_ai, dict) and isinstance(disclosure, dict):
            generated_ai = disclosure.get("ai_assistance")
            if isinstance(generated_ai, dict):
                for key, historical_value in historical_ai.items():
                    if provenance_value_is_default(generated_ai.get(key)):
                        generated_ai[key] = historical_value
    return entry


def preserve_published_review(
    review: PublicReview,
    existing_entry: dict[str, object] | None = None,
) -> dict[str, object]:
    public_index = review.public_dir / "index.html"
    if not public_index.exists():
        raise FileNotFoundError(f"Missing dist and published index for {review.folder}")

    existing_html = refresh_existing_public_variant(review, review.public_dir, "ko")
    parser = FirstImageParser()
    parser.feed(existing_html)
    if existing_entry is not None:
        thumbnail = str(existing_entry.get("thumbnail") or "")
        copied_assets = public_asset_names(existing_entry.get("assets") or [], review=review, language="ko")
    else:
        thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""
        copied_assets = public_asset_names(
            (path.name for path in review.public_dir.iterdir()
             if path.is_file() and path.name != "index.html"),
            review=review, language="ko",
        )
    print(f"[public-site:preserve] {review.folder} (source dist missing or not selected)")
    return build_review_manifest_entry(
        review,
        thumbnail,
        copied_assets,
        existing_translation_entries(review, existing_entry),
        existing_entry,
    )


def publish_review(
    review: PublicReview,
    existing_entry: dict[str, object] | None = None,
) -> dict[str, object]:
    if not review.dist_index.exists():
        return preserve_published_review(review, existing_entry)

    missing_translation_indexes = [
        review.translation_dist_index(translation)
        for translation in review.translations
        if not review.translation_dist_index(translation).exists()
    ]
    if missing_translation_indexes:
        missing_list = ", ".join(str(path) for path in missing_translation_indexes)
        raise FileNotFoundError(
            f"Missing translation dist index for {review.folder}: {missing_list}"
        )

    public_dir = review.public_dir
    public_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir = Path(
        tempfile.mkdtemp(prefix=f".{review.folder}.publish-", dir=public_dir.parent)
    )
    try:
        public_html, copied_assets = publish_dist_variant(
            review.dist_index,
            staging_dir,
            review,
            "ko",
            public_dir,
        )

        parser = FirstImageParser()
        parser.feed(public_html)
        thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""

        translation_entries: list[dict[str, object]] = []
        for translation in review.translations:
            dist_index = review.translation_dist_index(translation)
            translation_public_dir = staging_dir / translation.subdir
            _, translation_assets = publish_dist_variant(
                dist_index,
                translation_public_dir,
                review,
                translation.language,
                review.translation_public_dir(translation),
            )
            href = review.translation_href(translation)
            translation_entries.append(
                {
                    "language": translation.language,
                    "label": translation.label,
                    "href": href,
                    "metric_path": metric_path_for_href(href),
                    "assets": translation_assets,
                }
            )

        if public_dir.exists():
            remove_tree(public_dir)
        os.replace(staging_dir, public_dir)
    finally:
        if staging_dir.exists():
            remove_tree(staging_dir)

    return build_review_manifest_entry(
        review, thumbnail, copied_assets, translation_entries, existing_entry
    )


def render_translation_badges(item: dict[str, object]) -> str:
    translations = item.get("translations") or []
    if not isinstance(translations, list):
        return ""
    badges: list[str] = []
    for translation in translations:
        if not isinstance(translation, dict):
            continue
        href = str(translation.get("href") or "")
        language = str(translation.get("language") or "")
        label = str(translation.get("label") or language.upper())
        if not href or not language:
            continue
        badges.append(
            f'<a class="translation-badge" href="{html.escape(href, quote=True)}" '
            f'lang="{html.escape(language, quote=True)}" '
            f'hreflang="{html.escape(language, quote=True)}">{html.escape(label)}</a>'
        )
    return "".join(badges)


def render_review_card(item: dict[str, object]) -> str:
    return render_hub_card(item)



def render_latest_update(item: dict[str, object]) -> str:
    return render_hub_latest(item)



def render_category_chips(categories: list[str]) -> str:
    chips = ['<button type="button" class="category-chip active" data-category-filter="">전체</button>']
    chips.extend(
        f'<button type="button" class="category-chip" data-category-filter="{html.escape(category, quote=True)}">{html.escape(category)}</button>'
        for category in categories
    )
    return "\n".join(chips)


def render_index(
    manifest: list[dict[str, object]],
    preferred_category_order: list[str] | None = None,
    documents: list[dict] | None = None,
    language: str = "ko",
) -> str:
    return render_hub(
        manifest, preferred_category_order, documents,
        site_dir=SITE_DIR, language=language,
        css_version=hashlib.sha256(SITE_CSS.encode("utf-8")).hexdigest()[:12],
        js_version=hashlib.sha256(SITE_JS.encode("utf-8")).hexdigest()[:12],
        preferences_version=hashlib.sha256(HUB_PREFERENCES_JS.encode("utf-8")).hexdigest()[:12],
        library_version=LIBRARY_ASSET_VERSION,
    )



def copy_icon_assets() -> None:
    required = {
        "favicon.ico": SITE_DIR / "favicon.ico",
        "ai-tech-review-icon.svg": ASSETS_DIR / "ai-tech-review-icon.svg",
        "apple-touch-icon.png": ASSETS_DIR / "apple-touch-icon.png",
        "favicon-16x16.png": ASSETS_DIR / "favicon-16x16.png",
        "favicon-32x32.png": ASSETS_DIR / "favicon-32x32.png",
        "favicon-64x64.png": ASSETS_DIR / "favicon-64x64.png",
    }
    missing = [name for name in required if not (ICON_SOURCE_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing generated icon assets: {', '.join(missing)}")
    for name, dest in required.items():
        shutil.copy2(ICON_SOURCE_DIR / name, dest)


SITE_CSS = (HUB_ASSET_SOURCE_DIR / "hub.css").read_text(encoding="utf-8")


PUBLIC_METRICS_CSS = """
.public-metrics {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 18px 0 0;
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  color: #171b1f;
}
.public-metrics-pill,
.card-metrics span,
.latest-metrics span {
  display: inline-flex;
  align-items: baseline;
  gap: 5px;
  border: 1px solid rgba(13, 124, 102, 0.18);
  background: rgba(255, 255, 255, 0.78);
  color: #5c6670;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.35;
}
.public-metrics-pill {
  min-height: 36px;
  padding: 8px 11px;
  border-radius: 999px;
}
.public-metrics strong,
.card-metrics strong,
.latest-metrics strong {
  color: #0d7c66;
  font-weight: 900;
}
.public-metrics[data-state="loading"] strong,
.card-metrics[data-state="loading"] strong,
.latest-metrics[data-state="loading"] strong {
  color: #8a949c;
}
.public-metrics[data-state="loading"],
.public-metrics[data-state="error"],
.card-metrics[data-state="loading"],
.card-metrics[data-state="error"],
.latest-metrics[data-state="loading"],
.latest-metrics[data-state="error"] {
  display: none;
}
.public-metrics[data-state="error"] .public-metrics-pill {
  border-color: rgba(92, 102, 112, 0.16);
  color: #7a858e;
}
.card-metrics,
.latest-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin: 10px 0 12px;
}
.card-metrics span,
.latest-metrics span {
  padding: 5px 8px;
  border-radius: 999px;
}
.public-review .public-metrics {
  width: min(980px, calc(100% - 36px));
  margin: 14px auto 18px;
  padding: 0;
}
.public-review .public-metrics-pill {
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 8px 24px rgba(15, 23, 31, 0.08);
}
.public-review .byline-disclosure {
  width: min(980px, calc(100% - 36px));
  margin: 14px auto 22px;
  padding: 11px 14px;
  border: 1px solid rgba(13, 124, 102, 0.2);
  border-radius: 10px;
  background: #f4faf8;
  color: #4f5e58;
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  font-size: 13px;
  line-height: 1.6;
}
.public-review .public-fallback-nav {
  width: min(980px, calc(100% - 36px));
  margin: 12px auto 0;
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  font-size: 13px;
  font-weight: 800;
}
.public-review .byline-disclosure a,
.public-review .authoring-disclosure a {
  color: #0d6f5c;
  font-weight: 750;
}
.public-review .authoring-disclosure {
  margin: 44px 0 24px;
  padding: 24px;
  border: 1px solid rgba(13, 124, 102, 0.22);
  border-radius: 12px;
  background: linear-gradient(135deg, #f5faf8, #fbfaf7);
}
.public-review .authoring-disclosure .disclosure-kicker {
  margin: 0 0 6px;
  color: #0d6f5c;
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.public-review .authoring-disclosure h2 {
  margin: 0 0 16px;
}
.public-review .authoring-disclosure dl {
  display: grid;
  gap: 0;
  margin: 0;
}
.public-review .authoring-disclosure dl > div {
  display: grid;
  grid-template-columns: minmax(130px, 0.34fr) 1fr;
  gap: 16px;
  padding: 10px 0;
  border-top: 1px solid rgba(23, 33, 29, 0.1);
}
.public-review .authoring-disclosure dt {
  color: #273b34;
  font-weight: 800;
}
.public-review .authoring-disclosure dd {
  margin: 0;
}
.public-review .authoring-disclosure .disclosure-note {
  margin: 14px 0 0;
  color: #65716c;
  font-size: 0.88em;
}
@media (max-width: 680px) {
  .public-review .authoring-disclosure dl > div {
    grid-template-columns: 1fr;
    gap: 3px;
  }
}
@media (max-width: 680px) {
  .public-metrics {
    align-items: stretch;
  }
  .public-metrics-pill {
    flex: 1 1 140px;
    justify-content: center;
  }
}
"""


PUBLIC_METRICS_JS = """
(function () {
  const config = window.AI_TECH_REVIEW_METRICS || {};
  const endpoint = String(config.endpoint || "").replace(/\\/+$/, "");
  const basePath = String(config.basePath || "/AI_Tech_Review/");
  const siteId = String(config.siteId || "ai-tech-review");
  const isEnglish = (document.documentElement.lang || "").toLowerCase().startsWith("en");
  const locale = isEnglish ? "en-US" : "ko-KR";
  const isHttp = location.protocol === "https:" || location.protocol === "http:";

  if (!endpoint || !isHttp) {
    return;
  }

  const pagePath = canonicalPath(location.pathname);
  if (!pagePath.startsWith(basePath)) {
    return;
  }

  const pageWidget = insertPageWidget();
  const inlineMetricEls = Array.from(document.querySelectorAll("[data-inline-metrics][data-metric-path]"));
  const paths = Array.from(new Set([pagePath, ...inlineMetricEls.map((el) => canonicalPath(el.dataset.metricPath || ""))]));

  for (const el of inlineMetricEls) {
    el.dataset.state = "loading";
  }
  if (pageWidget) {
    pageWidget.dataset.state = "loading";
  }

  sendHitOnce()
    .catch(() => null)
    .then(() => loadSummary(paths))
    .then((summary) => {
      renderMetrics(summary);
      startEngagementTracking();
    })
    .catch(() => {
      if (pageWidget) {
        pageWidget.dataset.state = "error";
      }
      for (const el of inlineMetricEls) {
        el.dataset.state = "error";
      }
    });

  function canonicalPath(rawPath) {
    let path = String(rawPath || "").trim();
    if (!path) {
      return "";
    }
    if (/^https?:\\/\\//i.test(path)) {
      try {
        path = new URL(path).pathname;
      } catch {
        return "";
      }
    }
    if (!path.startsWith("/")) {
      path = "/" + path;
    }
    path = path.replace(/\\/index\\.html$/i, "/");
    if (path === basePath.replace(/\\/$/, "")) {
      path = basePath;
    }
    return path;
  }

  async function sendHitOnce() {
    const key = "ai-tech-review-hit:" + pagePath;
    try {
      if (sessionStorage.getItem(key)) {
        return;
      }
      sessionStorage.setItem(key, "1");
    } catch {
      // Some privacy modes block sessionStorage. Counting the page load is still acceptable.
    }
    await postJson("/hit", { path: pagePath });
  }

  async function loadSummary(metricPaths) {
    const url = new URL(endpoint + "/summary");
    url.searchParams.append("site", siteId);
    for (const path of metricPaths.filter(Boolean)) {
      url.searchParams.append("path", path);
    }
    const response = await fetch(url.toString(), { method: "GET", mode: "cors", cache: "no-store" });
    if (!response.ok) {
      throw new Error("metrics_summary_failed");
    }
    return response.json();
  }

  async function postJson(route, payload, keepalive) {
    const response = await fetch(endpoint + route, {
      method: "POST",
      mode: "cors",
      cache: "no-store",
      keepalive: Boolean(keepalive),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error("metrics_post_failed");
    }
    return response.json();
  }

  function renderMetrics(summary) {
    const pages = summary.pages || {};
    const page = pages[pagePath] || {};
    const site = (summary.sites || {})[siteId] || {};

    if (pageWidget) {
      pageWidget.dataset.state = "ready";
      setText(pageWidget, "total", formatNumber(site.views || 0));
      setText(pageWidget, "page", formatNumber(page.views || 0));
      setText(pageWidget, "average", formatDuration(page.averageActiveSeconds || 0));
    }

    for (const el of inlineMetricEls) {
      const path = canonicalPath(el.dataset.metricPath || "");
      const item = pages[path] || {};
      el.dataset.state = "ready";
      setText(el, "views", formatNumber(item.views || 0));
      setText(el, "average", formatDuration(item.averageActiveSeconds || 0));
    }
  }

  function setText(root, field, value) {
    const target = root.querySelector(`[data-metric-field="${field}"]`);
    if (target) {
      target.textContent = value;
    }
  }

  function insertPageWidget() {
    if (document.querySelector("[data-public-metrics-widget]")) {
      return document.querySelector("[data-public-metrics-widget]");
    }
    const isReview = document.body.classList.contains("public-review");
    const widget = document.createElement("aside");
    widget.className = "public-metrics";
    widget.dataset.publicMetricsWidget = "true";
    widget.dataset.state = "loading";
    widget.setAttribute("aria-live", "polite");
    if (isReview && isEnglish) {
      widget.setAttribute("aria-label", "Public review metrics");
      widget.innerHTML = `<span class="public-metrics-pill"><strong data-metric-field="page">-</strong> review views</span>
         <span class="public-metrics-pill">Average reading time <strong data-metric-field="average">-</strong></span>
         <span class="public-metrics-pill"><strong data-metric-field="total">-</strong> total hub views</span>`;
    } else if (isReview) {
      widget.setAttribute("aria-label", "공개 리뷰 조회 통계");
      widget.innerHTML = `<span class="public-metrics-pill"><strong data-metric-field="page">-</strong> 이 리뷰 조회</span>
         <span class="public-metrics-pill">평균 읽은 시간 <strong data-metric-field="average">-</strong></span>
         <span class="public-metrics-pill"><strong data-metric-field="total">-</strong> 리뷰 허브 전체 조회</span>`;
    } else {
      widget.innerHTML = `<span class="public-metrics-pill"><strong data-metric-field="page">-</strong> 허브 조회</span>
         <span class="public-metrics-pill">평균 읽은 시간 <strong data-metric-field="average">-</strong></span>`;
    }

    if (isReview) {
      const topline = document.querySelector(".topline");
      if (topline) {
        topline.insertAdjacentElement("afterend", widget);
      } else {
        document.body.insertBefore(widget, document.body.firstChild);
      }
      return widget;
    }

    const search = document.querySelector(".top-search");
    if (search) {
      search.insertAdjacentElement("afterend", widget);
      return widget;
    }
    const stats = document.querySelector(".hero .stats");
    if (stats) {
      stats.insertAdjacentElement("afterend", widget);
      return widget;
    }
    return null;
  }

  function startEngagementTracking() {
    const IDLE_TIMEOUT_MS = 2 * 60 * 1000;
    const MAX_SESSION_ACTIVE_MS = 45 * 60 * 1000;
    let lastTick = performance.now();
    let lastInteractionAt = lastTick;
    let windowFocused = document.hasFocus ? document.hasFocus() : true;
    let activeMs = 0;
    let sessionActiveMs = 0;
    let maxScrollPercent = getScrollPercent();
    let lastReportedScrollPercent = 0;

    const markInteraction = () => {
      const now = performance.now();
      if (now - lastInteractionAt > 1000) {
        lastInteractionAt = now;
      }
    };

    const tick = () => {
      const now = performance.now();
      const visible = document.visibilityState === "visible";
      const focused = document.hasFocus ? document.hasFocus() : windowFocused;
      const recentlyActive = now - lastInteractionAt <= IDLE_TIMEOUT_MS;
      if (visible && windowFocused && focused && recentlyActive && sessionActiveMs < MAX_SESSION_ACTIVE_MS) {
        const delta = Math.max(0, now - lastTick);
        const allowed = Math.min(delta, MAX_SESSION_ACTIVE_MS - sessionActiveMs);
        activeMs += allowed;
        sessionActiveMs += allowed;
      }
      lastTick = now;
      maxScrollPercent = Math.max(maxScrollPercent, getScrollPercent());
    };

    const flush = (keepalive) => {
      tick();
      const activeSeconds = Math.floor(activeMs / 1000);
      const scroll = Math.round(maxScrollPercent);
      const hasActiveTime = activeSeconds >= 5;
      const hasNewScrollDepth = scroll >= 25 && scroll > lastReportedScrollPercent;
      if (!hasActiveTime && !hasNewScrollDepth) {
        return;
      }
      activeMs = 0;
      lastReportedScrollPercent = Math.max(lastReportedScrollPercent, scroll);
      maxScrollPercent = getScrollPercent();

      const payload = { path: pagePath, activeSeconds, maxScrollPercent: scroll };
      if (keepalive && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon(endpoint + "/engagement", blob);
        return;
      }
      postJson("/engagement", payload, keepalive).catch(() => {});
    };

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") {
        flush(true);
      } else {
        markInteraction();
        lastTick = performance.now();
      }
    });
    window.addEventListener("blur", () => {
      flush(true);
      windowFocused = false;
      lastTick = performance.now();
    });
    window.addEventListener("focus", () => {
      windowFocused = true;
      markInteraction();
      lastTick = performance.now();
    });
    window.addEventListener("pagehide", () => flush(true));
    window.addEventListener("scroll", () => {
      markInteraction();
      maxScrollPercent = Math.max(maxScrollPercent, getScrollPercent());
    }, { passive: true });
    window.addEventListener("pointerdown", markInteraction, { passive: true });
    window.addEventListener("pointermove", markInteraction, { passive: true });
    window.addEventListener("wheel", markInteraction, { passive: true });
    window.addEventListener("touchstart", markInteraction, { passive: true });
    window.addEventListener("keydown", markInteraction);
    window.setInterval(() => flush(false), 15000);
  }

  function getScrollPercent() {
    const doc = document.documentElement;
    const body = document.body;
    const scrollTop = window.scrollY || doc.scrollTop || body.scrollTop || 0;
    const scrollHeight = Math.max(body.scrollHeight, doc.scrollHeight);
    const viewport = window.innerHeight || doc.clientHeight || 0;
    if (scrollHeight <= viewport) {
      return 100;
    }
    return Math.min(100, Math.max(0, ((scrollTop + viewport) / scrollHeight) * 100));
  }

  function formatNumber(value) {
    return new Intl.NumberFormat(locale).format(Number(value || 0));
  }

  function formatDuration(seconds) {
    const value = Number(seconds || 0);
    if (value <= 0) {
      return "-";
    }
    if (value < 60) {
      return isEnglish ? `${value}s` : `${value}초`;
    }
    return isEnglish ? `${Math.round(value / 60)} min` : `${Math.round(value / 60)}분`;
  }
})();
"""


SITE_JS = (HUB_ASSET_SOURCE_DIR / "hub.js").read_text(encoding="utf-8")


def load_existing_manifest() -> dict[str, dict[str, object]]:
    manifest_path = SITE_DIR / "manifest.json"
    if not manifest_path.exists():
        return {}
    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw_manifest, list):
        raise ValueError(f"Expected a list in {manifest_path}")
    return {
        str(item["folder"]): item
        for item in raw_manifest
        if isinstance(item, dict) and item.get("folder")
    }


def load_existing_category_order() -> list[str]:
    index_path = SITE_DIR / "index.html"
    if not index_path.exists():
        return []
    text = index_path.read_text(encoding="utf-8")
    categories: list[str] = []
    for value in re.findall(r'<option\s+value="([^"]+)">', text, flags=re.IGNORECASE):
        category = html.unescape(value).strip()
        if category and category not in categories:
            categories.append(category)
    return categories


def page_specs(item: dict[str, object]) -> list[tuple[str, str]]:
    specs = [(str(item["href"]), "ko")]
    translations = item.get("translations") or []
    if isinstance(translations, list):
        for translation in translations:
            if not isinstance(translation, dict):
                continue
            href = str(translation.get("href") or "")
            language = str(translation.get("language") or "").lower()
            if href and language:
                specs.append((href, language))
    return specs


def validate_local_references(
    document_path: Path,
    text: str,
    sparse_tracked_paths: set[Path] | None = None,
) -> list[str]:
    errors: list[str] = []
    for match in LOCAL_REF_RE.finditer(text):
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            continue
        local_path = split_local_url(raw_url)[0]
        if local_path:
            resolved_path = (document_path.parent / local_path).resolve()
            if resolved_path.exists() or resolved_path in (sparse_tracked_paths or set()):
                continue
        errors.append(f"missing local href/src/poster in {document_path}: {raw_url}")
    return errors


def disclosure_field(
    disclosure: DisclosureMetadataParser,
    labels: tuple[str, ...],
) -> tuple[str, str]:
    normalized_labels = {label.casefold() for label in labels}
    for label, value in disclosure.fields.items():
        if label.casefold() in normalized_labels:
            return label, value
    return "", ""


def validate_disclosure(review_index: Path, text: str) -> list[str]:
    errors: list[str] = []
    disclosure = DisclosureMetadataParser()
    disclosure.feed(text)
    required_fields = {
        "responsible editor": ("Responsible editor", "책임 편집자"),
        "AI system": ("AI system", "AI 시스템"),
        "editorial harness": ("Editorial harness", "편집 하네스"),
        "evidence cutoff": ("Evidence cutoff", "근거 기준일"),
    }
    observed: dict[str, tuple[str, str]] = {}
    for field_name, labels in required_fields.items():
        observed[field_name] = disclosure_field(disclosure, labels)
        if not observed[field_name][1].strip():
            errors.append(f"missing disclosure field in {review_index}: {field_name}")

    cutoff = observed["evidence cutoff"][1]
    cutoff_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", cutoff)
    if cutoff and not cutoff_match:
        errors.append(f"invalid evidence cutoff in {review_index}: {cutoff!r}")
    elif cutoff_match:
        try:
            date.fromisoformat(cutoff_match.group(0))
        except ValueError:
            errors.append(f"invalid evidence cutoff in {review_index}: {cutoff!r}")

    harness_label = observed["editorial harness"][0]
    methods_index = (SITE_DIR / EDITORIAL_METHODS_HREF / "index.html").resolve()
    method_link_found = False
    for href in disclosure.field_links.get(harness_label, []):
        if is_external_or_anchor(href):
            if href.rstrip("/") == f"{PUBLIC_BASE_URL}{EDITORIAL_METHODS_HREF}".rstrip("/"):
                method_link_found = True
            continue
        local_path = split_local_url(href)[0]
        resolved = (review_index.parent / local_path).resolve()
        if resolved.is_dir():
            resolved /= "index.html"
        if resolved == methods_index:
            method_link_found = True
    if not method_link_found:
        errors.append(f"missing public method link in disclosure: {review_index}")
    return errors


def validate_public_support_files(
    public_dir: Path, *, review: PublicReview | None = None, language: str = "ko",
) -> list[str]:
    errors: list[str] = []
    video_names = approved_video_assets(review, language)
    if not public_dir.exists():
        return errors
    for support_path in sorted(public_dir.iterdir(), key=lambda path: path.name.lower()):
        if support_path.is_file() and (
            support_path.suffix.lower() in {".mp4", ".vtt"}
            or support_path.name.startswith("noether-abstract-")
        ):
            if support_path.name not in video_names.values():
                errors.append(f"unapproved video asset in public output: {support_path.name}")
                continue
            try:
                if support_path.suffix.lower() in {".txt", ".vtt"}:
                    validate_video_text(support_path)
                else:
                    validate_video_binary(support_path)
            except (OSError, ValueError) as error:
                errors.append(str(error))
            continue
        if (
            not support_path.is_file()
            or support_path.name == "index.html"
            or support_path.suffix.lower() not in PUBLIC_TEXT_FILE_SUFFIXES
        ):
            continue
        try:
            support_text = support_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"public text support file is not UTF-8: {support_path}")
            continue
        for risk in public_text_risks(support_text):
            errors.append(f"{risk} left in public support file: {support_path}")
    return errors


def validate_public_page(
    href: str,
    expected_language: str,
    expected_alternates: dict[str, str],
    expected_title: str = "",
    sparse_tracked_paths: set[Path] | None = None,
    review: PublicReview | None = None,
) -> list[str]:
    errors: list[str] = []
    review_index = SITE_DIR / href
    if not review_index.exists():
        return [f"missing review index: {review_index}"]

    text = review_index.read_text(encoding="utf-8")
    errors.extend(validate_local_references(review_index, text, sparse_tracked_paths))
    try:
        validate_video_embed(text, review_index.parent, review, expected_language)
    except (OSError, ValueError) as error:
        errors.append(f"invalid video embed in {review_index}: {error}")

    if "data-missing-ref=" in text.lower():
        errors.append(f"data-missing-ref left in {review_index}")
    if "data-blocked-ref=" in text.lower():
        errors.append(f"data-blocked-ref left in {review_index}")
    if "data-local-ref=" in text.lower():
        errors.append(f"data-local-ref left in {review_index}")
    for risk in public_text_risks(text):
        errors.append(f"{risk} left in {review_index}")

    metadata = PageMetadataParser()
    metadata.feed(text)
    for link in metadata.hrefs:
        parts = urlsplit(html.unescape(link))
        if parts.scheme or parts.netloc or parts.path or not parts.fragment:
            continue
        fragment = unquote(parts.fragment)
        if fragment not in metadata.ids:
            errors.append(f"missing local fragment in {review_index}: #{fragment}")
    if metadata.html_lang != expected_language:
        errors.append(
            f"unexpected html lang in {review_index}: {metadata.html_lang!r} != {expected_language!r}"
        )
    if not metadata.has_hub_link:
        errors.append(f"missing review-hub link in {review_index}")
    if not metadata.has_authoring_disclosure:
        errors.append(f"missing authoring disclosure in {review_index}")
    else:
        errors.extend(validate_disclosure(review_index, text))
    if expected_title:
        observed_titles = {
            "title": metadata.title_text,
            "og:title": metadata.og_title,
            "h1": metadata.h1_text,
        }
        for label, observed in observed_titles.items():
            if observed != expected_title:
                errors.append(
                    f"title mismatch in {review_index} ({label}): "
                    f"{observed!r} != {expected_title!r}"
                )
    else:
        display_title = metadata.h1_text or metadata.title_text
        if not display_title:
            errors.append(f"missing display title in {review_index}")
        elif metadata.og_title != display_title:
            errors.append(
                f"title mismatch in {review_index} (og:title): "
                f"{metadata.og_title!r} != {display_title!r}"
            )
    if re.search(r"<td[^>]*>\s*\$\s*</td>", text, flags=re.IGNORECASE):
        errors.append(f"broken table cell containing only a dollar sign in {review_index}")

    expected_canonical = public_url_for_href(href)
    if metadata.canonical_urls != [expected_canonical]:
        errors.append(
            f"unexpected canonical in {review_index}: "
            f"{metadata.canonical_urls!r} != {[expected_canonical]!r}"
        )
    if expected_alternates:
        for language, expected_url in expected_alternates.items():
            if metadata.alternates.get(language) != expected_url:
                errors.append(
                    f"unexpected hreflang {language} in {review_index}: "
                    f"{metadata.alternates.get(language)!r} != {expected_url!r}"
                )
        if expected_language not in metadata.current_languages:
            errors.append(f"missing visible current-language marker in {review_index}: {expected_language}")
        for language, expected_url in expected_alternates.items():
            if language in {"x-default", expected_language}:
                continue
            if metadata.language_links.get(language) != expected_url:
                errors.append(
                    f"missing visible {language} language switch in {review_index}: {expected_url}"
                )
    return errors


def validate_manifest_disclosure(item: dict[str, object]) -> list[str]:
    errors: list[str] = []
    folder = str(item.get("folder") or "unknown review")
    disclosure = item.get("disclosure")
    if not isinstance(disclosure, dict):
        return [f"missing manifest disclosure: {folder}"]
    editor = disclosure.get("responsible_editor")
    ai_assistance = disclosure.get("ai_assistance")
    harness = disclosure.get("harness")
    verification = disclosure.get("verification")
    if not isinstance(editor, dict) or not any(
        str(editor.get(key) or "").strip() for key in ("name_ko", "name_en")
    ):
        errors.append(f"missing manifest responsible editor: {folder}")
    if not isinstance(ai_assistance, dict) or not any(
        str(ai_assistance.get(key) or "").strip() for key in ("system", "system_ko")
    ):
        errors.append(f"missing manifest AI system: {folder}")
    if (
        not isinstance(harness, dict)
        or not str(harness.get("name") or "").strip()
        or str(harness.get("methods") or "").strip() != EDITORIAL_METHODS_HREF
    ):
        errors.append(f"missing manifest harness/method link: {folder}")
    cutoff = str(verification.get("evidence_cutoff") or "") if isinstance(verification, dict) else ""
    try:
        date.fromisoformat(cutoff)
    except ValueError:
        errors.append(f"missing or invalid manifest evidence cutoff: {folder}")
    return errors


def validate_methods_page(sparse_tracked_paths: set[Path]) -> list[str]:
    methods_index = SITE_DIR / EDITORIAL_METHODS_HREF / "index.html"
    if not methods_index.exists():
        return [f"missing methods index: {methods_index}"]
    text = methods_index.read_text(encoding="utf-8")
    errors = validate_local_references(methods_index, text, sparse_tracked_paths)
    metadata = PageMetadataParser()
    metadata.feed(text)
    expected_canonical = f"{PUBLIC_BASE_URL}{EDITORIAL_METHODS_HREF}"
    if metadata.canonical_urls != [expected_canonical]:
        errors.append(
            f"unexpected canonical in {methods_index}: "
            f"{metadata.canonical_urls!r} != {[expected_canonical]!r}"
        )
    for risk in public_text_risks(text):
        errors.append(f"{risk} left in {methods_index}")
    return errors


def validate_public_site(manifest: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    sparse_tracked_paths: set[Path] = set()
    sparse_listing = subprocess.run(
        ["git", "ls-files", "-t", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if sparse_listing.returncode == 0:
        for raw_entry in sparse_listing.stdout.split(b"\0"):
            if not raw_entry.startswith(b"S "):
                continue
            relative_path = raw_entry[2:].decode("utf-8", errors="surrogateescape")
            sparse_tracked_paths.add((ROOT / relative_path).resolve())
    for item in manifest:
        registered_review = next((review for review in REVIEWS if review.folder == item.get("folder")), None)
        errors.extend(validate_manifest_disclosure(item))
        specs = page_specs(item)
        expected_alternates: dict[str, str] = {}
        if len(specs) > 1:
            expected_alternates = {
                language: public_url_for_href(href) for href, language in specs
            }
            expected_alternates["x-default"] = public_url_for_href(str(item["href"]))
        for href, language in specs:
            expected_title = str(item["title"]) if language == "ko" else ""
            errors.extend(
                validate_public_page(
                    href,
                    language,
                    expected_alternates,
                    expected_title,
                    sparse_tracked_paths,
                    registered_review,
                )
            )
            errors.extend(validate_public_support_files(
                (SITE_DIR / href).parent, review=registered_review, language=language,
            ))
    errors.extend(validate_methods_page(sparse_tracked_paths))
    errors.extend(validate_archive(SITE_DIR))
    archive_manifest = SITE_DIR / "archive-manifest.json"
    if archive_manifest.exists():
        for doc in json.loads(archive_manifest.read_text(encoding="utf-8"))["documents"]:
            if not doc.get("study_href"):
                continue
            study_root = SITE_DIR / doc["study_href"]
            study_index = study_root / "index.html"
            if study_index.exists():
                text = study_index.read_text(encoding="utf-8")
                errors.extend(validate_local_references(study_index, text, sparse_tracked_paths))
            for name in doc.get("study_assets", {}):
                path = study_root / name
                if path.is_file() and path.suffix in {".html", ".css", ".svg", ".json", ".py", ".txt"}:
                    errors.extend(f"{risk} left in lecture asset {name}" for risk in public_text_risks(path.read_text(encoding="utf-8")))
    for archive_page in (SITE_DIR / "archive/index.html", SITE_DIR / "archive/en/index.html",
                         SITE_DIR / "lectures/index.html", SITE_DIR / "lectures/en/index.html",
                         SITE_DIR / "briefings/index.html", SITE_DIR / "briefings/en/index.html"):
        if archive_page.exists():
            archive_text = archive_page.read_text(encoding="utf-8")
            errors.extend(validate_local_references(archive_page, archive_text, sparse_tracked_paths))
            errors.extend(f"{risk} left in {archive_page}" for risk in public_text_risks(archive_text))
    site_index = SITE_DIR / "index.html"
    if not site_index.exists():
        errors.append(f"missing site index: {site_index}")
        return errors
    index_text = site_index.read_text(encoding="utf-8")
    for risk in public_text_risks(index_text):
        errors.append(f"{risk} left in {site_index}")
    singleton_patterns = {
        "public metrics stylesheet": r"assets/public-metrics\.css",
        "favicon": r"favicon\.ico",
        "SVG favicon": r"ai-tech-review-icon\.svg",
        "apple-touch icon": r"apple-touch-icon\.png",
    }
    head_match = re.search(r"<head\b[^>]*>(.*?)</head>", index_text, flags=re.IGNORECASE | re.DOTALL)
    index_head = head_match.group(1) if head_match else index_text
    for label, pattern in singleton_patterns.items():
        count = len(re.findall(pattern, index_head, flags=re.IGNORECASE))
        if count != 1:
            errors.append(f"unexpected {label} count in {site_index}: {count}")
    metrics_script_count = len(re.findall(r"assets/public-metrics\.js", index_text, flags=re.IGNORECASE))
    metrics_config_count = len(re.findall(r"window\.AI_TECH_REVIEW_METRICS\s*=", index_text, flags=re.IGNORECASE))
    if metrics_script_count not in {0, 1} or metrics_config_count != metrics_script_count:
        errors.append(
            f"public metrics script/config must be absent together or appear once in {site_index}: "
            f"script={metrics_script_count}, config={metrics_config_count}"
        )
    for required in (
        f'<link rel="canonical" href="{HUB_PUBLIC_URL}">',
        '<meta property="og:title" content="AI Tech Review Letters">',
        '<meta name="twitter:card" content="summary_large_image">',
        'href="methods/"',
    ):
        if required not in index_text:
            errors.append(f"missing homepage metadata or methods link: {required}")
    english_index = SITE_DIR / "en/index.html"
    if not english_index.exists():
        errors.append("missing English homepage")
    else:
        english_text = english_index.read_text(encoding="utf-8")
        errors.extend(validate_local_references(english_index, english_text, sparse_tracked_paths))
        errors.extend(f"{risk} left in {english_index}" for risk in public_text_risks(english_text))
        for required in ('<html lang="en"', f'<link rel="canonical" href="{HUB_PUBLIC_URL}en/">', 'hreflang="ko"', 'hreflang="en"'):
            if required not in english_text:
                errors.append(f"missing English homepage metadata: {required}")
    return errors


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish the AI Tech Review static hub and registered review pages."
    )
    parser.add_argument(
        "--hub-only",
        action="store_true",
        help="Rebuild the hub and PDF archive while leaving published review files unchanged.",
    )
    parser.add_argument(
        "--review",
        action="append",
        default=[],
        metavar="SLUG",
        help=(
            "Publish only this registered review directory while preserving all other published "
            "review directories. May be repeated."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.hub_only and args.review:
        print("[public-site:error] --hub-only cannot be combined with --review")
        return 2
    selected_reviews = set(args.review)
    known_reviews = {review.folder: review for review in REVIEWS}
    unknown_reviews = sorted(selected_reviews - set(known_reviews))
    if unknown_reviews:
        for folder in unknown_reviews:
            print(f"[public-site:error] unknown review: {folder}")
        return 2

    preferred_category_order = load_existing_category_order() if selected_reviews or args.hub_only else []
    existing_manifest = load_existing_manifest()
    if args.hub_only and not existing_manifest:
        print("[public-site:error] --hub-only requires an existing published review manifest")
        return 2
    restore_published_analytics()

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    copy_icon_assets()

    manifest: list[dict[str, object]] = list(existing_manifest.values()) if args.hub_only else []
    for review in (() if args.hub_only else REVIEWS):
        if not selected_reviews or review.folder in selected_reviews:
            manifest.append(publish_review(review, existing_manifest.get(review.folder)))
            continue
        manifest.append(
            preserve_published_review(review, existing_manifest.get(review.folder))
        )
    manifest.sort(key=lambda item: str(item["date"]), reverse=True)

    def decorate_archive(text: str, prefix: str) -> str:
        return inject_cloudflare_web_analytics(inject_public_metrics(inject_public_icons(text, prefix), prefix))

    documents = publish_archive(ROOT / "archive", SITE_DIR, PUBLIC_BASE_URL, decorate_archive)
    for language, target, prefix in (("ko", SITE_DIR / "index.html", ""), ("en", SITE_DIR / "en/index.html", "../")):
        index_html = inject_public_icons(render_index(manifest, preferred_category_order, documents, language), prefix)
        index_html = inject_public_metrics(index_html, prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(inject_cloudflare_web_analytics(index_html), encoding="utf-8")
    (SITE_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS_DIR / "site.css").write_text(SITE_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "public-metrics.css").write_text(PUBLIC_METRICS_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "public-metrics.js").write_text(PUBLIC_METRICS_JS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "site.js").write_text(SITE_JS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "hub-preferences.js").write_text(HUB_PREFERENCES_JS.strip() + "\n", encoding="utf-8")

    enrich_reader_engagement(SITE_DIR)
    validate_reader_artifact(SITE_DIR)

    errors = validate_public_site(manifest)
    if errors:
        for error in errors:
            print(f"[public-site:error] {error}")
        return 2

    print(f"[public-site] {SITE_DIR}")
    print(f"[public-site] reviews={len(manifest)}")
    print(f"[public-site] archive_documents={len(documents)}")
    for item in manifest:
        print(f"[review] {item['href']}")
    print("[public-site-check] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
