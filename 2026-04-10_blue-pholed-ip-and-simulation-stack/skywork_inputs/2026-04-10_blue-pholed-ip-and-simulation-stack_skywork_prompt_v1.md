업로드된 자료와 `LGD_Template.pptx` 템플릿을 기반으로 새로운 한국어 PowerPoint deck을 생성하라.

프로젝트명: Blue PHOLED IP와 시뮬레이션 스택
청중: OLED 소재 연구자, 소자 엔지니어, 기술전략 담당자, 디스플레이 기술 매니저
목적: 2026년 공개 신호를 기준으로 UDC와 Idemitsu의 blue-PHOLED-adjacent IP 흐름, 실제 검증 가능한 의미, 그리고 멀티스케일 시뮬레이션 스택의 한계와 실행 방향을 기술 브리핑 형태로 설명한다.
권장 분량: 14장
비율: 16:9

반드시 사용할 템플릿:
- `LGD_Template.pptx`

사용할 업로드 자료:
1. `2026-04-10_blue-pholed-ip-and-simulation-stack_deepresearch.md`
2. `2026-04-10_blue-pholed-ip-and-simulation-stack_memo.md`
3. `2026-04-10_blue-pholed-ip-and-simulation-stack_sources.md`

소스 우선순위:
1. 업로드된 deep research report
2. 업로드된 source note
3. 업로드된 memo
4. 필요한 경우에만 문서에 이미 인용된 공식 1차 소스

리서치 정책:
- 업로드된 자료의 사실관계와 논지 구조를 우선 사용하라.
- 외부 리서치는 기본적으로 확장하지 말고, 업로드된 문서에 이미 정리된 검증 범위를 기준으로 장표를 구성하라.
- blue PHOLED readiness나 수명 해결을 과장하지 말고, 문서에 기록된 검증 수준을 유지하라.

LGD 템플릿 적용 원칙:
- LGD 템플릿의 master, color system, title rhythm, white-grid corporate background를 유지하라.
- 비교표, 매트릭스, roadmap, annotated review, evidence synthesis에 적합한 기존 템플릿 레이아웃을 우선 사용하라.
- sparse marketing style 대신 dense technical briefing style을 사용하라.
- 작은 짙은 녹색 annotation text로 용어 설명, caveat, technical note를 붙일 수 있다.
- reference와 source cue는 작은 짙은 회색 text로 표시하라.

핵심 편집 원칙:
- deck의 thesis는 `이번 공개 신호는 blue PHOLED 완성 선언이 아니라, 분자 설계·호스트/공정 통합·stack architecture co-design이 동시에 빨라지고 있다는 신호` 여야 한다.
- UDC의 메시지와 Idemitsu의 메시지를 같은 것으로 섞지 말고, `platform breadth` 대 `lifetime mechanism engineering` 축으로 구분하라.
- TMM/RCWA 도구를 곧바로 lifetime predictor처럼 설명하지 말라.
- QUBO는 core predictor가 아니라 exploratory optimization layer로 낮춰 설명하라.

반드시 반영할 verified / high-confidence facts:
- UDC는 `2026-03-25` ICDT 2026 보도자료에서 PHOLED 소재를 `single-stack`, `tandem`, `PSF`, `new pixel designs`와 연결했다.
- UDC patent `12593378`은 `2026-03-31` grant이며, carbazole + triazine host mixture를 one-crucible thermal evaporation으로 적용하는 방향을 보여준다.
- UDC assignee 페이지에는 `2026-04-02`, `2026-04-07`, `2026-04-09`에 걸친 추가 application / grant cluster가 존재한다.
- Idemitsu patent `12538638`은 장수명 organic electroluminescent element를 목표로 하며 multi-EML, host energy alignment를 직접 다룬다.
- `TMMax`, `TMM-Fast`, `grcwa`는 실제 optical simulation / differentiable optimization 도구이지만, 단독으로 blue PHOLED lifetime 문제를 해결하지 않는다.

반드시 피할 것:
- `UDC가 blue PHOLED 수명 문제를 해결했다`는 단정
- `최신 시뮬레이션 도구만 있으면 lifetime 예측이 된다`는 식의 단순화
- 특허 신호와 상용화 readiness를 같은 것으로 묘사하는 과장
- 빈 여백 중심의 마케팅형 슬라이드
- LGD 템플릿과 무관한 새로운 시각 언어

필수 장표 구성:
- 1장: 제목 + 한 줄 결론 + 왜 지금 중요한가
- 2장: executive summary 3x3
- 3장: 이번 Pulse/공개 신호의 구조와 검증 범위
- 4장: UDC 공개 시그널 타임라인 `2026-03-25 ~ 2026-04-09`
- 5장: UDC `12593378` 핵심 의미와 one-crucible host mixture 해석
- 6장: UDC vs Idemitsu 비교표
- 7장: 무엇이 실제로 새로운가 `2026 vs established practice`
- 8장: 분자 설계 -> 공정 통합 -> stack architecture co-design 흐름도
- 9장: realistic multiscale simulation stack
- 10장: TMMax / TMM-Fast / grcwa / QUBO 역할 구분표
- 11장: 무엇이 아직 공개적으로 증명되지 않았는가
- 12장: 실험 검증 로드맵 `DFT/TD-DFT -> exciton/degradation -> optics -> aging`
- 13장: 기업/연구 조직 관점의 시사점
- 14장: closing insight + next actions

시각 정책:
- 표, evidence matrix, timeline, layered diagram, source comparison board를 적극 사용하라.
- 복잡한 내용은 compound slide를 허용하되 하나의 상위 인사이트로 수렴시켜라.
- 특허/보도자료/툴링 출처는 슬라이드 하단이나 관련 블록 근처에 작은 짙은 회색 text로 표시하라.
- 다이어그램과 표는 설명용이어야 하며 장식용 이미지는 최소화하라.

좋은 슬라이드의 조건:
- 각 슬라이드마다 명시적 thesis line이 있어야 한다.
- 경영진도 읽을 수 있어야 하지만, 엔지니어가 보기에도 얇지 않아야 한다.
- signal, evidence, uncertainty, action이 분리되어 보여야 한다.
- 템플릿의 corporate readability를 해치지 않는 선에서 최대한 information dense 해야 한다.

이 기준으로 LGD 템플릿에 맞는 전체 deck을 생성하라.
