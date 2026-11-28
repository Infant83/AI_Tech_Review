보조 큐비트가 만날 수 있는 이웃은 적어도, 오류정정에서 읽어야 할 연산자는 여러 데이터 큐비트에 걸칠 수 있다. Gehér 등의 directional codes는 iSWAP이 두 상태의 자리를 맞바꾸는 성질을 활용한다. 정사각 격자의 소자를 움직이지 않고도, 보조 상태가 차례로 다른 데이터 상태를 만나 큰 stabilizer의 오류 신호를 읽게 한다. 부호의 대수적 설계와 그 신호를 얻는 회로를 함께 고른 결과다.<span class="citation">[<a href="#ref-1">1</a>]</span>

이 논문은 12개 논리 큐비트를 저장하는 회로 모사에서 유망한 이득을 보였다. 물리 오류율 0.001과 Tesseract short-beam 디코더를 둔 크기별 피팅에서는 회전형 directional 계열의 물리 큐비트 자원비가 rotated toric code의29.2%였다. 그러나 이 수치는 토러스의 주기 연결을 둔 메모리 모사에서 얻었다. 평면 칩의 가장자리를 어떻게 잇고 해독을 얼마나 빨리 수행할지는 별도로 남는다. 같은 논문이 이 두 문제를 후속 과제로 둔 이유도 여기에 있다.<span class="citation">[<a href="#ref-1">1</a>]</span>

코드 설계에서 배선과 측정 회로를 함께 세듯, 재료 역설계에서도 새로 배울 부분과 재사용할 부분을 구별할 필요가 있다. 별도 연구 EGMOF는 목표 물성에서183개의 구조·화학 설명자(descriptor)를 생성하는 모듈과, 이 설명자에서 금속-유기 골격체(MOF) 구조를 만드는 모듈을 나눈다. 후자는 약50만 개 가상 구조로 사전학습한 뒤 재사용하므로,1,000개의 새 물성 자료를 쓴 시험을 전체 학습 데이터가1,000개였던 실험으로 읽을 수는 없다. 수소흡착 벤치마크의 hit rate90%도 학습 분포의 표준편차를 허용폭으로 둔 계산 결과다. 이 고전적 재료 AI 사례는 QMOF의 전자구조 라벨을 활용하지만 새 QPU 계산을 수행한 연구는 아니다.<span class="citation">[<a href="#ref-2">2</a>]</span>

다음 오류정정 리뷰에서는 directional codes의 피팅 자원비를 실제 평면 배선·syndrome 주기·실시간 디코더 비용으로 이어 검토할 것을 제안한다. Directional은11월25일 공개돼 DQB26에서 소개한 논문의 원문 보강이며, EGMOF는11월28일 온라인 공개된 재료 역설계 연구다. 오늘 완성한 [Fock 공간 상태 준비와 센싱 리뷰](https://infant83.io/AI_Tech_Review/reviews/2026-11-28_fock-space-state-preparation-readout/)는 기존 별도 글로 이어 읽을 수 있다.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://doi.org/10.1038/s41467-026-79572-9">G. P. Gehér, D. Byfield, and A. Ruban, Directional codes for quantum LDPC error correction on square and hexagonal grid architectures, Nat. Commun., Article in Press (2026).</a></li>
<li id="ref-2"><a href="https://doi.org/10.1038/s41467-026-79640-0">S. Han, Y. Kang, T. Bae, J. Kim, Y. Kim, V. Bernales, A. Aspuru-Guzik, and J. Kim, EGMOF: efficient generation of metal-organic frameworks using a hybrid diffusion-transformer architecture, Nat. Commun., Article in Press (2026).</a></li>
</ol>

## 작성·검증

편집부(AEDAUT) root가 공식 초록·서론과 두 AIP의 본문·조건을 읽고 집필했다. aps_quantum_survey·aps_condensed_survey가 Directional의 SI·자원 피팅·토러스 조건·공식 맥락을, brief_format이 EGMOF의 지표·학습 비용과 한영 대응을 비작성자로 감수했다. 자체 수치 도표와 모듈 개념도, 상세 비교·기획·접근 범위는 공개 PDF에 담았다. 원 그림은 두 논문의 NCND 조건에 따라 사용하지 않았다. Editorial Method v2026.08과2026-11-27 개정 모델·문체·설명 기준을 적용했다. 원호·웹 작성·추가 근거 기준일은2026-11-28이다. 논문 모사·학습·GCMC·DFT를 재현하지 않았으며 별도 사람 감수는 기록되지 않았다. {{AI_MODEL_DISCLOSURE}}
