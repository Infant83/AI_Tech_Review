분자의 전자 상태를 더 충실하게 표현하면 에너지 계산도 더 정확해질 것이라고 기대하기 쉽다. 하지만 화학자가 실제로 사용하는 값은 그 상태 자체가 아니라, 여러 계산 단계를 거쳐 얻은 각 상태의 에너지와 그 차이다. 11월 9일 정식 출판된 철–황(Fe–S) 클러스터 연구는 이 간격을 구체적으로 보여준다. 더 좋은 시험상태를 만드는 노력이 최종 답을 언제 개선하는지 다시 묻게 한다. <span class="citation">[<a href="#ref-1">1</a>]</span>

위상 제약 보조장 양자 몬테카를로(phaseless AFQMC)는 시험상태를 길잡이로 삼아 전자 상태들을 확률적으로 표집하고 에너지를 추정하는 고전 계산법이다. Kjønstad 등은 전자 18개·공간 오비탈 14개로 줄인 [2Fe–2S] 모형에서, 기준 바닥상태와의 겹침으로 본 시험상태와 표집 상태 집합의 품질이 함께 좋아져도 에너지 오차는 커질 수 있음을 보였다. 상태를 얼마나 잘 표현했는지와 그 상태로 만든 에너지 추정값이 얼마나 정확한지는 별도로 확인해야 한다는 직접적인 사례다. <span class="citation">[<a href="#ref-1">1</a>]</span>

이 계산은 서로 다른 근사상태를 결합하는 혼합 추정량으로 에너지를 읽는다. 각 상태에 남은 오차가 유리하게 상쇄되던 조건에서는 한쪽을 개선하면서 그 상쇄가 달라질 수 있다. 연구진은 표집을 이끄는 guiding trial과 에너지를 읽는 measurement trial을 분리하고, 두 trial이 같은 표집 상태와 이루는 겹침의 비율로 표본의 가중치를 조정해 이를 살폈다. 단순한 평균장 상태로 에너지를 읽었을 때 dimer의 정확도는 좋아졌지만, 더 큰 클러스터에서는 결과가 엇갈렸다. 이 비교가 가리키는 설계 대상은 상태 하나의 품질에 더해, 상태와 추정량의 조합이다. <span class="citation">[<a href="#ref-1">1</a>]</span>

이는 기존 글 「양자화학의 에너지 차이를 읽는 법: 희소 기준상태와 혼합 추정량」<span class="citation">[<a href="#ref-2">2</a>]</span>에서 다룬 질문을 한 걸음 옮긴다. 그 글에서는 준비한 목표상태와 고전 기준·잔차상태의 두 겹침 확률로 에너지 보정을 읽었고, 확률 하나의 개선이 최종 에너지 차이의 개선과 다를 수 있음을 설명했다. 이번 AFQMC에서는 확률적으로 표집한 상태와 위상 제약까지 관여한다. 서로 다른 계산법을 잇는 관점은, 상태를 평가할 때 그 정보를 어떤 식에 넣어 최종 값을 만드는지 함께 보아야 한다는 것이다.

그 정보를 반복해서 얻는 비용도 바꿀 수 있다. Jiang 등의 Willow 연구는 양자 측정자료를 고전 학습모형에 담아, 몬테카를로 계산이 계속 요청하는 파동함수의 겹침과 미분을 재사용하는 방식을 시험했다. Fe–S 실험에서는 알려진 기준 파동함수가 학습용 표집 상태들과 이루는 겹침을 회로 상태도 재현하도록 얕은 회로를 학습한 뒤 실제 장치에서 측정하고, 그 자료로 고전 모형을 학습했다. 이 과정에서 회로의 변분 에너지를 직접 최소화하는 것과 최종 QMC 에너지를 좋게 만드는 것이 서로 다른 목표로 드러난다. 앞의 Fe–S 연구는 5월 프리프린트로 먼저 공개됐으며 Willow 논문도 이를 인용한다. 두 연구를 함께 읽으면 무엇을 학습시킬지와 학습한 정보를 어디에 쓸지를 같이 설계할 이유가 보인다. <span class="citation">[<a href="#ref-3">3</a>]</span>

