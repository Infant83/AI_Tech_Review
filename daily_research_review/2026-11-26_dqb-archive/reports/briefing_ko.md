리튬 원자의 전자 상태를 계산할 때, 궤도를 더 많이 쓰는 대신 궤도함수의 모양을 다시 맞출 수 있다. Deb와 Prasannaa의 MSTO 연구는 가우스 함수들을 묶는 계수와 폭을 조정해, 기존 최소 기저와 같은 수의 궤도로 더 낮은 고전 전자구조 에너지를 얻었다. 리튬은 더 큰 일부 표준 기저보다도 낮은 에너지를 보인 사례다. 전자를 회로에 담기 전에 표현을 개선하는 선택이다.<span class="citation">[<a href="#ref-1">1</a>]</span>

다만 작은 기저가 무엇을 잘 표현하는지는 대상에 따라 달라진다. 원자 에너지에 맞춘 함수가 결합을 만들고 끊는 분자에도 그대로 잘 맞지는 않았고, 수소 분자와 탄소 이원자 분자에는 한계가 드러났다. 기저를 바꾸면 유한 기저에 표현한 해밀토니안도 달라지므로, 줄어든 회로와 함께 원하는 물성의 오차를 확인해야 한다. OLED 분자의 들뜬상태나 에너지 차이에 이 접근을 옮기려면 그 물성을 기준으로 다시 시험할 필요가 있다.<span class="citation">[<a href="#ref-1">1</a>]</span>

논문의 회로 비용도 이 관점에서 읽을 수 있다. 리튬의 VQE 비교는 가정한 상태를 한 번 준비하는 회로의 게이트 수를 세며, 에너지는 양자회로의 출력이 아닌 고전 FCI 기준값이다. 여기서 절감된 게이트 수를 에너지 한 값을 얻는 전체 비용으로 옮기려면 측정과 반복을 더해야 한다. 앞선 「양자 계산의 전체 비용을 설계하다」에서 살핀 입력 준비와 목표 정확도의 질문이 기저 선택까지 거슬러 올라오는 셈이다.<span class="citation">[<a href="#ref-1">1</a>, <a href="#ref-2">2</a>]</span> 작은 표현의 가치는 큐비트 수와 함께, 그 표현으로 필요한 답을 얼마나 정확하게 읽을 수 있는지에서 판단할 수 있다.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://arxiv.org/abs/2608.02119v3">S. Deb and V. S. Prasannaa, Better accuracy with fewer qubits: Single-particle basis set optimization for electronic structure calculations on quantum computers, arXiv:2608.02119v3.</a></li>
<li id="ref-2"><a href="https://infant83.io/AI_Tech_Review/reviews/2026-09-09_quantum-resource-aware-workflows/">H.-J. Kim, 양자 계산의 전체 비용을 설계하다, Agentic Tech Review Letters (9 September 2026).</a></li>
</ol>

## 작성·검증

편집부(AEDAUT) root가 원 DQB 5쪽 전체 텍스트·화면과 기존 전체 비용 리뷰의 한영 관련 논의를 읽고 집필했다. MSTO arXiv 3판의 초록·방법과 원자/분자 결과, 회로 비용 절·부록 표의 관련 구간을 대조했으며, 초록 등록정보와 실제 원고의 제목·주장 차이를 구별했다. `dqb1125_qflow_materials`가 해당 원문·공식 코드의 공개 상태와 한영 글·제목·별도 요약을 비작성자로 감수했다. 원 DQB의 다른 문헌은 `dqb1125_pdf`와 `legacy1126_pdf_gate`가 담당했으며 최종 실제 독해·출력 감수 범위는 회차 기록에 남긴다. 원호·웹 작성일·추가 근거 기준일은 2026년 11월 26일이다. 원 계산·양자회로·QPU 실험이나 사람 독자 평가는 재현하지 않았다. AI 보조는 OpenAI Codex이며 정확한 모델 식별자는 미보존이다.
