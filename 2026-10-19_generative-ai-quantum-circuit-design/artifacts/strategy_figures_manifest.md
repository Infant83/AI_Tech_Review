# 전략·기술층 설명 그림 기록

작성일과 근거 기준일: 2026-10-19. 두 그림은 이 리뷰의 본문 8–10절과 연결한 직접 작성 SVG 개념도다. 논문의 실험 그림이나 회사 로고를 복제하지 않았고, 실험 수치·점수·성능 순위를 추가하지 않았다. 기존 리뷰에서 원문과 공식 자료를 확인한 사실을 다시 배치했으며, 이번 그림 제작에서 새로운 실험이나 제품 성능 검증은 수행하지 않았다.

## 1. `circuit_design_layers.svg`

- 제목: 범용 에이전트는 무엇을 호출하는가.
- 크기: 1000 × 1452 px. 본문 24 px, 설명 22 px, 하단 주석 최소 20 px. 운영체제 한글 sans-serif 폰트, 흰 배경·짙은 글자·차분한 청록과 적색을 사용한다.
- 의도: 전문가가 지시한 같은 범용 에이전트 아래에서 공개 SDK·합성기·검증기를 이용하는 경로와 Classiq Qmod·합성 엔진을 호출하는 경로를 병렬 비교한다. 두 경로 모두 공통 독립 검증과 같은 장치·예산의 평가를 받도록 표시한다.
- 본문 배치 제안: 8절의 에이전트가 Classiq를 호출하는 경우와 우회하는 경우를 구분하는 문단 뒤.
- 해석 조건: 공개 도구 이름은 조합 가능한 예시이며 모두를 한 작업에 반드시 사용한다는 의미가 아니다. 각 SDK·컴파일러·검증기의 기능과 지원 범위는 다르다. 도식은 실제 제품 전체 아키텍처를 재현하지 않는다.
- 검증 해석: 정확성 검증은 Classiq의 독점 기능으로 표현하지 않았다. 공개 경로에도 검증기·시뮬레이터가 있고 두 경로의 출력 회로를 별도의 공통 평가로 확인한다. 의미 검증과 실제 장치 성능은 별개다. 검사 불확정이나 실패를 성공으로 세지 않는 본문 기준이 적용된다.
- 전략 해석: 적색 두 상자는 각각 A만으로 같은 결과를 달성하는 경우와 B의 엔진을 호출하는 경우의 조건부 사업 해석이다. 호출이 발생한다는 사실만으로 매출이나 수익성은 입증되지 않는다. 점선 적색 상자는 AI가 합성 엔진의 규칙·휴리스틱도 개선할 수 있으므로 성능 격차나 사업적 방어력이 영구적으로 고정되지 않음을 표시한다.
- 비교 범위: 제품 전체의 추가 가치는 같은 에이전트·전문가 시간·과제·정확도·장치·예산으로 측정해야 한다. 엔진 자체의 성능을 분리하려면 입력 명세와 독립 검증기도 고정해야 한다.

근거 자료:

