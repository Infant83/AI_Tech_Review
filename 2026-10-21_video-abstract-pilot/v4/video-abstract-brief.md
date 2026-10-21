# v4 비디오 기획과 실제 구현

2026-10-22. 원 게시물: [대칭에서 보존법칙으로](../../2026-10-17_noether-symmetry-conservation/reports/review_ko.md). 상태: 실제 한영 영상 제작 완료. 기술 검사와 최종 해시를 대조한 독립 encoded 영상 심사 통과. 기사 native player·게시 검수는 게시자가 별도로 수행한다. 원고·지침만 수정한 단계와 구별하며 완료 결과는 README와 private QA에 기록한다.

게시물의 중심 주장은 대칭과 보존량을 모형 설계와 계산 검증에 활용하되, 학습한 물리 법칙의 정확성과 유한 간격 계산의 오차를 별도로 확인해야 한다는 것이다. 진동자는 리뷰 자체 수치 계산이고 HNN은 방법 구성이다. 새 AI 학습 결과가 아니며 원문의 모든 절을 소개하지 않는다. v3의 6장면과 근거를 유지하면서 공통 설명 준칙·영상 원칙0.5·시각 개편 계획을 실제 도식과 음성에 적용한다. 한영 발화에 필요한 용어 정의를 짧게 더해 실제 길이는 한국어236.75초, 영어228초다.

| 이해할 관계 | 실제 발화 구절·의미 cue | 볼 대상·변화 | 다음 질문·조건 |
|---|---|---|---|
| 외부 공급이 없는데 근사 계산의 진폭이 커짐 | `reference`, `euler`, `article_question` | 같은 초기상태·축척, 초기±A 범위, 실제 n27 이후 위치범위 이탈, n150 결과 유지 | 정확한 진폭이 왜 일정한가? 무마찰·무구동 선형 수평 용수철 |
| 내부 에너지 교환·시간 대칭·노터 관계 | `energy_exchange` → `clock_origins` → `action_definition` → `noether_energy` | 막대만 먼저 움직임. 같은 정확상태를 정지한 뒤 clock 눈금을 도입. T−V 시간적분으로 작용 소개 | 일정한 합이 근사 계산에도 남는가? 시간원점 재표시는 대칭의 증명이 아님 |
| 물리상태를 한 점에 대응시키고 에너지 원과 첫 근사 비교 | `state_mapping` → `phase_plane_name` → `energy_circle` → `euler_tangent` → `one_percent` | 실제 spring x=A,v=0 → 정규화 q,u → 점 → 원 → 첫 실제 갱신과25배 등방 확대 → E1/E0=1.01 유지 | 같은1% 증가를 반복하면? 좌표 대응은 물리적 morph가 아님 |
| 큰 누적과 작은 %오차를 차례로 해석 | `repeat_one_percent` → `euler_final` → `verlet_curve` → `percent_zoom` → `interpret_methods` | 상단 로그 곡선·끝값을 먼저 읽고 벨레선을 지목한 뒤 하단 선형%축 도입, 결과 유지 | 계산법 검사 다음 배운 법칙도 검사. 같은h 교육용 비교 |
| 배운 함수·연속 방정식·수치적분 구별 | `learn_function` → `previous_symbols` → `canonical_symbols` → `hamilton_equations` → `continuous_conservation` → 두 검사 질문 | Hθ 먼저 제시, q/u→q/p 의미 설명, 해밀턴 방정식 두 식, 연속시간 보존 조건, 적분/이산 상태는 마지막 별도 강조 | 실제 에너지 학습과 계산 오차는 따로 판단. 새 학습실험 없음 |
| 앞의 두 결과를 게시물 결론으로 회수 | `recall_two_tests` → `recall_learned_law` → `design_constraints` → `article_argument` → `external_exchange` | 축이 남은 실제 정지 그래프와 앞에서 설명한 도식 재사용. 새J기호 없음 | 대칭을 설계 조건으로, 보존량을 검사 기준으로 사용. 외부 교환은 모형에 포함 |

`storyboard.json`의 의미ID는 문장 번호가 아니라 한영의 실제 발화 구절에 연결한다. renderer는 캐시 재사용 또는 합성한 음성 unit의 시작·끝 시간으로 각 ID를 확정한다. `qa/timeline-private-{ko,en}.json`에 anchor·실제 발화·local/video seconds가 기록된다. 단순한 장면길이 비율로 의미 전환을 정하지 않는다. 물리 시간 τ=ωt와 화면시간·수치단계n을 구별한다.

정규화는 q=x/A,u=v/(Aω),h=ωΔt=.1이며 .1초라는 뜻이 아니다. 초기 상태(1,0),E0=.5,2,000단계의 Euler 비율439286205.0500984와 Verlet 최대 절대 상대오차 약.0024999993을 유지한다. 첫 Euler 계산점은(1,−.1), 확대 배율은두축동일25배다. HNN은 매끄럽고 명시적 시간 의존성이 없는 Hθ와 정준 좌표를 가정한다. 그 보존은 연속시간에 관한 것이며 실제 에너지 정확성이나 적분 정확성을 입증하지 않는다.

v2의 생성 hero 그림 하나만 배경으로 재사용한다. 새 이미지·생성형 비디오·외부 유료 음성 API는 사용하지 않는다. 수학·궤적·막대·축·정량 결과는 NumPy/Pillow 코드다. 기존v3 음성49개를 텍스트가 같은지 확인해 재사용하고 새 정의·수정 발화26개만 Supertonic2/F1로 기기에서 합성한다. 합성음성임을 영상·transcript에 고지한다. v2에 보존된 MIT 코드/OpenRAIL-M 모델의 출력 사용·고지 조건을 따른다.

공개 웹 MP4에는 발화 자막을 굽지 않는다. 별도 VTT를 native player에 연결하고 영상 아래 안전영역은 남긴다. 시각 정보를 설명하는 TXT와 정지 poster를 함께 제공한다. 게시용 원본 allowlist는 MP4·WebP·VTT·TXT·timeline과 manifest이며, 실제 기사에는 root가 언어별 MP4·poster·VTT·TXT 네 개만 합의한 이름으로 복사한다. source·TTS·QA·캐시·런타임은 배포 대상이 아니다.

과학 검토와 실제 출력 검토를 구별한다. 별도 에이전트가 대본·수치·첫 등장 still을 확인했고, 완성된 encoded 출력의 의미 전환·자막·디코드 검수는 최종 해시와 함께 기록했다. 두 언어 각각 83개 독립 추출 프레임, 총 24개 시간순 contact sheet와 8개 전체 해상도 프레임을 별도 검토했다. 사람의 청취·발음·이해도 평가는 하지 않았다. 자동 음량·자막·프레임 검사로 사람 평가를 대신했다고 말하지 않는다.
