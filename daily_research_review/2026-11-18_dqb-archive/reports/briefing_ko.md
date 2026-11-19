다항식 하나를 받아 수천 개의 조건 중 몇 개를 만족하는지 세는 일은, 좋은 다항식을 처음부터 찾는 일보다 쉽다. 최적 다항식 교차 문제(OPI)는 이 차이를 이용해 양자 계산을 시험한다. 양자컴퓨터가 높은 점수의 후보를 내놓으면 고전컴퓨터가 그 점수를 확인할 수 있다. 여기서 검증하는 것은 후보의 점수이며, 모든 후보 가운데 최선이라는 증명까지 얻는 것은 아니다.

11월 17일 학술지 Physical Review X에 채택된 Khattar 등의 DQI(decoded quantum interferometry) 연구는 좋은 후보를 만드는 회로를 구체적인 자원표로 옮겼다. 대표 인스턴스에 필요한 레지스터는 1,885개 논리 큐비트이며, 회로 한 번의 Toffoli 게이트 수는 약 572만 개다. 암호·오류정정에서 쓰이는 Reed–Solomon 복호를 가역 회로로 구현할 때 중간 결과를 저장하는 방식을 바꾸고 레지스터를 공유해 이 비용을 낮췄다. 사전공개본에서 같은 목표 점수에 대해 제시한 10의 23승 이상 고전 시행 횟수는 연구진이 분석한 Extended Prange 공격 모형의 추정이다.<span class="citation">[<a href="#ref-1">1</a>]</span>

이제 회로를 한 번 실행하는 비용과 원하는 답을 얻는 비용 사이가 중요해진다. 오류정정이 실행을 보호해도 각 표본이 목표 점수에 도달하는 확률은 따로 남는다. 11월 17일 공개된 코드 v2는 유한 크기에서 점수의 평균을 높이는 가중치와 목표 이상 점수를 뽑을 확률을 높이는 가중치를 나누어 계산한다. 따라서 장치의 오류율·코드 주기·저장 배치와 함께 성공확률에 따른 반복 횟수를 정해야 전체 실행시간을 논할 수 있다.<span class="citation">[<a href="#ref-2">2</a>]</span>

실제 장치에서 돌아가는 Aqarios의 제약 최적화도 같은 질문을 다른 방식으로 만난다. IBM Heron의 74–132큐비트 실행에서 유효한 높은 점수의 해를 반환했지만, 앞단의 변수 고정과 뒤의 고전 후처리도 결과를 만든다. IBM 문서는 동일한 후처리를 거치면 고전 표본도 비슷한 최종 품질에 이를 수 있다고 설명한다.<span class="citation">[<a href="#ref-3">3</a>]</span> 어떤 표본이 최종 해에 기여했는지를 읽어야 하는 이유다.

기존 「양자 계산의 전체 비용을 설계하다」가 물었던 공간·대기·반복 비용의 관계를 DQI는 검증 가능한 탐색 문제로 구체화한다.<span class="citation">[<a href="#ref-4">4</a>]</span> 계산이 끝났을 때 확인할 답의 조건을 먼저 정하면, 한 번의 회로에서 성공한 작업 전체까지 무엇을 더 세어야 하는지도 드러난다.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://doi.org/10.1103/2cxf-9srg">T. Khattar, N. Shutty, C. Gidney, A. Zalcman, N. Yosri, D. Maslov, R. Babbush, and S. P. Jordan, Verifiable quantum advantage via optimized DQI circuits, Phys. Rev. X (accepted 17 November 2026)</a>; <a href="https://arxiv.org/abs/2510.10967v1">T. Khattar, N. Shutty, C. Gidney, A. Zalcman, N. Yosri, D. Maslov, R. Babbush, and S. P. Jordan, Verifiable quantum advantage via optimized DQI circuits, arXiv:2510.10967v1 (2025)</a>.</li>
<li id="ref-2"><a href="https://doi.org/10.5281/zenodo.24325102">T. Khattar, N. Shutty, C. Gidney, A. Zalcman, N. Yosri, D. Maslov, R. Babbush, and S. Jordan, Data for “Verifiable quantum advantage via optimized DQI circuits”, Zenodo, version v2 (2026).</a></li>
<li id="ref-3"><a href="https://quantum.cloud.ibm.com/docs/en/functions/aqarios-constrained-quantum-optimizer">Aqarios, Constrained Quantum Optimizer - A Quantum Function by Aqarios, IBM Quantum Documentation (accessed 19 November 2026).</a></li>
<li id="ref-4"><a href="https://infant83.io/AI_Tech_Review/reviews/2026-09-09_quantum-resource-aware-workflows/">H.-J. Kim, 양자 계산의 전체 비용을 설계하다, AI Tech Review Letters (9 September 2026).</a></li>
</ol>

## 작성·검증

편집부(AEDAUT) `dqb1119_nov18`이 원 DQB 4쪽과 관련 원문을 대조하고 한영 초안을 작성했으며 root가 문체·판본·인용·요약을 다듬고 통합했다. PRX 채택 초록과 2025년 사전공개본의 선택한 자원 분석, 2026년 자료 v2의 설명·코드, IBM 공식 문서와 기존 리뷰를 확인했다. 채택본 전체 본문을 읽었다고 표시하지 않는다. `dqb1119_systems`가 한영 편집글과 별도 요약을 독립 감수했고, `dqb1119_pdf`가 공개 PDF를 제작·검사했다. 원호는 2026년 11월 18일이며 웹 작성일·추가 근거 기준일은 11월 19일이다. 원 연구의 전체 자원 계산·제품·QPU를 재실행하거나 사람 독자 평가를 수행하지 않았다. AI 보조는 OpenAI Codex이며 정확한 모델 식별자는 미보존이다.
