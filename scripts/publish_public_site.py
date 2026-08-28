from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import stat
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


@dataclass(frozen=True)
class PublicTranslation:
    language: str
    subdir: str
    label: str


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
    ),
    PublicReview(
        folder="2026-08-27_classiq-ashn-circuit-compression",
        title="양자 회로는 어디에서 짧아지는가: Classiq 합성과 AshN 네이티브 게이트",
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
    ),
    PublicReview(
        folder="2026-05-06_gpt-5-5-family-post-release-evaluation",
        title="GPT-5.5 기술동향 리포트",
        subtitle="긴 작업 수행 능력, Hallucination 평가, Claude Opus 4.7 비교, 안전한 활용 조건",
        date="2026-05-10",
        updated="2026-05-10",
        category="Frontier Models",
        tags=("GPT-5.5", "Claude Opus", "Agentic AI", "Trust and Safety"),
        summary=(
            "GPT-5.5 계열 모델의 장시간 작업 수행 능력과 외부 평가를 함께 보며, 실제 업무에 "
            "맡길 수 있는 일의 조건을 점검합니다."
        ),
    ),
)


LOCAL_REF_RE = re.compile(
    r"(?P<prefix>\b(?:src|href)=['\"])(?P<url>[^'\"]+)(?P<suffix>['\"])",
    re.IGNORECASE,
)
LOCAL_HREF_RE = re.compile(r"\s+href=(?P<quote>['\"])(?P<url>[^'\"]+)(?P=quote)", re.IGNORECASE)
INTERNAL_PATH_RE = re.compile(r"(?:file:///[A-Za-z]:[\\/][^<>'\"\s]+|(?<![A-Za-z0-9])[A-Za-z]:[\\/][^<>'\"\s]+)")
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
    ".md",
    ".txt",
    ".pdf",
    ".json",
    ".csv",
    ".py",
    ".html",
}
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "html":
            self.html_lang = values.get("lang", "").strip().lower()
            return
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
    return endpoint.strip().rstrip("/")


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
    script_src = f"{asset_prefix}assets/public-metrics.js"
    pad = " " * indent
    return (
        f"\n{pad}<!-- AI Tech Review Public Metrics -->"
        f"\n{pad}<script>window.AI_TECH_REVIEW_METRICS={config};</script>"
        f"\n{pad}<script defer src=\"{html.escape(script_src, quote=True)}\"></script>"
        f"\n{pad}<!-- End AI Tech Review Public Metrics -->"
    )


def inject_public_metrics(html_text: str, asset_prefix: str = "") -> str:
    html_text = PUBLIC_METRICS_HEAD_RE.sub("\n", html_text)
    html_text = PUBLIC_METRICS_SCRIPT_RE.sub("\n", html_text)
    head = public_metrics_head(asset_prefix)
    scripts = public_metrics_scripts(asset_prefix)
    if head and "</head>" in html_text:
        html_text = re.sub(r"\n[ \t]*</head>", head + "\n  </head>", html_text, count=1)
    if scripts and "</body>" in html_text:
        html_text = re.sub(r"\n[ \t]*</body>", scripts + "\n  </body>", html_text, count=1)
    return html_text


def inject_public_icons(html_text: str, asset_prefix: str = "") -> str:
    html_text = PUBLIC_ICON_RE.sub("\n", html_text)
    icons = public_icon_links(asset_prefix)
    if icons and "</head>" in html_text:
        return re.sub(r"\n[ \t]*</head>", icons + "\n  </head>", html_text, count=1)
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


