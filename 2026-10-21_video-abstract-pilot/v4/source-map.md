# v4 근거와 재현 자료

v4는 v3의 대표 계산과 HNN 구성에 발화 정의·시선 순서를 보완한 출력이다. 물리 모형과 수치는 바꾸지 않았다.

- R: [개정 노터 리뷰](../../2026-10-17_noether-symmetry-conservation/reports/review_ko.md), 특히§3·6·7·11.
- N: [Noether 원문 번역](https://arxiv.org/html/physics/0503066v3).
- M: [HMC mechanics chapter6](https://www.physics.hmc.edu/~saeta/courses/p111/uploads/Y2012/Ch06.pdf).
- V: [Marsden–West variational integration](https://lagrangeweb.web.engr.illinois.edu/var_int/).
- HNN: [Hamiltonian neural networks](https://arxiv.org/html/1906.01563).
- CALC: [공개 리뷰 계산 코드](https://github.com/Infant83/AI_Tech_Review/blob/main/2026-10-17_noether-symmetry-conservation/artifacts/build_figures.py), 초기값을 포함한 2,001개 표본을 사용하는 교육용 계산.
- DERIV: [본문의 계산과 해석](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/#section-6). v4는 작용·첫Euler단계·벨레 에너지 오차·HNN의 조건부 연속시간 보존만 사용하며, 예전v2의 별도 타원 반례·분자동역학 장면을 재사용하지 않는다.

`artifacts/render_review.py`는 전체 Euler 수열을(1+h²)^n과, velocity Verlet 상태를 독립 닫힌식과 비교한다. 별도 검토자의 독립 계산과 실제 encoded 검수는 qa에 보존한다. 영상의 diagram은 측정장치나 새 학습결과가 아니라 검증한 교육용 계산·방법구성이다. source·QA는 공개 기사로 복사하지 않는다. 공개 TXT에는 위 source code의 원문URL 대응표를 별도로 제공한다.
