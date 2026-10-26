# 평탄밴드와 관측량에 맞춘 동역학 리뷰

2026-10-26. 10월 24일 후보의 중복성 재검토와 10월 26일 DQB를 종합해 두 개의 한국어 심층 원고로 발전시켰다. 사용자의 flat-band 관심을 반영하고, 서로 다른 물리와 알고리즘의 성능을 한 주장으로 묶지 않는다.

- [평탄한 밴드에서 분수 위상상까지](reports/flatband_review_ko.md): 단층 ReAg2Cl6의 자기질서·SOC·Chern 밴드와 flat-band-limit 다체 진단. 기존 적층 위상상 글과 달리 고유벡터·투영 상호작용·PES 계수로 새 설명을 구성한다.
- [관측량과 항의 크기에 맞춘 양자 동역학 계산](reports/dynamics_review_ko.md): StateDRIFT와 norm-aware product formula의 서로 다른 설계 변수·오차·자원, 정확한 새 교육 계산과 실패 조건.

## 실제 계산과 독립 확인

1. `artifacts/compare_flatbands.py`: 같은 평탄한 에너지에서 C=0과 C=-1이 가능한 두 밴드 반례. 31/61/121 격자·위상 게이지·스펙트럼 평탄화와 scale 비교. [수치](artifacts/results/flatband-toy.json), [별도 해석 곡률 감사](notes/flatband-calculation-audit.md).
2. `artifacts/check_pes_counting.py`: 원저자 공개 Figure 4 데이터의 낮은 PES 가지 1088/1088/168을 원자료·조합식·직접 계수로 대조. [결과](artifacts/results/pes-counting.json). ED/PES 재실행은 아니다. 원 XLSX는 개인/임시 보관 영역에만 둔다.
3. `artifacts/compare_dynamics.py`: 한 큐비트 비가환 모형의 결정론적 곱 공식과 정확 qDRIFT 평균·분산 비교. 교육 oracle 탐색은 StateDRIFT allocator의 구현이 아니다. [결과](artifacts/results/dynamics_comparison.json).
4. `artifacts/verify_dynamics_bloch.py`: 별도 SO(3) 회전·1차/2차 모멘트로 기대값·편향·분산을 독립 검산. [감사 수치](notes/independent-dynamics-audit.json).

## 기존 글과의 차이

평탄밴드는 10월 1일의 적층 위상질서 소개에서 단층 자기 밴드·단일밴드 투영·PES 진단으로 범위를 옮긴다. 동역학은 10월 3일 VQE와 10월 21일 혼합 추정량의 최종 에너지 측정 배분에서, 실제 시간발전 항의 확률과 분할 공식을 바꾸는 문제로 들어간다. 강상관 전극 로드맵은 기존 DMFT 서문의 보강 후보로, AI 에이전트 회로 최적화는 10월 19일 및 25일 플랫폼 리뷰의 업데이트 후보로 남긴다. Mamba-QE·Fokker-Planck·PQK는 오늘 DQB에 보존하되 이번 두 원고의 주제를 늘리는 데 사용하지 않는다.

## 상태와 범위

두 원고·새 교육 계산·원자료 계수 확인을 보존한 단계다. 정식 표지·영문 전문·최종 PDF·리뷰허브의 새 기사 게재는 완료했다고 표시하지 않는다. 오늘 DQB는 별도 공개용 정정판으로 등록·게시한다. 원문·수집 메일·QA 화면은 공개 사이트 자산에 포함하지 않는다. 사람의 문장별 감수·독자 이해도 평가는 수행하지 않았다.
