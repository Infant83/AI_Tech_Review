from __future__ import annotations

import argparse
import html
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


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
REVIEWS_DIR = SITE_DIR / "reviews"
ASSETS_DIR = SITE_DIR / "assets"
ICON_SOURCE_DIR = ROOT / ".automation" / "assets" / "federlicht-icon" / "generated"
ICON_ASSET_VERSION = "20260523-federlicht"
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
    r"(?P<prefix>\b(?:src|href)=['\"])(?P<url>[^'\"]+)(?P<suffix>['\"])",
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
PUBLIC_TEXT_FILE_SUFFIXES = {".svg", ".css", ".js", ".md", ".txt", ".json", ".csv", ".py", ".html"}
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
CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV = "CLOUDFLARE_WEB_ANALYTICS_TOKEN"
PUBLIC_METRICS_ENDPOINT_ENV = "INFANT83_PUBLIC_METRICS_ENDPOINT"
LEGACY_PUBLIC_METRICS_ENDPOINT_ENV = "AI_TECH_REVIEW_PUBLIC_METRICS_ENDPOINT"
DEFAULT_PUBLIC_METRICS_ENDPOINT = "https://infant83-public-metrics.infant83.workers.dev"
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
    r"\s*<link\b(?=[^>]*\bhref=['\"](?:data:,|[^'\"]*(?:favicon\.ico|federlicht-favicon\.svg|apple-touch-icon\.png)(?:\?[^'\"]*)?)['\"])[^>]*>",
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


def unpublished_local_text_reference(fragment: str) -> bool:
    for match in LOCAL_HREF_RE.finditer(fragment):
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            continue
        local_path = split_local_url(raw_url)[0]
        suffix = Path(local_path).suffix.lower()
        if suffix in {".md", ".txt", ".json", ".csv", ".py"}:
            return True
        if suffix == ".html" and Path(local_path).name.lower() != "index.html":
            return True
    return False


def strip_private_public_material(html_text: str, language: str) -> str:
    def strip_list_item(match: re.Match[str]) -> str:
        item = match.group(0)
        if PRIVATE_MESSAGE_METADATA_RE.search(item) or unpublished_local_text_reference(item):
            return ""
        return item

    def strip_anchor(match: re.Match[str]) -> str:
        anchor = match.group(0)
        if not unpublished_local_text_reference(anchor):
            return anchor
        label = "private working file omitted" if language.lower().startswith("en") else "비공개 작업 파일 생략"
        return f'<span class="private-source-omitted">{label}</span>'

    stripped = HTML_LIST_ITEM_RE.sub(strip_list_item, html_text)
    return HTML_ANCHOR_RE.sub(strip_anchor, stripped)


def inject_public_local_note(html_text: str, language: str) -> str:
    html_text = PUBLIC_LOCAL_NOTE_RE.sub("\n", html_text)
    if language.lower().startswith("en"):
        public_note = (
            "\n<section id=\"public-local-references\" class=\"public-note\">"
            "<p>This public HTML includes the article, figures, and public external references. "
            "Private working notes and message metadata are not published.</p>"
            "<p class=\"metrics-disclosure\">Public views and average reading time are recorded only "
            "as aggregate values by page path, without personal identifiers.</p>"
            "</section>\n"
        )
    else:
        public_note = (
            "\n<section id=\"public-local-references\" class=\"public-note\">"
            "<p>공개 HTML에는 본문, 그림과 공개 외부 참고 링크만 포함합니다. "
            "비공개 작업 메모와 메시지 메타데이터는 게시하지 않습니다.</p>"
            "<p class=\"metrics-disclosure\">공개 조회수와 평균 읽은 시간은 개인 식별 정보 없이 "
            "페이지 경로 단위의 집계값으로만 기록합니다.</p>"
            "</section>\n"
        )
    if "</body>" in html_text:
        return html_text.replace("</body>", public_note + "</body>")
    return html_text


