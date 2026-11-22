# 양자 알고리즘의 원리와 응용 및 실용화 조건 리뷰 기획

2026-11-22 · 편집부(AEDAUT) 조사·기획 · 공개 게시 전

## 중심 질문과 편집 방향

**양자 알고리즘은 우리가 풀려는 문제를 어떤 연산으로 바꾸고, 그 연산의 결과를 어떻게 읽어 내는가.** 위상·진폭·간섭을 출발점으로 Shor, Grover, QFT, QPE, VQE, QAOA, HHL, quantum walks, QAE, QSVT를 연결한다. 각 알고리즘의 이론적 이점을 입력 준비·회로·측정·오류정정과 함께 읽고, 지금 사용할 수 있는 방법과 유용한 규모로 가기 위해 남은 조건을 설명한다.

- 가제: **양자 알고리즘은 어떻게 문제를 바꾸는가**
- 부제: **Shor에서 QSVT까지 원리와 응용과 실용화 조건을 연결하는 열 가지 경로**
- 형식: 하나의 체계적인 심층 리뷰. 본문은 공통 원리와 사례의 이야기를 따라가고, 알고리즘별 비교표와 선택형 수식·회로 설명을 둔다.
- 독자: 양자 회로의 회전·상호작용을 접했지만, 그것이 분자 에너지·검색·확률 추정·최적화의 답으로 이어지는 과정을 알고 싶은 연구자와 기술 독자.
- 기획 의도: 알고리즘 이름을 기억하는 데서 나아가, 자신의 문제에서 필요한 입력·출력과 실제 이점의 조건을 판단하게 한다. 앞선 정보·에너지 리뷰의 ‘검증된 결과를 얻는 전체 비용’이라는 관점을 양자 계산으로 이어 간다.

기존 [양자 소프트웨어·AI 에이전트 리뷰](../2026-10-25_quantum-software-platforms-ai-agents/reports/review_ko.md)에서 다룬 명세·회로 합성·검증의 문제를, 이번에는 **무슨 계산을 선택하고 어떤 물리 정보를 얻을 것인가**로 확장한다. SDK와 회사의 자동화 기능은 필요한 회로를 실제로 만드는 지점에서 소개한다.

