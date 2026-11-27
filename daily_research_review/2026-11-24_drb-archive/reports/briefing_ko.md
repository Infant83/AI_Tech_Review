스핀-1 한 자리를 표현하려면 세 상태가 필요하다. Kumaran 연구진은 트랜스몬에서 보통 큐비트로 쓰는 두 준위에 두 번째 들뜬 준위를 더해, 한 소자를 큐트릿으로 사용했다. 논문의 비교용 두 큐비트 인코딩은 |0〉·|1〉·|2〉를 각각 |00〉·|01〉·|10〉에 넣고 |11〉을 남긴다. 세 상태를 한 소자에 담으면 준비 회로를 줄일 수 있지만, 높은 들뜬 준위의 잡음과 판독까지 그 선택에 맞춰 설계해야 한다. 이번 실험은 열린 경계의 2·3·4자리 AKLT 상태에서 이 문제를 구체적으로 다뤘다.<span class="citation">[<a href="#ref-1">1</a>]</span>

AKLT 상태를 이해하는 원자가 결합 그림에서는 각 스핀-1을 두 가상 스핀-½의 대칭 부분공간으로 나타내고, 이웃 자리의 가상 스핀 사이에 일중항 결합을 만든다. 이는 1987년 Affleck·Kennedy·Lieb·Tasaki가 제시한 바닥상태 구성의 물리적 그림이다.<span class="citation">[<a href="#ref-2">2</a>]</span> 여기의 가상 스핀은 상태의 얽힘 구조를 설명하는 수학적 자유도다. 실제 회로에서 세 기저를 두 큐비트에 대응시킨 앞의 사상과는 역할이 다르다. 2025년 Edmunds 등의 이온 포획 큐트릿 연구는 이 계열의 상태에서 긴 거리의 string order와 사슬 끝 유효 스핀을 관측했다. 이번 트랜스몬 연구는 또 다른 하드웨어에서 상태 준비와 위상 추정을 연결한다.<span class="citation">[<a href="#ref-3">3</a>]</span>

연구진은 ibm_hanoi에서 0↔1·1↔2 전이를 보정하고, 높은 준위를 쓰는 연산을 회로 뒤쪽에 배치했다. 열린 경계 4자리의 두 대표 회로가 보고한 Hellinger 일치도는 88.68%와 80.80%다. 이는 실험과 이론의 측정 확률분포를 비교한 값으로, 상대위상까지 확인하는 양자 상태 충실도와 구별해야 한다. 위상을 보는 실험에는 주기 경계의 두 자리를 사용했다. 결합 하나를 비트는 매개변수를 바꾸면서 |02〉·|11〉·|20〉의 상대위상을 토모그래피와 가상 RZ 보정으로 맞추고, 이 지배적 부분공간을 선택해 Berry 위상을 추정했다. 3–7개 분할에서 π 부근의 결과를 얻었다는 보고는 이 보정·선택 조건과 함께 읽어야 한다.<span class="citation">[<a href="#ref-1">1</a>]</span>

준비 회로의 압축은 측정 자원과 이어진다. 이번 장치의 판독 방식에서는 |1〉과 |2〉를 분리하기 위해 추가 연산을 넣은 회로들을 실행했고, 전체 삼진 확률분포를 얻는 절차의 회로 수는 큐트릿 수에 따라 지수적으로 늘어난다. 최대 40자리까지의 분석은 별도의 잡음 텐서네트워크 계산이며, 준비 성능을 전망한 그림에는 측정한 T1·T2보다 다섯 배 긴 수명을 가정한 조건도 포함된다. 실제 장치의 짧은 사슬에서 확인한 준비·판독과 이런 확장 계산을 함께 보면, 다음 설계 과제는 분명해진다. 세 준위에 맞춘 인코딩의 이점을 살리면서, 판독 회로와 샷 비용을 얼마나 줄일 수 있는지가 중요하다.<span class="citation">[<a href="#ref-1">1</a>]</span>

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://doi.org/10.1038/s41534-026-01421-w">K. Kumaran, F. Alam, N. Eassa, K. Ferris, X. Xiao, L. Cincio, N. Bronn, and A. Banerjee, Transmon qutrit-based simulation of spin-1 AKLT systems, npj Quantum Inf. (2026).</a></li>
<li id="ref-2"><a href="https://doi.org/10.1103/PhysRevLett.59.799">I. Affleck, T. Kennedy, E. H. Lieb, and H. Tasaki, Rigorous results on valence-bond ground states in antiferromagnets, Phys. Rev. Lett. 59, 799–802 (1987).</a></li>
<li id="ref-3"><a href="https://doi.org/10.1103/PRXQuantum.6.020349">C. L. Edmunds, E. Rico, I. Arrazola, G. K. Brennen, M. Meth, R. Blatt, and M. Ringbauer, Symmetry-protected topological Haldane phase on a qudit quantum processor, PRX Quantum 6, 020349 (2025).</a></li>
</ol>

## 작성·검증

편집부(AEDAUT) root가 공식 2026년 11월 24일 Article in Press 본문과 SI의 지표·기기·판독·회로·위상 보정 대목을 읽고 보고 수치를 대조했다. brief_format은 관련 본문과 선택 SI, 두 선행 논문의 공식 초록·서지를 추가 확인하고 한영 초안을 작성했다. 1987년 논문의 증명과 2025년 이온 실험은 초록·서지 독해 범위에서 연구 맥락으로 사용했다. <a href="https://github.com/keerthikumara/Spin-1/tree/ed2694ea53587d1ce72fad8dda4aba643edf14cc">공개 Spin-1 저장소의 고정 판본</a>에서 파일 목록·README와 대표 노트북의 셀 구조를 정적으로 확인했으며, 하드웨어 회로·원자료 재분석·잡음 모사를 독립 실행하지 않았다. aps_quantum_survey가 비작성 범위에서 원문·선택 SI, 수치·판본·서지, 한영 대응과 제목·목록 요약을 교차 감수했다. 새 심층 리뷰는 제안 상태다. 출판에는 운영팀(ADOPT)의 기존 절차를 사용한다. AI 보조: OpenAI Codex, 정확한 모델 식별자는 미보존. 사람의 문장별 검토는 수행하지 않았다. 웹 작성·추가 근거 기준일은 2026년 11월 24일이다.