def public_asset_names(values: Iterable[object]) -> list[str]:
    return sorted(
        {
            str(value)
            for value in values
            if Path(str(value)).suffix.lower() in PUBLIC_REVIEW_FILE_SUFFIXES
        }
    )


def prune_public_support_files(public_dir: Path) -> None:
    if not public_dir.exists():
        return
    for support_path in public_dir.iterdir():
        if not support_path.is_file() or support_path.name == "index.html":
            continue
        if support_path.suffix.lower() not in PUBLIC_REVIEW_FILE_SUFFIXES:
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
    if SMARTY_ENTITY_IN_MATH_RE.search(text):
        risks.append("smart-quote entity inside math")
    if re.search(r"W(?:&rsquo;|')?\s*<em\b", text, flags=re.IGNORECASE):
        risks.append("markdown emphasis inside math")
    return list(dict.fromkeys(risks))


def copy_public_file(source_path: Path, dest_path: Path) -> None:
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


def public_icon_links(asset_prefix: str = "", indent: int = 4) -> str:
    pad = " " * indent
    version = f"?v={ICON_ASSET_VERSION}"
    prefix = html.escape(asset_prefix, quote=True)
    return (
        f"\n{pad}<!-- AI Tech Review Icons -->"
        f"\n{pad}<link rel=\"icon\" href=\"{prefix}favicon.ico{version}\" sizes=\"any\">"
        f"\n{pad}<link rel=\"icon\" href=\"{prefix}assets/federlicht-favicon.svg{version}\" type=\"image/svg+xml\">"
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

    def replace_ref(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            return match.group(0)

        local_path, query, fragment = split_local_url(raw_url)
        if not local_path:
            return match.group(0)

        source_path = (dist_dir / local_path).resolve()
        suffix = source_path.suffix.lower()

        try:
            source_path.relative_to(dist_root)
        except ValueError:
            safe_url = html.escape(raw_url, quote=True)
            return f'data-blocked-ref="{safe_url}"'

        if suffix not in PUBLIC_REVIEW_FILE_SUFFIXES:
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

    sanitized = strip_private_public_material(html_text, language)
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


def copy_public_support_files(dist_dir: Path, public_dir: Path, copied: list[str]) -> list[str]:
    del dist_dir, public_dir
    return public_asset_names(copied)


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
    copied_assets = copy_public_support_files(dist_index.parent, public_dir, copied_assets)
    return public_html, copied_assets


def refresh_existing_public_variant(
    review: PublicReview,
    public_dir: Path,
    language: str,
) -> str:
    index_path = public_dir / "index.html"
    existing_html = index_path.read_text(encoding="utf-8")
    asset_prefix = asset_prefix_for_public_dir(public_dir)
    refreshed = strip_private_public_material(existing_html, language)
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
    prune_public_support_files(public_dir)
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
            assets = public_asset_names(prior.get("assets") or [])
        else:
            assets = public_asset_names(
                path.name
                for path in public_dir.iterdir()
                if path.is_file() and path.name != "index.html"
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
        copied_assets = public_asset_names(existing_entry.get("assets") or [])
    else:
        thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""
        copied_assets = public_asset_names(
            path.name
            for path in review.public_dir.iterdir()
            if path.is_file() and path.name != "index.html"
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
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in item["tags"])
    translation_badges = render_translation_badges(item)
    thumbnail = item.get("thumbnail") or ""
    image_html = (
        f'<img src="{html.escape(str(thumbnail), quote=True)}" alt="{html.escape(str(item["title"]), quote=True)} 대표 이미지" loading="lazy">'
        if thumbnail
        else '<div class="thumb-placeholder" aria-hidden="true"></div>'
    )
    return f"""
        <article class="review-card" data-category="{html.escape(str(item["category"]), quote=True)}" data-tags="{html.escape(" ".join(item["tags"]), quote=True)}" data-title="{html.escape(str(item["title"]), quote=True)}" data-metric-path="{html.escape(str(item["metric_path"]), quote=True)}">
          <a class="thumb" href="{html.escape(str(item["href"]), quote=True)}">{image_html}</a>
          <div class="review-card-body">
            <p class="meta">{html.escape(str(item["category"]))} · {html.escape(str(item["updated"]))}{translation_badges}</p>
            <h3><a href="{html.escape(str(item["href"]), quote=True)}">{html.escape(str(item["title"]))}</a></h3>
            <p class="subtitle">{html.escape(str(item["subtitle"]))}</p>
            <p class="card-metrics" data-inline-metrics data-metric-path="{html.escape(str(item["metric_path"]), quote=True)}">
              <span><strong data-metric-field="views">-</strong> 조회</span>
              <span>평균 <strong data-metric-field="average">-</strong></span>
            </p>
            <p>{html.escape(str(item["summary"]))}</p>
            <div class="tags">{tags}</div>
          </div>
        </article>
    """.rstrip()


def render_latest_update(item: dict[str, object]) -> str:
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in item["tags"][:4])
    translation_badges = render_translation_badges(item)
    thumbnail = item.get("thumbnail") or ""
    image_html = (
        f'<img src="{html.escape(str(thumbnail), quote=True)}" alt="{html.escape(str(item["title"]), quote=True)} 대표 이미지" loading="eager">'
        if thumbnail
        else '<div class="thumb-placeholder" aria-hidden="true"></div>'
    )
    return f"""
      <section class="latest-update" aria-labelledby="latest-heading">
        <div class="latest-copy">
          <p class="section-kicker">Latest update</p>
          <h2 id="latest-heading">{html.escape(str(item["title"]))}</h2>
          <p class="latest-subtitle">{html.escape(str(item["subtitle"]))}</p>
          <p>{html.escape(str(item["summary"]))}</p>
          <p class="latest-metrics" data-inline-metrics data-metric-path="{html.escape(str(item["metric_path"]), quote=True)}">
            <span><strong data-metric-field="views">-</strong> 조회</span>
            <span>평균 읽은 시간 <strong data-metric-field="average">-</strong></span>
          </p>
          <div class="tags">{tags}</div>
          <a class="text-link" href="{html.escape(str(item["href"]), quote=True)}">최신 리뷰 읽기</a>{translation_badges}
        </div>
        <a class="latest-media" href="{html.escape(str(item["href"]), quote=True)}">{image_html}</a>
      </section>
    """.rstrip()


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
) -> str:
    updated = date.today().isoformat()
    available_categories = {str(item["category"]) for item in manifest}
    categories = [
        category
        for category in (preferred_category_order or [])
        if category in available_categories
    ]
    categories.extend(sorted(available_categories - set(categories)))
    category_options = "\n".join(f'<option value="{html.escape(category)}">{html.escape(category)}</option>' for category in categories)
    category_chips = render_category_chips(categories)
    cards = "\n".join(render_review_card(item) for item in manifest)
    latest = render_latest_update(manifest[0]) if manifest else ""
    home_description = "AI, 과학, 에이전트, 제조 데이터, 거버넌스를 원문과 근거 경계로 검증하는 공개 기술 리뷰 허브"
    latest_thumbnail = str(manifest[0].get("thumbnail") or "") if manifest else ""
    home_image = f"{PUBLIC_BASE_URL}{latest_thumbnail}" if latest_thumbnail else ""
    home_image_meta = (
        f'\n    <meta property="og:image" content="{html.escape(home_image, quote=True)}">'
        f'\n    <meta property="og:image:alt" content="AI Tech Review Letters 최신 리뷰 대표 이미지">'
        f'\n    <meta name="twitter:image" content="{html.escape(home_image, quote=True)}">'
        if home_image
        else ""
    )

    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Tech Review Letters</title>
    <meta name="description" content="{html.escape(home_description, quote=True)}">
    <link rel="canonical" href="{PUBLIC_BASE_URL}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="AI Tech Review Letters">
    <meta property="og:title" content="AI Tech Review Letters">
    <meta property="og:description" content="{html.escape(home_description, quote=True)}">
    <meta property="og:url" content="{PUBLIC_BASE_URL}">{home_image_meta}
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="AI Tech Review Letters">
    <meta name="twitter:description" content="{html.escape(home_description, quote=True)}">
    <link rel="stylesheet" href="assets/site.css">
  </head>
  <body>
    <header class="site-header">
      <nav class="topbar" aria-label="주요 링크">
        <div class="topbar-left">
          <a class="brand" href="index.html">AI Tech Review Letters</a>
          <label class="top-search">
            <span class="sr-only">리뷰 검색</span>
            <input id="search" type="search" placeholder="검색: AI scientist, TabPFN, agent..." autocomplete="off">
          </label>
          <aside class="public-metrics topbar-metrics" data-public-metrics-widget data-state="loading" aria-live="polite" aria-label="허브 조회 통계">
            <span class="public-metrics-pill"><strong data-metric-field="page">-</strong> 허브 조회</span>
            <span class="public-metrics-pill">평균 읽은 시간 <strong data-metric-field="average">-</strong></span>
          </aside>
        </div>
        <span class="topbar-links">
          <a href="https://infant83.github.io/">김현중</a>
          <a href="methods/">작성·검증 원칙</a>
          <a href="manifest.json">데이터</a>
        </span>
      </nav>
      <section class="hero">
        <p class="eyebrow">Public report hub · {updated}</p>
        <h1>Enlighten your AI Technology Insight.</h1>
        <p class="lead">AI for Science, frontier models, agent systems, materials AI를 원문 링크와 함께 다시 읽는 공개 리뷰 허브입니다.</p>
        <div class="stats" aria-label="허브 요약">
          <a href="#review-grid" class="stat-link" data-category-filter=""><strong>{len(manifest)}</strong> 공개 리뷰</a>
          <a href="#topic-filter" class="stat-link"><strong>{len(categories)}</strong> 주제 묶음</a>
        </div>
      </section>
    </header>

    <main>
      {latest}

      <section class="topic-filter" id="topic-filter" aria-label="주제별 리뷰 찾기">
        <div class="filter-heading">
          <div>
            <p class="section-kicker">Browse by topic</p>
            <h2>주제별 리뷰</h2>
          </div>
          <label class="category-select">
            <span>주제 선택</span>
            <select id="category">
              <option value="">전체</option>
              {category_options}
            </select>
          </label>
        </div>
        <div class="category-chips" aria-label="주제 빠른 선택">
          {category_chips}
        </div>
      </section>

      <section class="review-grid" id="review-grid" aria-live="polite">
        {cards}
      </section>

      <section class="transparency-notice" aria-labelledby="transparency-heading">
        <div>
          <p class="section-kicker">Human-owned · AI-assisted · source-audited</p>
          <h2 id="transparency-heading">작성·검증 공개</h2>
          <p class="operator"><a href="methods/">전체 작성 원칙과 하네스 보기</a></p>
        </div>
        <div class="notice-body">
          <dl class="credit-list">
            <div>
              <dt>책임 편집자</dt>
              <dd>
                <a href="https://infant83.github.io/">김현중</a>
                <span class="credit-links">
                  <a href="https://infant83.github.io/">Profile</a>
                  <a href="https://github.com/Infant83">GitHub</a>
                  <a href="https://www.linkedin.com/in/hyun-jung-kim-8126a7236/">LinkedIn</a>
                  <a href="https://scholar.google.com/citations?user=FtSLeT4AAAAJ&hl=en">Google Scholar</a>
                </span>
              </dd>
            </div>
            <div>
              <dt>AI 지원</dt>
              <dd>AI 시스템은 글별 공개 기록에 따릅니다. 이번 공개 보완은 OpenAI Codex Work Mode를 사용했으며, 미보존 역할·모델 정보는 추정하지 않습니다.</dd>
            </div>
          </dl>
          <ul>
            <li>사람이 연구 질문, 과학적 해석과 발행 책임을 맡고 AI 에이전트는 조사, 대조, 초안, 번역, 시각자료 설계와 게시 검사를 지원합니다.</li>
            <li>글마다 사용한 에이전트 역할, 검증 범위, 근거 기준일과 하네스 버전을 공개합니다. 기록이 남지 않은 세부 모델·에이전트 구성은 ‘미보존’으로 표시합니다.</li>
            <li>논문 보고 결과, 독립 검증, 리뷰 해석, 후속 제안을 구분하고 QPU·실험, 고전 시뮬레이션, 컴파일, 논리 자원 추정을 같은 증거 수준으로 섞지 않습니다.</li>
            <li>외부 출처의 저작권/라이선스는 원 저작권자에게 있으며, 재배포 전 원문 정책 확인이 필요합니다.</li>
            <li>고위험 의사결정(법률·의료·재무·규제)에는 원문 대조와 추가 검증 절차를 수행하세요.</li>
            <li class="metrics-disclosure">공개 조회수와 평균 읽은 시간은 개인 식별 정보 없이 페이지 경로 단위의 집계값으로만 기록합니다.</li>
          </ul>
        </div>
      </section>
    </main>

    <script src="assets/site.js"></script>
  </body>
</html>
"""


def copy_icon_assets() -> None:
    required = {
        "favicon.ico": SITE_DIR / "favicon.ico",
        "federlicht-favicon.svg": ASSETS_DIR / "federlicht-favicon.svg",
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


SITE_CSS = """
:root {
  --bg: #f6f7f4;
  --paper: #ffffff;
  --ink: #171b1f;
  --muted: #5c6670;
  --line: #d9ded8;
  --green: #0d7c66;
  --blue: #2357a5;
  --red: #a23645;
  --deep: #0d141b;
  --shadow: 0 18px 48px rgba(27, 36, 45, 0.10);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  line-height: 1.6;
}
h1, h2, h3, .lead, .subtitle, .review-card p, .latest-update p, .transparency-notice li {
  word-break: keep-all;
  overflow-wrap: break-word;
}
a { color: inherit; }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.site-header, main {
  width: min(1180px, calc(100% - 36px));
  margin: 0 auto;
}
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 22px;
  padding: 24px 0 18px;
  font-size: 14px;
  color: var(--muted);
}
.topbar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  min-width: 0;
  flex: 1;
}
.topbar-links {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  white-space: nowrap;
}
.brand {
  color: var(--ink);
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}
.top-search {
  width: min(360px, 42vw);
}
.topbar-left .public-metrics {
  flex: 0 0 auto;
  min-width: 0;
  margin: 0;
}
.topbar-left .public-metrics-pill {
  background: rgba(255, 255, 255, 0.72);
  min-height: 34px;
  padding: 7px 10px;
  white-space: nowrap;
}
.top-search input {
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
}
.hero {
  border-top: 5px solid var(--green);
  border-bottom: 1px solid var(--line);
  padding: 52px 0 34px;
}
.eyebrow {
  margin: 0 0 14px;
  color: var(--green);
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
h1 {
  max-width: 860px;
  margin: 0;
  font-size: clamp(34px, 6vw, 64px);
  line-height: 1.08;
  letter-spacing: 0;
}
.lead {
  max-width: 780px;
  margin: 22px 0 0;
  color: var(--muted);
  font-size: 18px;
}
.section-kicker {
  margin: 0 0 8px;
  color: var(--green);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}
.stat-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.65);
  padding: 10px 13px;
  font-size: 14px;
  text-decoration: none;
  transition: border-color 0.18s ease, background 0.18s ease, color 0.18s ease;
}
.stat-link:hover,
.stat-link:focus-visible {
  border-color: rgba(13, 124, 102, 0.55);
  background: #ffffff;
  color: var(--green);
}
.latest-update {
  display: grid;
  grid-template-columns: minmax(340px, 0.92fr) minmax(460px, 1.08fr);
  gap: 0;
  align-items: stretch;
  margin: 30px 0 26px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: var(--shadow);
  overflow: hidden;
}
.latest-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(24px, 4vw, 38px);
}
.latest-copy h2 {
  margin: 0 0 12px;
  max-width: 12.5em;
  font-size: 42px;
  line-height: 1.12;
  text-wrap: balance;
}
.latest-copy p {
  color: var(--muted);
}
.latest-subtitle {
  color: var(--ink) !important;
  font-weight: 800;
  max-width: 38em;
}
.latest-media {
  display: grid;
  min-height: 100%;
  background: #eef1ed;
  border-left: 1px solid var(--line);
}
.latest-media img {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 320px;
  object-fit: cover;
  object-position: center;
}
.latest-media img[src$=".svg"] {
  object-fit: contain;
  padding: clamp(12px, 2vw, 22px);
  background: #f8faf8;
}
.text-link {
  display: inline-flex;
  margin-top: 22px;
  color: var(--green);
  font-weight: 900;
  text-decoration: none;
}
.text-link:hover {
  color: var(--blue);
}
.topic-filter {
  display: grid;
  gap: 12px;
  margin: 30px 0 18px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.58);
}
.filter-heading {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
}
.filter-heading h2 {
  margin: 0;
  font-size: clamp(22px, 3vw, 32px);
}
.category-select {
  display: grid;
  gap: 6px;
  min-width: min(260px, 100%);
}
.category-select span,
.top-search span {
  font-size: 13px;
}
.category-select span {
  display: grid;
  gap: 6px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}
