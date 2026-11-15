양자 장치에서 얻은 전자배치의 후보를 고전 컴퓨터에 넘기면, 선택한 공간에서 분자의 에너지를 계산할 수 있다. 이런 큰 계산에서는 직접 얻은 유한한 결과를 바탕으로 더 정밀한 값을 추정하는 외삽도 사용한다. 11월 15일 DQB에서 다시 살펴본 큐노바의 철–황 계산은 이 두 에너지를 구분해 읽을 때 더 흥미롭다. 회사는 11월 12일 RIKEN의 IBM Quantum System Two와 슈퍼컴퓨터 Fugaku를 결합한 80큐비트 HI-VQE 결과를 발표했다.<span class="citation">[<a href="#ref-1">1</a>]</span>

발표의 최종값은 −327.2482 ± 0.0007하트리다. 부분공간에서 직접 얻은 마지막 에너지에 해당하는 값은 공개하지 않았고, 회사가 제시한 이 수치는 유한한 계산 결과에서 외삽한 추정치다. 비교한 DMRG 기준 −327.2471하트리와 중심값의 차이는 1.1밀리하트리다. 통상 화학적 정확도의 크기로 쓰는 약 1.6밀리하트리 안에 든다. 다만 이 DMRG 기준도 계산 공간을 제한하는 결합 차원을 무한대로 보낸 외삽값이다. 여기서 가까워진 것은 두 외삽 추정이다.<span class="citation">[<a href="#ref-2">2</a>]</span> 어느 공간의 실제 계산값들을 어떤 함수로 맞추었는지, ±0.7밀리하트리가 무엇의 불확실성인지까지 알면 그 정확도가 어떻게 얻어졌는지 더 구체적으로 판단할 수 있다.<span class="citation">[<a href="#ref-1">1</a>]</span>

비용이 줄어든 지점도 중간 결과에서 찾을 수 있다. 회사는 두 번째 반복에서 −326.9821하트리에 도달하는 데 Fugaku 2,518노드시간을 썼고, 앞선 SQD 결과보다 낮은 에너지에 약 300배 적은 비용으로 도달했다고 설명한다. 다음 반복에서 공간을 얼마나 키웠는지, 마지막 외삽값까지 총 얼마가 들었는지는 이 수치에 담겨 있지 않다. 따라서 후속 자료에서 보고 싶은 것은 에너지의 수렴 곡선과 그 곡선의 각 점까지 쌓인 양자·고전 자원이다. 같은 정확도까지 드는 총비용을 비교할 길이 열린다.<span class="citation">[<a href="#ref-1">1</a>]</span>

기존 「분자를 계산하는 두 컴퓨터: 양자 이득은 어디서 오는가」는 양자 장치가 후보를 제안하고 고전 컴퓨터가 부분공간의 파동함수를 푸는 HI-VQE의 분업을 설명했다.<span class="citation">[<a href="#ref-3">3</a>]</span> 당시 검토한 논문의 철–황 문제는 72개 문제 큐비트와 연결용 8개를 사용하므로, 이번 발표의 80큐비트라는 숫자만으로 활성공간이 커졌다고 판단할 수는 없다. 공개 개정판은 이번 발표의 최종 외삽값과 적합 절차를 제시하지 않는다.<span class="citation">[<a href="#ref-4">4</a>]</span> 이번에 보태 볼 논의는 계산 규모의 숫자보다, 후보의 발견과 공간의 확장, 외삽이 각각 정확도에 기여하는 방식이다. 하루 전 브리핑에서 살펴본 학습형 회로 생성기는 첫 단계인 후보의 질을 개선하려 했다.<span class="citation">[<a href="#ref-5">5</a>]</span> 나는 같은 고전 처리와 총예산에서 후보 생성법을 바꾸고, 직접 계산한 에너지와 외삽한 에너지가 함께 어떻게 움직이는지 비교해 보고 싶다.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://qunovacomputing.com/news/148">Qunova Computing, Qunova Sets a New Benchmark for Quantum Chemistry, Matching the Best Classical Methods on a Landmark Iron-Sulfur Problem, company announcement (12 November 2026).</a></li>
<li id="ref-2"><a href="https://arxiv.org/abs/2603.28648v1">Ö. Legeza, A. Menczer, M. A. Werner, S. S. Xantheas, F. Neese, M. Ganahl, C. Brower, S. R. Bernabeu, J. Hammond, and J. Gunnels, Hunting for quantum advantage in electronic structure calculations is a highly non-trivial task, arXiv:2603.28648v1 (2026).</a></li>
<li id="ref-3"><a href="https://infant83.io/AI_Tech_Review/reviews/2026-11-10_qunova-hivqe-quantum-chemistry/">H.-J. Kim, 분자를 계산하는 두 컴퓨터: 양자 이득은 어디서 오는가, Agentic Tech Review Letters (10 November 2026; terminology updated 11 November 2026).</a></li>
<li id="ref-4"><a href="https://arxiv.org/abs/2601.06935v2">P. Yoo, K. Kim, E. E. Elala, S. McFarthing, A. Pellow, J. I. Fuks, D. H. Kang, P. Nakliang, J. Kim, H. Pathak, T. Shirakawa, S. Yunoki, and J.-K. K. Rhee, Extending the Handover-Iterative VQE to Challenging Strongly Correlated Systems: N₂ and Fe-S Cluster, arXiv:2601.06935v2 (2026; revised 12 September 2026).</a></li>
<li id="ref-5"><a href="https://infant83.io/AI_Tech_Review/briefings/2026-11-14/">편집부(AEDAUT), 좋은 양자 표본을 만드는 회로를 학습하다, Agentic Tech Review Letters, Daily Quantum Brief editorial (14 November 2026).</a></li>
</ol>

## 작성·검증

편집부(AEDAUT) root가 원 DQB 4쪽을 읽고 집필·통합했다. 독립 담당자는 회사 발표·HI-VQE 원문·기존 리뷰와 반복 등장한 방법론 연구를 대조했고, 별도 담당자가 공개 PDF를 제작·검사했다. 웹 작성일과 추가 근거 기준일은 2026년 11월 15일이다. 마지막 문단의 비교는 편집 제안이다. 원 논문의 QPU·전자구조 계산을 재실행하지 않았다. AI 보조는 OpenAI Codex이며 정확한 모델 식별자는 미보존이다. 사람의 문장별 감수와 독자 평가는 수행하지 않았다.