- [IBM Qiskit MCP Servers](https://quantum.cloud.ibm.com/docs/en/guides/qiskit-mcp-servers): 에이전트에서 회로와 실행 도구를 호출하는 경로.
- [Classiq Quantum Engineer Plugin](https://docs.classiq.io/user-guide/ai/quantum-engineer-plugin): 범용 개발 에이전트가 Classiq 개발 도구를 사용하는 경로.
- [Classiq Qmod-to-Qmod compiler architecture](https://www.classiq.io/insights/qmod-to-qmod-a-new-compiler-architecture): 구조를 보존하는 컴파일과 기능 수준 합성의 기술 설명.
- [Qrisp memory management 논문](https://arxiv.org/abs/2606.31837), [Qrisp compiler 문서](https://qrisp.eu/reference/Core/generated/qrisp.QuantumSession.compile.html): 공개 고수준 프로그램·보조 큐비트 관리의 예.
- [Quantinuum TKET 저장소](https://github.com/Quantinuum/tket), [MQT QCEC 저장소](https://github.com/munich-quantum-toolkit/qcec): 공개 컴파일러와 등가성 검사기의 예.
- [QuantumEvo 논문](https://arxiv.org/abs/2609.05327): LLM이 합성 휴리스틱 코드를 개선하는 연구. 엔진도 AI의 변화 대상이라는 해석의 근거이며 모든 상용 엔진을 대체했다는 뜻은 아니다.

## 2. `company_technology_layers.svg`

- 제목: 기업별로 값이 쌓이는 기술층이 다르다.
- 크기: 1000 × 1624 px. 본문과 회사명 24 px, 설명 22 px, 하단 주석 최소 20 px. 첫 번째 그림과 같은 색과 한글 폰트를 사용한다.
- 의도: 의도·모델 작성, 합성·컴파일, 응용·검증, 오류 관리·오류정정 자원, GPU·QPU 실행의 다섯 범주에 공개된 주요 기능을 배치한다. Classiq, IBM, NVIDIA, Quantinuum, QMill, Haiqu, Q-CTRL·Qedma가 어떤 자산으로 경쟁하는지 설명한다.
- 본문 배치 제안: 9절의 기업별 기술 자산 표 앞 또는 뒤. 기존 상세 표와 출처 링크를 함께 유지한다.
- 사실과 해석의 구분: 청록색 영역은 본문에서 확인한 공개 기능의 범주 분류다. 적색 하단은 해당 기능이 고객의 구매 이유가 되려면 어떤 차이를 입증해야 하는지에 대한 조건부 전략 해석이다.
- 지도 해석: 패널의 위치·번호·면적·회사명 반복 횟수는 성능·제품 완성도·시장 지배력·전략 자산 강도를 뜻하지 않는다. 선정한 기능만 표시했으므로 특정 층에서 회사가 빠져 있다고 해당 기능이 없다는 뜻은 아니다. 한 업체는 여러 층에 참여할 수 있다.
- 검증 해석: 응용 연구와 제품 실행 통합을 표시하면서 독립 정확성 검증은 모든 경로의 공통 요구라고 따로 명시했다. 나열한 회사들이 같은 종류·같은 범위의 독립 검증 제품을 제공한다는 뜻은 아니다.
- 압축 해석: QMill의 전체 기능 보존은 회사가 밝힌 제품 주장으로 표시했다. Haiqu는 특정 초기상태의 근사 압축으로 구분했다. 두 기능의 압축률이나 품질을 직접 비교하지 않는다.
- 오류 관리 해석: 오류정정 자원 추정과 현재 장치의 오류 억제·완화를 서로 다른 역할로 구분한다. Q-CTRL·Qedma 표기는 두 회사가 같은 기법을 제공한다는 의미가 아니다.
- 실행 해석: NVIDIA의 GPU 모사·학습·실행 인프라와 IBM·Quantinuum의 QPU 및 실행 소프트웨어를 구분했다. 소프트웨어 사용 증가만으로 유료 실행 수요나 수익성이 보장된다고 해석하지 않는다.

근거 자료:

- Classiq: [에이전트 발표](https://www.classiq.io/insights/classiqs-quantum-engineering-agents-now-in-your-ide-and-the-platform), [합성 연구](https://arxiv.org/abs/2412.07372), [Fault Tolerance Engine](https://www.classiq.io/insights/introducing-classiqs-fault-tolerance-engine).
- IBM: [MCP 문서](https://quantum.cloud.ibm.com/docs/en/guides/qiskit-mcp-servers), [AI transpiler 문서](https://quantum.cloud.ibm.com/docs/en/guides/ai-transpiler-passes).
- NVIDIA: [CUDA-Q Logical 공식 발표](https://nvidianews.nvidia.com/news/nvidia-expands-open-source-cuda-q-platform-for-fault-tolerant-quantum-computing), [CUDA-Q Logical 논문](https://arxiv.org/abs/2609.13388), [DQAOA-GPT의 CUDA-Q 모사](https://arxiv.org/abs/2607.20225).
- Quantinuum·NVIDIA 등: [ADAPT-GQE 연구](https://arxiv.org/abs/2607.22468). 두 회사만의 연구라는 뜻이 아니며, 전체 공동 연구진은 원문을 따른다.
- Quantinuum: [TKET 공개 저장소](https://github.com/Quantinuum/tket).
- QMill: [회로 압축 제품의 공개 주장](https://qmill.com/en/blog-by-clayton-leite-qmill-sets-a-world-record-in-quantum-circuit-compression), [qBraid 배포](https://qbraid.com/press/qmill-circuit-compression-is-now-available-on-qbraid-lab).
- Haiqu: [압축 문서](https://docs.haiqu.ai/core_features/compression), [AgenticOS 발표](https://haiqu.ai/blog/haiqu-launches-agentic-quantum-operating-system-for-enterprise-applications-r-d).
- Q-CTRL·Qedma: [Fire Opal 문서](https://docs.q-ctrl.com/fire-opal/discover/adopt/fire-opal-overview), [장치 실행 관리 비교 논문](https://arxiv.org/abs/2608.05202). 비교 논문에는 저자 한 명의 Q-CTRL 유료 자문 관계가 공개돼 있다. 그림은 해당 논문의 업체별 우열이나 수치를 옮기지 않는다.

## QA 기록

- Python `xml.etree.ElementTree`로 두 SVG를 파싱해 XML 문법, viewBox, 텍스트 노드의 존재를 확인했다. 텍스트 노드는 각각 33개와 46개다.
- 스타일의 텍스트 크기는 모두 20 px 이상이다. 내장 `title`과 `desc`, `role="img"`와 `aria-labelledby`를 포함했다.
- bundled Sharp로 각각 원본 1000 × 1452 px, 1000 × 1624 px PNG를 `/tmp/circuit_design_layers_full.png`와 `/tmp/company_technology_layers_full.png`에 렌더했다. 임시 PNG를 이미지 뷰어로 열어 상단부터 하단까지 전체를 검토했다. 한글 표시, 경로의 분기·합류, 패널 구분, 출처·해석 구분, 글자와 도형의 겹침 및 잘림이 없음을 확인했다.
- Quick Look은 원본을 정사각형 썸네일로 잘랐기 때문에 최종 시각 QA에는 사용하지 않았다. 전체 비율을 유지한 Sharp 렌더를 기준으로 확인했다.
- 모바일에는 SVG 원본 크게 보기 링크를 함께 제공하는 것이 적절하다. 1000 px 폭의 그림을 좁은 화면에 축소하면 글자가 작아질 수 있다. 실제 게시 페이지의 데스크톱·모바일 화면 확인은 통합 게시 단계의 별도 QA다.
- 납품 파일은 SVG 두 개와 이 기록이며 임시 PNG는 게시 자산에 포함하지 않는다.
