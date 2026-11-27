공급처를 나눠 두어도 같은 물류 거점이 멈추면 여러 주문이 함께 도착하지 않을 수 있다. 이번 Daily Quantum Exercise는 전자부품 공장의 긴급 조달을 통해 이런 공동 중단을 계산한다. 부족한 물량의 기대비용과 납기 내 전량을 받는 확률을 각각 구해 보면, 구매팀이 어떤 위험을 줄이려는지에 따라 좋은 주문의 조건도 달라진다.

[문제 PDF의 1쪽 열기](https://infant83.io/AI_Tech_Review/archive/files/2026-11-26-daily-quantum-exercise.pdf#page=1). 15분 문제이며 해설은 2쪽, 비교·판단은 4쪽, 참고문헌은 5쪽에 있다. 기업·물량·확률·실행시간은 교육용 가정이다.

실무에서 이런 모형을 만들 때에는 공급사별 배송률과 함께 같은 날·같은 원인으로 지연된 주문을 조사할 수 있다. 공동 거점·운송 경로를 반영한 시나리오를 만들고, 예약비·부족 비용·납기 기준을 정하면 예비 재고나 다른 경로의 확보 비용을 비교할 수 있다. Gurobi가 공개한 ICRON의 제약기업 공급망 사례도 서비스 요구·공급 위험·완충 재고를 혼합정수 계획에 반영한다.<span class="citation">[<a href="#ref-1">1</a>]</span> 익명 고객에 관한 공급업체의 보고이며, 이번 문제는 그 고객의 데이터나 성과를 재현한 것이 아니다.

<details><summary>주문 비교·수식·해설과 도입 판단 펼치기</summary>
<h3>오늘 정한 주문을 모든 시나리오에서 평가한다</h3>
<p>a,b,c는 공급사 A,B,C에 오늘 예약할지를 나타내는 이진 변수다. 내일 어떤 중단이 생길지 알기 전에 같은 주문을 확정한다. 시나리오별로 주문을 다시 고른 해는 이 의사결정의 대안이 될 수 없다. Gurobi의 Multiple Scenarios 기능은 각 변형 모형의 별도 최적해를 계산하므로, 공통 주문과 확률 제약은 사용자가 모형에 명시해야 한다.<span class="citation">[<a href="#ref-2">2</a>]</span></p>
<ul><li>AB: S0·S1·S2의 부족량 0·4·2상자, 기대 총비용 31만원, 전량 충족 확률 70%.</li><li>AC: 부족량 0·4·2상자, 기대 총비용 33만원, 전량 충족 확률 70%.</li><li>BC: 부족량 0·0·8상자, 기대 총비용 28만원, 전량 충족 확률 90%.</li><li>ABC: 부족량 0·0·2상자, 기대 총비용 34만원, 전량 충족 확률 90%.</li></ul>
<p>전량 충족 확률 90%를 만족하는 BC와 ABC 중 BC가 최적이다. A를 더 예약하면 S2의 부족량은 6상자 줄지만 전량을 채우지는 못한다. 기대 부족 비용은 6만원 줄고 예약비는 12만원 늘어 총비용이 6만원 증가한다. AB의 기대 충족 수량 비율은 87.5%지만, 전량 충족 확률은 70%다. 일부라도 받은 물량의 평균과 전량을 받은 사건의 확률은 서로 다른 지표다.</p>
<h3>이차화한 비용과 납기 제약을 함께 확인한다</h3>
<p>기준 확률의 F=80−36a−27b−25c+14ab+14ac+14abc에는 3차항이 있다. y=ab를 도입하면 14abc를 14yc로 바꾸고 P(ab−2ay−2by+3y)를 더할 수 있다. 잘못된 y의 벌점은 적어도 P이며, 같은 a,b,c에서 y를 바꿔 얻는 비용 이득은 최대 14만원이다. 따라서 P&gt;14만원, 예를 들어 15만원이면 이 치환을 엄격히 강제하는 충분조건이다. 최소 필요 벌점이라는 주장은 아니다.<span class="citation">[<a href="#ref-3">3</a>]</span></p>
<p>제시한 치환에는 a,b,c,y의 4개 이진 변수가 쓰인다. 서비스 확률을 표현할 추가 변수와 물리 큐비트는 포함하지 않은 수다. 시나리오별 부족량 u와 위반 허용 이진 변수 z를 쓰는 MILP에서는 u≥8−q, u≥0, q+8z≥8과 Σp z≤0.10을 함께 둔다. q≥0이므로 big-M=8상자면 충분하다. 양의 부족 비용에 의해 최적해에서 u가 실제 부족량과 같아지며, 같은 주문 변수가 모든 시나리오에 공유된다. 이를 QUBO로 옮길 때에는 위반 변수·slack 부호화·벌점을 추가로 계산해야 한다.</p>
<p>이 작은 문제는 제약을 먼저 정리하면 더 단순하다. 확률이 각각 0.10보다 큰 S0와 S1은 반드시 충족해야 한다. S1의 조건은 b=c=1을 강제하고, 비용은 F=28+6a가 되어 a=0이 정해진다. 두 솔버에 이 전처리를 똑같이 적용하면 비자명한 탐색이 남지 않는다. 네 변수는 위 치환의 크기이며, 모든 가능한 표현의 최소 자원 수를 뜻하지 않는다.</p>
<h3>운영 시간과 선택지의 한계를 계산한다</h3>
<p>1,000 reads×20 μs는 0.020초다. 어닐링 경로 전체는 2+8+15+4+0.020+1=30.020초, 고전 경로는 2+0.30+1=3.30초다. 주어진 10초 제한에서는 기준 모형의 고전 운영은 Go, 양자 운영은 No-Go다. 어닐링을 즉시 끝내더라도 나머지 가정 비용 30초가 남는다.</p>
<p>어닐링은 이차 목적함수의 낮은 에너지 표본을 구하고, QAOA는 Ising 비용을 회로로 구현해 측정과 고전 매개변수 조정을 반복한다. BQM·CQM이라는 모형과 고전·QPU·하이브리드 sampler의 선택을 구별한다.<span class="citation">[<a href="#ref-4">4</a>]</span> 실제 장비 비교에서는 어닐링의 임베딩·사슬 길이·사슬 파손과 계수 정밀도를, QAOA의 라우팅 후 깊이·2큐비트 게이트·shots·최적화 횟수를 기록한다. 대기·통신·해독·검증·재시도도 전체 시간에 포함한다.</p>
<p>스트레스 확률에서 S2가 생기면 모든 공급사에 주문해도 6상자만 도착한다. S2의 확률이 25%이므로 전량 충족 확률의 상한은 75%다. 현재 선택지로는 90% 조건을 달성할 수 없어 Pivot이 필요하다. 별도 거점의 보장 물량 2상자처럼 선택지를 확장하고 비용과 실현성을 다시 평가할 수 있다. 확률이 바뀌면 기대비용 다항식도 다시 계산한다.</p>
<p>후속 PoC는 같은 선택지·시나리오·전처리를 쓴 전수 탐색 또는 MILP를 기준으로 설계한다. 확대 모형에서는 MILP 하한 대비 gap≤1%, 원래 서비스 확률≥90%, 전체 시간≤10초를 모두 확인하고 같은 총 예산에서 시간 또는 비용 이득을 비교한다. 실패·시간 초과도 반복 실행의 분모에 넣는다. 관측하지 않은 기간의 공동 중단 자료로 확률을 교정하고, 스트레스 상황의 부족량도 함께 보고하면 구매 정책의 적용 범위를 판단할 수 있다. 여기서 제시한 시험 설계는 후속 제안이다.</p>
</details>

[분자 역설계의 D-Wave 비교 리뷰](https://infant83.io/AI_Tech_Review/reviews/2026-08-27_dwave-molecular-inverse-design-benchmark/index.html)는 같은 BQM의 정확 최적값과 QPU 표본을 비교하고, 논리 변수에서 물리 큐비트로 임베딩한 기록을 살핀다. 조달 문제에서도 원래 제약을 통과한 해의 비용을 다시 계산하고, 장치에 올리면서 추가된 자원을 기록할 때 참고할 수 있다.

QAOA 경로를 더 살펴보려면 [QML 11강: 하드웨어, 컴파일과 전체 학습 자원 계산](https://infant83.io/AI_Tech_Review/lectures/quantum-machine-learning/lectures-11-hardware-and-resources.html)의 라우팅 예제와 전체 샷·시간 계산을 읽어 볼 수 있다. 게이트형 회로의 컴파일 비용을 다루므로, 이번 어닐링의 시간표에 그대로 대입하지 않고 선택한 실행 방식에 맞춰 자원을 센다.

## 참고문헌

<ol class="reference-list">
<li id="ref-1"><a href="https://www.gurobi.com/resources/case-studies/pharmaceuticals-using-optimization-to-mitigate-risks-across-global-supply-chains">Gurobi Optimization, Pharmaceuticals: Using optimization to mitigate risks across global supply chains (accessed 26 November 2026).</a></li>
<li id="ref-2"><a href="https://docs.gurobi.com/projects/optimizer/en/current/features/multiscenario.html">Gurobi Optimization, Multiple scenarios, Gurobi Optimizer Reference Manual 14.0 (accessed 26 November 2026).</a></li>
<li id="ref-3"><a href="https://docs.dwavequantum.com/en/latest/quantum_research/reformulating.html">D-Wave, Reformulating a problem, D-Wave Quantum Computing Products documentation, Ocean SDK 9.5.0 (accessed 26 November 2026).</a></li>
<li id="ref-4"><a href="https://docs.dwavequantum.com/en/latest/industrial_optimization/workflow.html">D-Wave, Basic workflow: Models and sampling, D-Wave Quantum Computing Products documentation, Ocean SDK 9.5.0 (accessed 26 November 2026).</a></li>
</ol>

## 작성·검증 범위

원호와 근거 확인일은 2026-11-26이며 웹 안내도 이날 작성했다. AEDAUT이 원 PDF 5쪽·한영 안내·공개 요약을 감수하고 8개 주문의 비용·확률, 이차화 벌점, MILP 제약과 시간 합을 독립 계산했다. 위 공식 웹 문서 4건의 관련 본문과 표시 판본을 직접 확인했다. 연결한 기존 리뷰의 BQM·QPU 비교 절은 한영으로, QML 11강의 자원 계산은 국문으로 읽었다. 실제 기업 자료 분석·MILP 소프트웨어 실행·QPU 실행은 수행하지 않았다. 공개 PDF는 1–4쪽의 과학 내용과 원호 날짜·출처 연결을 유지하고, 5쪽의 비공개 학습 이력을 삭제하며 정식 서지를 보완했다. ADOPT이 게시·아카이브·실제 URL 검증을 지원했다. AI 보조 작성·역할을 나눈 에이전트 감수이며, 이 호에 대한 사람의 별도 검토는 확인되지 않았다.