def sanitize_for_public(
    html_text: str,
    dist_dir: Path,
    public_dir: Path,
    language: str = "ko",
) -> tuple[str, list[str]]:
    copied: list[str] = []
    source_to_dest: dict[Path, str] = {}
    used_names: set[str] = {"index.html"}

    def replace_ref(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            return match.group(0)

        local_path, query, fragment = split_local_url(raw_url)
        if not local_path:
            return match.group(0)

        source_path = (dist_dir / local_path).resolve()
        suffix = source_path.suffix.lower()

        if suffix not in PUBLIC_REVIEW_FILE_SUFFIXES:
            safe_url = html.escape(raw_url, quote=True)
            return f"data-local-ref=\"{safe_url}\""

        if not source_path.exists() or not source_path.is_file():
            safe_url = html.escape(raw_url, quote=True)
            return f"data-missing-ref=\"{safe_url}\""

        if source_path not in source_to_dest:
            dest_name = unique_dest_name(source_path, used_names)
            source_to_dest[source_path] = dest_name
            shutil.copy2(source_path, public_dir / dest_name)
            copied.append(dest_name)

        new_url = rebuild_local_url(source_to_dest[source_path], query, fragment)
        return f"{match.group('prefix')}{html.escape(new_url, quote=True)}{match.group('suffix')}"

    sanitized = LOCAL_REF_RE.sub(replace_ref, html_text)
    sanitized = INTERNAL_PATH_RE.sub("[local path removed]", sanitized)
    sanitized = sanitized.replace("<body>", '<body class="public-review">')
    if "</body>" in sanitized and 'class="public-note"' not in sanitized:
        if language.lower().startswith("en"):
            public_note = (
                "\n<section id=\"public-local-references\" class=\"public-note\">"
                "<p>This public HTML includes the article, figures, external references, and relative links "
                "to local review notes and authoring-support files.</p>"
                "<p class=\"metrics-disclosure\">Public views and average reading time are recorded only "
                "as aggregate values by page path, without personal identifiers.</p>"
                "</section>\n"
            )
        else:
            public_note = (
                "\n<section id=\"public-local-references\" class=\"public-note\">"
                "<p>공개 HTML에는 본문, 시각 자료, 외부 참고 링크와 함께 "
                "검토에 사용한 로컬 메모와 작성 보조 파일의 상대경로 링크를 포함했습니다.</p>"
                "<p class=\"metrics-disclosure\">공개 조회수와 평균 읽은 시간은 개인 식별 정보 없이 "
                "페이지 경로 단위의 집계값으로만 기록합니다.</p>"
                "</section>\n"
            )
        sanitized = sanitized.replace("</body>", public_note + "</body>")
    asset_prefix = asset_prefix_for_public_dir(public_dir)
    sanitized = inject_public_icons(sanitized, asset_prefix)
    sanitized = inject_public_metrics(sanitized, asset_prefix)
    return inject_cloudflare_web_analytics(sanitized), copied


def copy_public_support_files(dist_dir: Path, public_dir: Path, copied: list[str]) -> list[str]:
    copied_names = set(copied)
    for source_path in sorted(dist_dir.iterdir(), key=lambda path: path.name.lower()):
        if not source_path.is_file():
            continue
        if source_path.name == "index.html" or source_path.suffix.lower() not in PUBLIC_REVIEW_FILE_SUFFIXES:
            continue
        dest_path = public_dir / source_path.name
        if not dest_path.exists():
            shutil.copy2(source_path, dest_path)
        copied_names.add(source_path.name)
    return sorted(copied_names)


def publish_dist_variant(
    dist_index: Path,
    public_dir: Path,
    language: str,
) -> tuple[str, list[str]]:
    public_dir.mkdir(parents=True, exist_ok=True)
    raw_html = dist_index.read_text(encoding="utf-8")
    public_html, copied_assets = sanitize_for_public(
        raw_html, dist_index.parent, public_dir, language
    )
    (public_dir / "index.html").write_text(public_html, encoding="utf-8")
    copied_assets = copy_public_support_files(dist_index.parent, public_dir, copied_assets)
    return public_html, copied_assets


def existing_translation_entries(review: PublicReview) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for translation in review.translations:
        public_dir = review.translation_public_dir(translation)
        if not (public_dir / "index.html").exists():
            continue
        assets = sorted(
            path.name for path in public_dir.iterdir() if path.is_file() and path.name != "index.html"
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
) -> dict[str, object]:
    return {
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
    }


def preserve_published_review(review: PublicReview) -> dict[str, object]:
    public_index = review.public_dir / "index.html"
    if not public_index.exists():
        raise FileNotFoundError(f"Missing dist and published index for {review.folder}")

    existing_html = public_index.read_text(encoding="utf-8")
    parser = FirstImageParser()
    parser.feed(existing_html)
    thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""
    copied_assets = sorted(
        path.name
        for path in review.public_dir.iterdir()
        if path.is_file() and path.name != "index.html"
    )
    print(f"[public-site:preserve] {review.folder} (source dist missing or not selected)")
    return build_review_manifest_entry(
        review, thumbnail, copied_assets, existing_translation_entries(review)
    )


def publish_review(review: PublicReview) -> dict[str, object]:
    if not review.dist_index.exists():
        return preserve_published_review(review)

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
    if public_dir.exists():
        remove_tree(public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)

    public_html, copied_assets = publish_dist_variant(review.dist_index, public_dir, "ko")

    parser = FirstImageParser()
    parser.feed(public_html)
    thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""

    translation_entries: list[dict[str, object]] = []
    for translation in review.translations:
        dist_index = review.translation_dist_index(translation)
        translation_public_dir = review.translation_public_dir(translation)
        _, translation_assets = publish_dist_variant(
            dist_index, translation_public_dir, translation.language
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

    return build_review_manifest_entry(
        review, thumbnail, copied_assets, translation_entries
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

    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Tech Review Letters</title>
    <meta name="description" content="AI, 과학, 에이전트, 제조 데이터, 거버넌스 주제를 다루는 공개 기술 리뷰 허브">
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
          <a href="https://infant83.github.io/">Operator</a>
          <a href="manifest.json">Manifest</a>
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
          <p class="section-kicker">AI Transparency and Source Notice</p>
          <h2 id="transparency-heading">투명성 및 출처 고지</h2>
          <p class="operator">작성정보</p>
        </div>
        <div class="notice-body">
          <dl class="credit-list">
            <div>
              <dt>작성자</dt>
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
              <dt>작성 보조 및 퇴고</dt>
              <dd>Codex 기반 GPT-5 계열 에이전트 하네스</dd>
            </div>
          </dl>
          <ul>
            <li>이 허브의 게시물은 AI 보조 생성 및 퇴고 과정을 거친 콘텐츠입니다.</li>
            <li>외부 출처의 저작권/라이선스는 원 저작권자에게 있으며, 재배포 전 원문 정책 확인이 필요합니다.</li>
            <li>고위험 의사결정(법률·의료·재무·규제)에는 원문 대조와 추가 검증 절차를 수행하세요.</li>
            <li>EU AI Act 투명성 취지에 따라 AI 생성/보조 작성 콘텐츠임을 명시합니다.</li>
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


def validate_public_page(
    href: str,
    expected_language: str,
    expected_alternates: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    review_index = SITE_DIR / href
    if not review_index.exists():
        return [f"missing review index: {review_index}"]

    text = review_index.read_text(encoding="utf-8")
    for match in LOCAL_REF_RE.finditer(text):
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            continue
        local_path = split_local_url(raw_url)[0]
        if local_path and (review_index.parent / local_path).resolve().exists():
            continue
        errors.append(f"missing local href/src in {review_index}: {raw_url}")

    if "data-missing-ref=" in text.lower():
        errors.append(f"data-missing-ref left in {review_index}")
    if INTERNAL_PATH_RE.search(text):
        errors.append(f"internal path left in {review_index}")

    metadata = PageMetadataParser()
    metadata.feed(text)
    if metadata.html_lang != expected_language:
        errors.append(
            f"unexpected html lang in {review_index}: {metadata.html_lang!r} != {expected_language!r}"
        )

    if expected_alternates:
        expected_canonical = public_url_for_href(href)
        if metadata.canonical_urls != [expected_canonical]:
            errors.append(
                f"unexpected canonical in {review_index}: {metadata.canonical_urls!r} != {[expected_canonical]!r}"
            )
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


def validate_public_site(manifest: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for item in manifest:
        specs = page_specs(item)
        expected_alternates: dict[str, str] = {}
        if len(specs) > 1:
            expected_alternates = {
                language: public_url_for_href(href) for href, language in specs
            }
            expected_alternates["x-default"] = public_url_for_href(str(item["href"]))
        for href, language in specs:
            errors.extend(validate_public_page(href, language, expected_alternates))
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

    existing_manifest = load_existing_manifest() if selected_reviews else {}
    preferred_category_order = load_existing_category_order() if selected_reviews else []

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    copy_icon_assets()

    manifest: list[dict[str, object]] = []
    for review in REVIEWS:
        if not selected_reviews or review.folder in selected_reviews:
            manifest.append(publish_review(review))
            continue
        existing_entry = existing_manifest.get(review.folder)
        if existing_entry is not None:
            manifest.append(existing_entry)
        else:
            manifest.append(preserve_published_review(review))
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