.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.category-chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #ffffff;
  color: var(--muted);
  padding: 8px 12px;
  font: inherit;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}
.category-chip:hover,
.category-chip:focus-visible,
.category-chip.active {
  border-color: rgba(13, 124, 102, 0.55);
  background: rgba(13, 124, 102, 0.08);
  color: var(--green);
}
input, select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  color: var(--ink);
  padding: 12px 13px;
  font: inherit;
}
input:focus, select:focus {
  outline: 3px solid rgba(13, 124, 102, 0.18);
  border-color: var(--green);
}
.review-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}
.review-card {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 0;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
.thumb {
  display: block;
  aspect-ratio: 16 / 10;
  background: #e8ece8;
}
.thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.thumb-placeholder {
  width: 100%;
  aspect-ratio: 16 / 10;
  background: linear-gradient(135deg, rgba(13,124,102,0.24), rgba(35,87,165,0.18));
}
.review-card-body {
  padding: 22px;
}
.meta {
  margin: 0 0 10px;
  color: var(--green);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.translation-badge {
  display: inline-flex;
  align-items: center;
  margin-left: 9px;
  padding: 3px 8px;
  border: 1px solid rgba(35, 87, 165, 0.34);
  border-radius: 999px;
  color: var(--blue);
  background: rgba(35, 87, 165, 0.06);
  font-size: 11px;
  font-weight: 800;
  line-height: 1.3;
  text-decoration: none;
  text-transform: none;
  letter-spacing: 0;
  vertical-align: middle;
}
.translation-badge:hover {
  border-color: var(--blue);
  background: rgba(35, 87, 165, 0.12);
}
h3 {
  margin: 0 0 10px;
  font-size: 21px;
  line-height: 1.25;
}
h3 a {
  text-decoration: none;
}
h3 a:hover {
  color: var(--blue);
}
.subtitle {
  color: var(--muted);
  font-weight: 700;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 18px;
}
.tags span {
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  padding: 4px 9px;
  font-size: 12px;
}
.transparency-notice {
  display: grid;
  grid-template-columns: minmax(220px, 0.85fr) minmax(0, 1.4fr);
  gap: 24px;
  margin: 46px 0 76px;
  padding: clamp(22px, 4vw, 34px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  background: var(--deep);
  color: #eaf0f3;
}
.transparency-notice h2 {
  margin: 0 0 14px;
  font-size: 24px;
}
.transparency-notice .operator {
  margin: 0;
  color: rgba(234, 240, 243, 0.72);
}
.transparency-notice a {
  color: #8bd8c6;
  font-weight: 800;
}
.transparency-notice ul {
  margin: 0;
  padding-left: 20px;
  color: rgba(234, 240, 243, 0.82);
}
.notice-body {
  display: grid;
  gap: 22px;
}
.credit-list {
  display: grid;
  gap: 12px;
  margin: 0;
  color: rgba(234, 240, 243, 0.86);
}
.credit-list div {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr);
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(234, 240, 243, 0.14);
}
.credit-list dt {
  color: rgba(234, 240, 243, 0.62);
  font-weight: 800;
}
.credit-list dd {
  margin: 0;
}
.credit-links {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: 8px;
}
.credit-links a {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.transparency-notice li + li {
  margin-top: 8px;
}
.public-note {
  max-width: 980px;
  margin: 52px auto 0;
  padding: 18px 24px;
  border-top: 1px solid rgba(0,0,0,0.12);
  color: #5c6670;
  font-size: 14px;
}
.metrics-disclosure {
  font-size: 12px;
  color: rgba(234, 240, 243, 0.66);
}
.public-note .metrics-disclosure {
  margin-top: 8px;
  color: #747e87;
}
a:not([href]) {
  color: inherit;
  text-decoration: none;
  cursor: default;
}
.hidden { display: none !important; }
@media (max-width: 900px) {
  .topbar,
  .topbar-left {
    align-items: stretch;
    flex-direction: column;
  }
  .top-search {
    width: 100%;
  }
  .topbar-left .public-metrics {
    width: 100%;
  }
  .topbar-links {
    align-self: flex-start;
  }
  .latest-update,
  .transparency-notice {
    grid-template-columns: 1fr;
  }
  .latest-copy h2 {
    font-size: 38px;
  }
  .latest-media {
    border-left: 0;
    border-top: 1px solid var(--line);
  }
  .filter-heading,
  .credit-list div {
    grid-template-columns: 1fr;
  }
  .filter-heading {
    align-items: stretch;
    flex-direction: column;
  }
  .review-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 680px) {
  .site-header, main { width: min(100% - 24px, 1180px); }
  .review-grid { grid-template-columns: 1fr; }
  .latest-copy h2 { font-size: 32px; }
  .thumb { aspect-ratio: 16 / 9; }
  .latest-media img { min-height: 220px; }
  .hero { padding-top: 36px; }
}
"""


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


SITE_JS = """
const search = document.querySelector("#search");
const category = document.querySelector("#category");
const reviewGrid = document.querySelector("#review-grid");
const topicFilter = document.querySelector("#topic-filter");
const cards = Array.from(document.querySelectorAll(".review-card"));
const categoryTriggers = Array.from(document.querySelectorAll("[data-category-filter]"));

function normalize(value) {
  return (value || "").toLocaleLowerCase("ko-KR");
}

function updateCategoryTriggers(value) {
  for (const trigger of categoryTriggers) {
    trigger.classList.toggle("active", trigger.dataset.categoryFilter === value);
  }
}

function applyFilters() {
  const q = normalize(search.value);
  const c = category.value;
  for (const card of cards) {
    const haystack = normalize(`${card.dataset.title} ${card.dataset.tags} ${card.textContent}`);
    const categoryMatch = !c || card.dataset.category === c;
    const searchMatch = !q || haystack.includes(q);
    card.classList.toggle("hidden", !(categoryMatch && searchMatch));
  }
  updateCategoryTriggers(c);
}

function setCategory(value, scrollTarget) {
  category.value = value;
  applyFilters();
  if (scrollTarget) {
    scrollTarget.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

search.addEventListener("input", applyFilters);
category.addEventListener("change", applyFilters);
for (const trigger of categoryTriggers) {
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    const value = trigger.dataset.categoryFilter || "";
    setCategory(value, value ? reviewGrid : reviewGrid);
  });
}
document.querySelector('a[href="#topic-filter"]')?.addEventListener("click", (event) => {
  event.preventDefault();
  topicFilter.scrollIntoView({ behavior: "smooth", block: "start" });
});
"""


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
        errors.append(f"missing local href/src in {document_path}: {raw_url}")
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


def validate_public_support_files(public_dir: Path) -> list[str]:
    errors: list[str] = []
    if not public_dir.exists():
        return errors
    for support_path in sorted(public_dir.iterdir(), key=lambda path: path.name.lower()):
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
) -> list[str]:
    errors: list[str] = []
    review_index = SITE_DIR / href
    if not review_index.exists():
        return [f"missing review index: {review_index}"]

    text = review_index.read_text(encoding="utf-8")
    errors.extend(validate_local_references(review_index, text, sparse_tracked_paths))

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
                )
            )
            errors.extend(validate_public_support_files((SITE_DIR / href).parent))
    errors.extend(validate_methods_page(sparse_tracked_paths))
    site_index = SITE_DIR / "index.html"
    if not site_index.exists():
        errors.append(f"missing site index: {site_index}")
        return errors
    index_text = site_index.read_text(encoding="utf-8")
    for risk in public_text_risks(index_text):
        errors.append(f"{risk} left in {site_index}")
    singleton_patterns = {
        "public metrics stylesheet": r"assets/public-metrics\.css",
        "public metrics script": r"assets/public-metrics\.js",
        "public metrics config": r"window\.AI_TECH_REVIEW_METRICS\s*=",
        "favicon": r"favicon\.ico",
        "SVG favicon": r"federlicht-favicon\.svg",
        "apple-touch icon": r"apple-touch-icon\.png",
    }
    for label, pattern in singleton_patterns.items():
        count = len(re.findall(pattern, index_text, flags=re.IGNORECASE))
        if count != 1:
            errors.append(f"unexpected {label} count in {site_index}: {count}")
    for required in (
        '<link rel="canonical" href="https://infant83.github.io/AI_Tech_Review/">',
        '<meta property="og:title" content="AI Tech Review Letters">',
        '<meta name="twitter:card" content="summary_large_image">',
        'href="methods/"',
    ):
        if required not in index_text:
            errors.append(f"missing homepage metadata or methods link: {required}")
    return errors


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish the AI Tech Review static hub and registered review pages."
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
    selected_reviews = set(args.review)
    known_reviews = {review.folder: review for review in REVIEWS}
    unknown_reviews = sorted(selected_reviews - set(known_reviews))
    if unknown_reviews:
        for folder in unknown_reviews:
            print(f"[public-site:error] unknown review: {folder}")
        return 2

    preferred_category_order = load_existing_category_order() if selected_reviews else []
    existing_manifest = load_existing_manifest()

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    copy_icon_assets()

    manifest: list[dict[str, object]] = []
    for review in REVIEWS:
        if not selected_reviews or review.folder in selected_reviews:
            manifest.append(publish_review(review, existing_manifest.get(review.folder)))
            continue
        manifest.append(
            preserve_published_review(review, existing_manifest.get(review.folder))
        )
    manifest.sort(key=lambda item: str(item["date"]), reverse=True)

    index_html = inject_public_icons(render_index(manifest, preferred_category_order))
    index_html = inject_public_metrics(index_html)
    (SITE_DIR / "index.html").write_text(inject_cloudflare_web_analytics(index_html), encoding="utf-8")
    (SITE_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS_DIR / "site.css").write_text(SITE_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "public-metrics.css").write_text(PUBLIC_METRICS_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "public-metrics.js").write_text(PUBLIC_METRICS_JS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "site.js").write_text(SITE_JS.strip() + "\n", encoding="utf-8")

    errors = validate_public_site(manifest)
    if errors:
        for error in errors:
            print(f"[public-site:error] {error}")
        return 2

    print(f"[public-site] {SITE_DIR}")
    print(f"[public-site] reviews={len(manifest)}")
    for item in manifest:
        print(f"[review] {item['href']}")
    print("[public-site-check] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