사용자가 제공한 [Quantum Computing Era의 공개 LinkedIn 소개](https://www.linkedin.com/posts/10-quantum-computing-algorithms-worth-knowing-share-7530179971982483456-TI0u/)의 열 가지 항목을 출발 목록으로 사용한다. QFT와 QPE는 다른 계산 안에서 쓰이는 핵심 절차, QSVT는 여러 알고리즘을 구성하는 변환 체계라는 역할을 먼저 잡는다. 이름의 목록과 계산을 이루는 구조를 함께 읽는 기획이다.

### 도입 시안

같은 분자의 에너지를 구하는 데에도 서로 다른 양자 알고리즘을 쓸 수 있다. 한 방법은 회로가 만든 상태의 에너지를 반복 측정하며 회전 각도를 고친다. 다른 방법은 그 상태를 시간에 따라 진화시키고, 진화 중 쌓인 위상에서 에너지를 읽는다. VQE와 QPE다. 구하려는 물리량은 같지만, 상태를 준비하고 정보를 끌어내는 순서가 달라지면 필요한 회로의 길이와 측정 횟수도 달라진다.

이 차이를 따라가면 양자 알고리즘의 이름들이 서로 연결되기 시작한다. QFT는 위상에 담긴 반복 무늬를 읽는 도구가 되고, Grover의 두 반사는 원하는 결과의 진폭을 키우는 회전이 된다. 그 회전의 크기를 읽으면 확률을 추정하는 QAE로 이어진다. 현대의 QSVT에서는 행렬의 특이값에 원하는 함수를 적용하는 문제로 여러 계산을 구성할 수 있다.

연구자가 알고 싶은 것은 어떤 이름의 알고리즘이 가장 강력한가보다, 자신이 원하는 답이 이 구조 안에서 어떻게 표현되는가이다. 분자 에너지 하나, 조건을 만족하는 배치 하나, 위험 사건의 확률 하나는 서로 다른 출력이다. 입력 자료를 회로에 넣고 그 출력을 꺼내는 비용까지 살펴보면, 양자 계산의 장점이 살아나는 문제와 아직 어려운 문제를 구체적으로 구별할 수 있다.

## 이야기의 전개

### 1 회전과 간섭이 계산할 대상을 정한다

한 큐비트의 회전과 두 큐비트의 상호작용에서 시작한다. 위상에 문제의 값이 들어가고, 간섭을 거쳐 측정 확률이 달라지는 짧은 예제를 보여준다. 상태를 많이 표현하는 능력과 필요한 결과를 읽는 절차를 연결한다. 뒤에서 반복 사용할 위상, 진폭, 기대값과 측정의 뜻을 이 장면에서 소개한다.[1]

### 2 위상을 읽어 주기와 에너지를 구한다

QFT와 QPE의 관계를 먼저 설명한 뒤 Shor의 주기 찾기와 물리계의 에너지 추정으로 갈라진다. Shor에서는 정수의 모듈러 거듭제곱이 주기 정보로, 물리계에서는 시간 진화의 고유위상이 에너지로 이어지는 과정을 읽는다. 계산의 목적과 절차의 재사용을 동시에 보여주는 장이다.[1,2]

### 3 원하는 결과를 찾고 그 확률을 추정한다

Grover의 표식과 반사가 두 차원 부분공간에서 회전을 만든다는 그림을 둔다. 이어 같은 진폭 증폭 연산을 여러 깊이에서 실행해 성공 확률을 추정하는 QAE로 넘어간다. 검색의 ‘검사 한 번’과 실제 가역 판정 회로의 비용을 함께 설명한다.[3,4]

### 4 물리적 상태와 좋은 후보를 변분적으로 만든다

VQE에서 준비한 상태·측정 에너지·고전 최적화가 순환하는 이유를 설명한다. QAOA에서는 목적함수에 따른 위상과 후보를 섞는 연산이 번갈아 작용하는 모습을 구체적인 그래프 문제로 보여준다. 같은 하이브리드 구조 안에서도 목표와 회로의 제약이 다름을 읽는다.[5,6]

### 5 행렬을 변환하는 언어로 다시 연결한다

HHL에서 선형계의 해가 양자 상태로 만들어지는 과정을 설명하고, 어떤 관측량을 읽으려는지 먼저 정한다.[7] 양자 보행은 그래프의 연결을 진폭의 전파와 간섭으로 이용한다.[8] QSVT에서는 블록 인코딩에 담은 행렬의 특이값을 다항식으로 바꿔 역함수·필터·시간 진화를 구성한다.[9]

이 지점에서 목록에 없던 **해밀토니안 시뮬레이션**을 연결 기술로 소개한다. U(t)=exp(−iHt/ℏ)를 구현해야 에너지의 위상을 읽거나 물리적 동역학을 계산할 수 있다. Qubitization과 QSP가 이 구현을 정교하게 만든 원리를 QSVT와 연결한다.[10]

### 6 알고리즘의 이점이 실제 작업의 이점이 되는 조건

입력 준비 → 알고리즘 호출 → 논리 게이트 → 오류정정·물리 게이트 → 반복 측정 → 고전 처리의 전체 작업을 같은 도식으로 읽는다. 최신 연구의 성과는 아래 표에서 실행 수준을 나누어 비교한다. 고전 기준법도 같은 정확도와 출력에 맞춰 고른다.

### 7 실용화의 시점을 조건과 함께 전망한다

현재 SDK·클라우드에서 실행할 수 있다는 사실, 유용한 크기의 문제를 계산했다는 사실, 고전적 방법보다 시간·비용의 이점이 있다는 사실을 각각 확인한다. 연도는 기업이 발표한 목표와 논문이 가정한 자원 조건에 연결한다. 알고리즘별 현재 단계와 남은 조건, 현행 기업 로드맵은 [상용화·자원 근거표](timelines-and-evidence.md)에 정리한다.

## 알고리즘별 원리와 활용

| 알고리즘과 역할 | 기본 연산과 물리적 뜻 | 실제 입력과 읽는 출력 | 응용에 사용할 방법 |
|---|---|---|---|
| **QFT** · 표현을 바꾸는 절차 | 기저 상태를 규칙적인 상대위상의 중첩으로 바꾸어 주기 구조가 간섭에 나타나게 한다.[1] | 계산 기저에 표현된 상태 → Fourier 기저의 상태. 측정은 필요한 주파수·위상 정보를 얻도록 다른 절차와 결합한다. | 주기 찾기와 QPE에 사용한다. 고전 데이터의 전체 Fourier 계수 배열이 필요하면 입력 준비와 읽기까지 센다. |
| **QPE** · 고유위상 추정 | U의 고유상태에 controlled-U의 여러 거듭제곱을 작용시켜 위상차를 만들고 읽는다.[1] | U와 고유공간에 겹침이 있는 준비 상태 → 고유위상의 추정과 확률. U=exp(−iHt/ℏ)이면 에너지와 연결한다. | 분자·재료의 에너지, 스펙트럼과 다른 알고리즘의 부품. 목표 고유상태와 초기 상태의 겹침, 위상 정밀도, 최대 진화 시간을 설계한다. |
| **Shor** · 주기 찾기를 이용한 정수 알고리즘 | 모듈러 거듭제곱의 주기를 양자 간섭으로 추정한 뒤 고전 수론 처리로 인수·이산로그를 구한다.[2] | 정수와 가역 산술 회로 → 주기 후보, 최종 인수·이산로그. | 암호 분석의 자원 추정과 암호 전환의 위험 평가. 큰 수를 위한 산술·uncomputation·오류정정 스케줄을 구체적으로 컴파일한다. |
| **Grover** · 진폭 증폭 검색 | 조건을 만족하는 상태의 위상을 뒤집고 기준 상태에 대한 반사를 반복해 좋은 부분공간의 진폭을 키운다.[3] | 가역 판정기 f와 초기 상태 → 조건을 만족하는 후보를 높은 확률로 샘플링. | 제한된 구조의 후보 탐색·열쇠 검색·다른 알고리즘의 성공 확률 증폭. 판정기와 그 역연산의 전체 비용을 산정한다. |
| **QAE** · 확률·기대값 추정 | 상태 준비 A가 만든 성공 진폭을 Grover 계열의 회전으로 증폭하고 여러 관측에서 회전각을 추정한다.[4] | 분포·payoff·성공 판정을 인코딩한 A와 A† → 확률 또는 정규화한 기대값과 오차 구간. | Monte Carlo형 위험·가격·적분 계산. 분포 로딩, payoff 산술, 회로 깊이와 표본 수, 신뢰도를 함께 최적화한다. |
| **VQE** · 변분 고유값 계산 | 매개변수 회로로 상태를 만들고 H의 기대값을 측정해 고전 최적화로 각도를 바꾼다.[5] | Hamiltonian과 ansatz → 근사 상태·에너지·관측량. | 전자구조·스핀 모형·물성 계산. 활성공간·보존 대칭·ansatz·측정 묶음·최적화·잡음 대응을 함께 선택한다. |
| **QAOA** · 구조를 가진 변분 최적화 | 목적함수의 위상 연산과 mixer를 번갈아 적용해 좋은 후보의 측정 확률을 조절한다.[6] | 비용 Hamiltonian·제약·초기 상태 → 후보 bit string과 비용의 분포. | MaxCut·조합 최적화. 문제의 제약을 유지하는 mixer, 깊이 p, 각도 초기화와 고전 탐색을 비교한다. |
| **HHL** · 양자 선형계의 원형 | 고유값 정보를 얻고 그 역수에 맞춘 진폭 조작 후 보조계를 정리해 해 상태를 만든다.[7] | 효율적으로 접근 가능한 A와 준비 상태 &#124;b⟩ → A⁻¹&#124;b⟩에 비례하는 정규화 상태. | 선형 방정식·미분방정식·응답량 계산의 부품. 전체 해 벡터보다 필요한 기대값을 정하고, 조건수·전처리·상태 준비·측정 비용을 포함한다. |
| **Quantum walks** · 그래프 위의 간섭 | 연결에 따라 진폭이 이동하고 여러 경로가 간섭하도록 이산 또는 연속 시간 진화를 구성한다.[8] | 그래프 접근 연산·초기 상태·표식 → 탐색 결과, 표본 또는 진화의 관측량. | 구조적 검색·Markov chain형 표본화·물리 시뮬레이션. 그래프 구조와 스펙트럼, 준비·검사·업데이트 연산의 비용을 정한다. |
| **QSVT** · 행렬 변환 체계 | 큰 유니터리의 한 블록에 넣은 A의 특이값 σ에 허용 조건을 만족하는 다항식 p(σ)가 작용하도록 위상·반사를 합성한다.[9] | 블록 인코딩·다항식·위상열 → 변환된 연산 또는 이를 이용한 상태·관측량. | 행렬 역함수·스펙트럼 필터·상태 준비·시간 진화를 구성한다. 블록 인코딩의 정규화, 스펙트럼 구간, 다항식 차수·짝홀성·범위 조건과 위상 합성 비용을 확인한다. |

## 현재 연구의 최전선을 읽을 대표 사례

여기서 ‘최전선’은 서로 다른 병목을 실제로 줄이거나 검증하는 최근 사례를 뜻한다. 유명 연구자·기업의 단일 순위를 만들기보다, 어떤 문제에서 어떤 증거로 진전했는지 연결한다. 창시자의 원논문은 앞 표의 근거로, 현재 연구 주체는 아래의 결과와 연결해 소개한다.

| 대상 | 최근 연구·대표 주체 | 확인한 수준과 본문에서 읽을 진전 | 다음에 확인할 과제 |
|---|---|---|---|
| **QFT** | Aumann·Fellner·Lechner 등의 **ParityQC**, IBM Heron r3를 사용한 QFT 벤치마크. 2026-11-04 개정 v3.[11] | 실제 QPU에서 배치와 native gate set에 따른 QFT 실행을 비교한다. 50큐비트의 과정 충실도는 약10⁻²이며, SWAP 기반 매핑과 비교한 개선을 보고한다. | 과정 충실도와 응용의 최종 성공 확률을 연결해 평가한다. 논문의 매핑·충실도 개선과 고전 계산 대비 시간 이점은 별도 지표로 다룬다. |
| **QPE** | **Kaur Kristjuhan·Dominic W. Berry**, Molecular Quantum Solutions·Macquarie의 제어 상태 준비와 중간 측정 방식. 2026-08-19 출판.[12] | 최적 신뢰구간을 위한 제어 상태를 효율적으로 준비하고 제어 레지스터를 재사용한다. 세 제어 큐비트는 전체 시스템 큐비트 수와 구별해 설명한다. | 목표 상태 준비, controlled evolution, 회로 깊이·정밀도·논리 오류의 총비용. |
| **Shor** | **Axel Pappalardo와 공동연구진**, cat-qubit 구조에 맞춘 end-to-end 컴파일. 2026-11-19 개정 v2.[13] | 논리 산술에서 물리 배치·스케줄까지 이어지는 자원 추정. 물리 장치의 잡음·주기·피드백 시간을 조건으로 읽는다. | 작은 정수 시연에서 RSA 규모로의 오류정정·산술·공장·연결성의 격차와 가정의 실증. |
| **Grover** | **Evan M. Reeves·Elias Sopkin·Thomas A. Searles**, 구체적 절차적 생성 문제의 oracle 설계. 2026-10-23 v1.[14] | 산술 특수화의 자원 추정과 축소 문제의 실제 IBM·Quantinuum 실행을 나누어 보여준다. | 한 oracle 호출의 가역 회로·역계산·routing 비용과 전체 검색 반복, 경쟁 고전 탐색. |
| **QAE** | **Farrokh Labib**, power-of-two 이외의 깊이 스케줄·정확한 최대우도 추정. 2026-09-02 v1.[15] | 적응 여부와 병렬성, 최대 회로 깊이·총 query·신뢰구간을 함께 설계하는 수치·이론 연구. | 실제 상태 준비·payoff 회로·잡음의 조건에서 동일 정밀도의 총시간과 비용. |
| **VQE** | **Hugo D. Nogueira·Jean-Philip Piquemal와 공동연구진**, VULCAN의 grow–compress–perturb. 2026-11-02 개정 v3.[16] | 큰 비교는 에뮬레이션이며 Quantinuum H2의 초기 실험을 별도로 보고한다. 회로 성장·압축과 고전 섭동 보정의 분업을 읽는다. | 측정·최적화·보정·고전 후처리의 전체 자원과 물리 관측량, 강한 고전 전자구조 기준법. |
| **QAOA** | **Michael A. Perlin·Ruslan Shaydulin와 공동연구진**, **JPMorganChase·Quantinuum**. 2026-11-19 PRX.[17] | H2·Helios에서 오류정정된 fault-tolerant 구성요소로 작은 알고리즘을 실행한다. near-breakeven은 부호화한 양자 실행과 비부호화 실행의 비교다. | 고전적으로 각도를 정하고 작은 T-gate 예산에 맞춰 고른 인스턴스에서, 더 큰 문제의 반복 최적화·강한 고전 휴리스틱과의 최종 해 품질 비교로 나아가야 한다. |
| **HHL·현대 선형계 알고리즘** | [17]의 Poisson HHL 실험, **Guang Hao Low·Yuan Su**의 초기 상태 준비 query 개선. 2026-03-23 출판.[18] | 실제 작은 논리 회로와 더 나은 query 복잡도의 이론이 서로 다른 방향의 진전이다. | A와 b의 실제 접근·준비, κ와 정확도, preconditioner 구축, 원하는 출력 관측의 비용. |
| **Quantum walks** | **Massimiliano Incudini·Guglielmo Mazzola**의 fully-quantum Metropolis 연구(2026-07-24 v1), **Tao Rong와 공동연구진**의 구조적 검색 실험(2026-11-15 v1).[19,20] | 전자는 특정 Ising 표본화의 이론·FT 컴파일·고전 비교, 후자는 실제 gate-based 검색이다. 전체 상태공간과 축소 불변부분공간 encoding을 구별한다. | 제안·수락·검사 비용, 혼합 시간·정확도, 실제 그래프와 하드웨어 구현에서의 이점. |
| **QSVT** | **Joel Bierman·Pawan Poudel·Yuan Liu**의 double randomization(2026-11-13 v1), **Xi Lu·Yuan Liu·Hongwei Lin**의 U(N) 확장(2026-03-27 출판).[21,22] | 블록 인코딩과 다항식을 함께 무작위화하는 자원·오차 분석, 여러 다항식 변환을 구성하는 이론적 확장을 읽는다. | 실제 Hamiltonian의 블록 인코딩 비용, 오차 예산, sampling과 coherent depth의 교환, 합성 회로의 실험 검증. |

본문에서는 각 결과가 줄인 병목을 좁혀 설명한다. 동일 계열에서 결과가 달라지는 원인을 비교하고, 다른 알고리즘과의 결합까지 추적한다.

## ‘언제 쓸 수 있는가’를 세 개의 시계로 읽는다

도구의 출시, 과학적 유용성의 실증, 경쟁 가능한 비용으로의 채택은 다른 속도로 진행된다. 전망은 이 세 시계를 나란히 놓고 제시한다. 지금 활용할 수 있는 개발 환경을 소개하고, 다음 장치에서 검증할 응용을 고른 뒤, 그 응용이 필요한 정확도의 답을 얻는 전체 비용을 비교하는 순서다.

현재 기업 계획에는 Quantinuum의 Sol 2027년·Apollo 2029년, IBM의 Starling 2029년, IonQ의 2027–2030년 논리 큐비트 확대 목표가 있다.[23–25] 이 목표가 실제로 달성되고 필요한 게이트·논리 오류율·운전 시간을 확보한다면, **2027–2029년을 작은 논리 알고리즘에서 더 깊은 응용 검증으로 넘어갈 조건부 관찰 창**으로 삼을 수 있다. 이는 다음의 검증을 어디에 둘지에 대한 편집상 전망이다. 알고리즘과 장치의 자원표를 직접 맞춰야 해당 응용의 실행 가능성을 판단할 수 있다.

| 시계와 시간 창 | 무엇을 사용할 수 있거나 검증할 것인가 | 판단에 필요한 결과 |
|---|---|---|
| **도구·연구 서비스: 현재, 2026년** | QFT·QPE·Grover·QAE·HHL·walks의 작은 회로와 VQE·QAOA 하이브리드 실험, QSVT 회로 설계, 작은 정수의 Shor 교육 계산. | 사용자가 자신의 입력을 회로로 만들고 출력을 검산하는 방법. API 제공·하드웨어 실행·고전 대비 유용성을 각각 표시한다. |
| **응용 실증: 2027–2029년 기업 목표가 충족되는 경우** | QPE·VQE의 같은 물리량 비교, QAOA의 깊이·해 품질, 실제 oracle를 넣은 Grover·QAE의 전체 비용, QLSA·QSVT·walks의 구조적 응용을 더 큰 논리 회로에서 시험한다. QFT는 각 응용 안에서 평가한다. | 같은 정확도에서 상태 준비·오류정정·측정·고전 후처리를 포함한 결과와 총시간. 장치의 논리 자원이 해당 회로를 지탱한다는 실측 근거가 먼저 필요하다. |
| **경제적 채택: 응용별 자원–장치 조건을 충족한 뒤** | 장치 가동·연산·대기·재시도 비용까지 넣어 특정 업무에서 지속적으로 활용한다. RSA 규모 Shor도 산술 깊이와 장시간 오류정정을 실제 장치에 대조해 별도로 전망한다. | 강한 고전 대안과 같은 품질·신뢰도를 확보한 time-to-solution·비용·에너지 비교. 응용별 이 검증의 완료 시점이 실제 채택 전망을 결정한다. |

따라서 가까운 활용은 **현재의 연구 도구와 공동 개발**, 다음 검증 기회는 **조건부 초기 오류정정 응용**, 실무 채택은 **문제별 전체 비용의 이점**으로 설명한다. 알고리즘별 필요한 마일스톤과 Shor·QPE·QAOA의 정량 자원 근거는 [상용화·자원 근거표](timelines-and-evidence.md)에 둔다. 본문의 피규어 3은 세 시계를 겹쳐 보여 주되 기업의 날짜는 계획, 논문의 수치는 해당 가정 아래 추정, 실제 장치 결과는 실증으로 표시한다.

## 공동 예제로 계산의 구조를 보인다

**두 스핀의 작은 Hamiltonian** H=J Z₀Z₁+h(X₀+X₁)을 사용한다. J와 h는 에너지 단위, 시간 진화는 exp(−iHt/ℏ)로 둔다. VQE는 상태와 기대 에너지를 바꾸고, QPE는 준비한 상태의 고유성분에 쌓인 위상을 읽는다. 위상은 2π를 주기로 같아지므로, 에너지 구간을 알고 시간 t와 에너지 이동을 정해 서로 다른 에너지가 같은 위상으로 보이는 aliasing을 피한다. QSVT에서는 정규화한 H의 스펙트럼에 필터를 적용한다. 같은 행렬과 관측량을 유지하면서 다른 계산 경로를 비교할 수 있다.

**작은 MaxCut 문제**에서는 QAOA의 비용 위상과 mixer를 보여준다. 같은 후보 집합에 ‘cut 값이 정해 둔 기준 이상인가’라는 가역 판정을 만들면 Grover형 검색을 설명할 수 있고, 정해진 상태 준비에서 그런 후보가 나올 확률은 QAE의 대상이 된다. 입력 문제의 그래프와, bit string 사이의 이동을 나타내는 상태공간 그래프는 별도 패널에서 구별한다.

**주기 찾기 예제**는 작은 정수의 모듈러 거듭제곱으로 따로 둔다. 모듈러 함수의 반복과 Fourier 측정의 피크가 어떻게 연결되는지 계산한다. 작은 시연에는 문제의 답을 미리 넣은 컴파일과 일반적인 가역 산술의 차이를 기록한다.

이 예제들은 리뷰가 수행할 교육 계산이다. 원 논문의 하드웨어 실험이나 큰 자원 추정을 재현했다고 표시하지 않는다. 집필 단계에서 상태벡터·직접 대각화·목표 확률과 단위·부호를 독립 검산하고 공개 코드·값을 함께 제공한다.

## 피규어와 읽는 순서

1. **문제에서 관측까지의 전체 지도.** 왼쪽에는 정수·Hamiltonian·그래프·행렬·확률을, 중앙에는 위상 추정·진폭 증폭·변분·행렬 변환을, 오른쪽에는 인수·에너지·후보·기대값을 배치한다. QFT·QPE 같은 절차와 QSVT 같은 체계가 어디에 재사용되는지 표시한다. 화살표는 개념적 의존과 실제 입력·출력을 구별한다.
2. **같은 대상의 서로 다른 계산 경로.** 두 스핀 Hamiltonian의 상태 준비·회전·위상·기대값을 같은 색과 좌표로 잇는다. VQE와 QPE가 얻는 정보와 필요한 반복이 실제 작은 수치로 드러나게 한다. MaxCut은 별도 패널에서 입력 그래프와 상태공간을 구별한다. 짧은 회로와 독자의 조절 변수는 본문에서 해석한다.
3. **실용화 조건과 자원 단계.** query, logical gate, physical qubit, 전체 실행시간·반복·오차를 연결한다. 실제 QPU 결과·컴파일/자원 추정·이론·기업 목표는 서로 다른 표식으로 둔다. 동일 척도인 수치만 같은 축에서 비교하며, 달력 그림에는 검증한 기업 목표와 그 발표일을 명시한다.

표지는 ‘여러 문제의 표현이 같은 간섭 장치에서 각기 다른 관측으로 나타나는 사건’을 탐색한다. 전체 지도와 정량 그림은 코드·SVG로 만들고, 개념 표지는 별도 브리프에서 세 발상을 비교해 제작한다. 이번 기획 단계에서는 새 표지를 생성하지 않는다.

## 알고리즘을 활용할 때 공통으로 물을 것

| 판단할 대상 | 글에서 구체화할 질문 |
|---|---|
| 원하는 답 | 전체 벡터·최적해 하나·확률·에너지 차이 중 무엇을 어떤 오차로 얻을 것인가. |
| 입력 | 자료가 이미 양자 상태인지, 고전 파일에서 새로 로딩하는지, oracle와 그 역연산을 어떻게 구성하는가. |
| 비교법 | 같은 출력과 정확도에 맞는 고전 알고리즘·근사·전처리를 무엇으로 고르는가. |
| 성공과 반복 | 상태 준비의 겹침, postselection·표본 수·검증·실패 후 재시도를 어떻게 센다. |
| 장치와 자원 | 논리 연산을 실제 잡음·연결성·오류정정·피드백 지연에서 얼마나 오래 수행해야 하는가. |
| 활용 시점 | 지금의 교육·탐색·연구 서비스, 제한된 문제의 실증, 경쟁 가능한 실무 운용을 어떤 근거로 구별하는가. |

Quantum annealing과 gate-based QAOA의 유사성은 설명하되, 서로 다른 실행 모델과 성과의 비교 조건을 유지한다. 기업 로드맵의 날짜는 위 조건들이 충족된 알고리즘별 우위의 실현일로 치환하지 않는다. 상세 시점·조건표는 별도 근거 문서에 연결한다.

## 참고문헌

[1] R. Cleve, A. Ekert, C. Macchiavello, and M. Mosca, Quantum algorithms revisited, [Proc. R. Soc. Lond. A **454**, 339 (1998)](https://doi.org/10.1098/rspa.1998.0164).

[2] P. W. Shor, Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer, [SIAM J. Comput. **26**, 1484 (1997)](https://doi.org/10.1137/S0097539795293172).

[3] L. K. Grover, A fast quantum mechanical algorithm for database search, [in Proceedings of the Twenty-Eighth Annual ACM Symposium on Theory of Computing (ACM, New York, 1996), p. 212](https://doi.org/10.1145/237814.237866).

[4] G. Brassard, P. Høyer, M. Mosca, and A. Tapp, Quantum amplitude amplification and estimation, [Contemp. Math. **305**, 53 (2002)](https://doi.org/10.1090/conm/305/05215).

[5] A. Peruzzo, J. McClean, P. Shadbolt, M.-H. Yung, X.-Q. Zhou, P. J. Love, A. Aspuru-Guzik, and J. L. O’Brien, A variational eigenvalue solver on a quantum processor, [Nat. Commun. **5**, 4213 (2014)](https://doi.org/10.1038/ncomms5213).

[6] E. Farhi, J. Goldstone, and S. Gutmann, A quantum approximate optimization algorithm, [arXiv:1411.4028v1](https://arxiv.org/abs/1411.4028v1) (2014).

[7] A. W. Harrow, A. Hassidim, and S. Lloyd, Quantum algorithm for linear systems of equations, [Phys. Rev. Lett. **103**, 150502 (2009)](https://doi.org/10.1103/PhysRevLett.103.150502).

[8] A. M. Childs, R. Cleve, E. Deotto, E. Farhi, S. Gutmann, and D. A. Spielman, Exponential algorithmic speedup by quantum walk, [in Proceedings of the Thirty-Fifth Annual ACM Symposium on Theory of Computing (ACM, New York, 2003), p. 59](https://doi.org/10.1145/780542.780552).

[9] A. Gilyén, Y. Su, G. H. Low, and N. Wiebe, Quantum singular value transformation and beyond: Exponential improvements for quantum matrix arithmetics, [in Proceedings of the Fifty-First Annual ACM SIGACT Symposium on Theory of Computing (ACM, New York, 2019), p. 193](https://doi.org/10.1145/3313276.3316366).

[10] G. H. Low and I. L. Chuang, Hamiltonian simulation by qubitization, [Quantum **3**, 163 (2019)](https://doi.org/10.22331/q-2019-07-12-163).

[11] P. Aumann, M. Fellner, D. Alber, M. Cykiert, C. Fleckenstein, R. ter Hoeven, L. Stenzel, R. J. Valencia-Tortora, and W. Lechner, Demonstrating record fidelity for the quantum Fourier transform, [arXiv:2604.12465v3](https://arxiv.org/abs/2604.12465v3) (2026).

[12] K. Kristjuhan and D. W. Berry, Quantum phase estimation with optimal confidence interval using three control qubits, [Quantum **10**, 2193 (2026)](https://doi.org/10.22331/q-2026-08-19-2193).

[13] A. Pappalardo, D. Goudarzi, V. Hertz, H. Jacinto, L. Kroell, A. Schrottenloher, P. Shanahan, É. Gouzien, R. de la Vieuville, and V. Londe, Shor’s algorithm compiled on cat qubits: 22 593 qubits for RSA-2048 in 3.14 days, [arXiv:2610.37839v2](https://arxiv.org/abs/2610.37839v2) (2026).

[14] E. M. Reeves, E. Sopkin, and T. A. Searles, The cost of a real Grover oracle: Minecraft seed search from software to quantum hardware, [arXiv:2610.33139v1](https://arxiv.org/abs/2610.33139v1) (2026).

[15] F. Labib, Quantum amplitude estimation beyond power-of-two schedules, [arXiv:2609.02715v1](https://arxiv.org/abs/2609.02715v1) (2026).

[16] H. D. Nogueira, S. Badreddine, O. Adjoua, D. Traore, G. Michel, and J.-P. Piquemal, Grow, compress, and perturb: A hybrid quantum-classical pathway to scalable quantum chemistry on quantum computers, [arXiv:2610.40561v3](https://arxiv.org/abs/2610.40561v3) (2026).

[17] M. A. Perlin, Z. He, A. Alexiades Armenakas, P. Andres-Martinez, T. Hao, D. A. Herman, Y. Jin, K. Mayer, C. N. Self, D. Amaro, C. Ryan-Anderson, and R. Shaydulin, Fault-tolerant execution of error-corrected quantum algorithms, [Phys. Rev. X **16**, 041048 (2026)](https://doi.org/10.1103/gnq3-c2df).

[18] G. H. Low and Y. Su, Quantum linear system algorithm with optimal queries to initial state preparation, [Quantum **10**, 2041 (2026)](https://doi.org/10.22331/q-2026-03-23-2041).

[19] M. Incudini and G. Mazzola, Practical advantage beyond the quadratic speedup limit with fully-quantum walks, [arXiv:2607.22818v1](https://arxiv.org/abs/2607.22818v1) (2026).

[20] T. Rong, M. Li, X. Tong, J. Cai, Y. Li, N. Zhou, S. Li, S. Cao, Y. Li, Y. Xu, F. Chen, M. Gong, X. Sun, and C. Zha, Hardware-aware realization of deterministic quantum-walk search on complete bipartite graphs, [arXiv:2611.20053v1](https://arxiv.org/abs/2611.20053v1) (2026).

[21] J. Bierman, P. Poudel, and Y. Liu, Double-randomized quantum singular value transformations for early fault-tolerant quantum computers, [arXiv:2611.18881v1](https://arxiv.org/abs/2611.18881v1) (2026).

[22] X. Lu, Y. Liu, and H. Lin, Quantum signal processing and quantum singular value transformation on U(N), [Quantum **10**, 2048 (2026)](https://doi.org/10.22331/q-2026-03-27-2048).

[23] Quantinuum, [Roadmaps](https://www.quantinuum.com/company/roadmaps) (accessed November 22, 2026).

[24] M. Steffen and M. Marwick, [Tracking progress on the path to IBM Quantum Starling](https://www.ibm.com/quantum/blog/path-to-ibm-quantum-starling) (November 11, 2026).

[25] IonQ, [Roadmap](https://www.ionq.com/roadmap) (accessed November 22, 2026).

## 조사와 집필 준비 기록

- 확인일은 2026-11-22이며 제공 링크의 공개 소개와 원 논문·출판사 기록을 사용했다. 추적 매개변수와 원문 소셜 게시물 전문은 저장하지 않았다.
- 신간·최신 사례의 서지와 초록·공개 소개를 직접 확인했다. [12,17,22]는 출판사 본문 소개와 연구 조건을 읽었고, [11,13–16,18–21]은 판본과 초록을 대조했다. 집필에서 선택할 정량 그림은 각 본문·보충자료·공식 데이터에서 다시 추적한다. 기획 단계의 조사와 원 연구 재현을 구별한다.
- Grover 원논문의 query 이점은 oracle 모델의 검사 횟수로 설명한다. 입력 소개의 ‘백만 중 천 번’ 예시는 실제 검색 시간의 계측값으로 사용하지 않는다.
- QPE의 제어 큐비트, 알고리즘의 논리 큐비트, 물리 큐비트 수를 따로 기록한다. 압축한 불변부분공간의 명목 문제 크기와 전체 입력 공간을 구현한 크기도 구별한다.
- 별도 조사자가 원리·최신 사례표를 교차 검토했고, QFT의 충실도·Grover의 축소 실행·QPE의 에너지 aliasing·상용화의 세 시계를 보완했다. 25개 참고문헌의 최초 인용순, 표 열 수와 동반 근거 파일의 연결을 확인했다.
- 이번 파일은 quantum_algorithms_plan이 작성했고, 상용화·자원 근거표는 quantum_timelines_audit가 별도 작성한다. 등록·배포·새 자동화는 수행하지 않았다. 실제 원고와 시각자료는 이 기획의 다음 제작 단계다.