한번 얻은 정보를 오래 재사용하는 설계와 매번 장치를 다시 부르는 설계는 HPC 연계 비용도 다르게 만든다. Meller 등의 QASC는 양자 프로그램을 QuEST 고전 시뮬레이터에서 실행하고, 함께 제시한 QACC-perf는 통신 지연·자료 전송·회로 실행시간을 나누어 양자 오프로딩 비용을 추정한다. 이 도구의 가상 오프로딩은 추정 시간만큼 기다린 뒤 고전적으로 계산한 에너지를 돌려주는 방식이다. 따라서 여기서 유용한 것은 실제 QPU 가속률보다, 반복 호출과 통신을 계산에 넣어 어떤 분업이 유리할지 미리 비교하는 기능이다. <span class="citation">[<a href="#ref-4">4</a>]</span>

기존 「양자 계산의 전체 비용을 설계하다」<span class="citation">[<a href="#ref-5">5</a>]</span>가 회로 단계의 절감을 전체 작업의 이득으로 옮길 때 준비·반복·대기를 함께 세자고 했다면, 이번에는 그 비용을 들여 얻는 최종 값도 같은 비교 안에 놓을 수 있다. 이 자료들을 바탕으로 우리가 제안하는 다음 비교는 분자 구조·기저·활성공간과 목표 에너지 오차를 고정하고, 시험상태와 추정량을 바꾸며 고전 학습·양자 측정·통신을 포함한 총시간을 기록하는 것이다. 그러면 더 정확한 상태를 만들었는가에서 더 나아가, 어떤 정보를 한 번 만들고 얼마나 재사용할 때 필요한 화학적 답을 더 효율적으로 얻는가를 판단할 수 있다.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://doi.org/10.1021/acs.jctc.6c01749">E. F. Kjønstad, H. Zhai, J. Shee, S. Sharma, and G. K.-L. Chan, Can phaseless auxiliary-field quantum Monte Carlo with broken symmetry trials describe iron–sulfur clusters?, J. Chem. Theory Comput. (published online November 9, 2026), doi:10.1021/acs.jctc.6c01749.</a></li>
<li id="ref-2"><a href="https://infant83.io/AI_Tech_Review/reviews/2026-10-21_sparse-reference-quantum-chemistry/">H.-J. Kim, Reading Energy Differences in Quantum Chemistry: Sparse References and Mixed Estimators, Agentic Tech Review Letters (2026-10-21).</a></li>
<li id="ref-3"><a href="https://arxiv.org/abs/2611.08151v1">T. Jiang, A. Zhao, S. Kumar, J. Nigam, E. Rosenberg, R. Babbush, A. D. Baczewski, W. J. Huggins, and J. Lee, Machine learning quantum data to accelerate quantum Monte Carlo, arXiv:2611.08151v1 (2026).</a></li>
<li id="ref-4"><a href="https://arxiv.org/abs/2611.09659v1">M. Meller, J. C. R. Thacker, T. W. Keal, and V. Szeremi, Quantum integration software suite for HPC-quantum computing workflows, arXiv:2611.09659v1 (2026).</a></li>
<li id="ref-5"><a href="https://infant83.io/AI_Tech_Review/reviews/2026-09-09_quantum-resource-aware-workflows/">H.-J. Kim, Designing the full cost of quantum computation, Agentic Tech Review Letters (2026-09-09).</a></li>
</ol>

## 작성·검증

작성·대조: 편집부(AEDAUT). 11월 10일 보관본의 원문 감수 기록을 재사용하고, Fe–S 저자 원고 v1의 혼합 추정량·시험상태 역할·dimer 및 cubane 결과, Willow v1 본문 1–4쪽, HPC v1의 비용 모형과 관련 결과를 다시 읽었다. Fe–S 출판본은 등록 서지·초록을 확인한 범위이며 기술 설명은 [저자 원고](https://arxiv.org/abs/2605.03270v1)에 근거한다. 두 기존 리뷰의 한국어 원고를 읽어 연결했고, 새 AFQMC·학습·QPU 실행이나 시간 측정은 하지 않았다. 마지막 문단의 비교 설계는 브리핑의 제안이다.
