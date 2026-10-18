# Figure manifest

- 파일: `circuit_generation_workflow.svg`
- 제목: 생성형 AI를 이용한 양자회로 설계와 검증의 흐름
- 유형: 직접 작성한 벡터 개념도. 연구 논문의 결과 그림을 재현하거나 실험 수치를 제시하지 않는다.
- 크기: 1200 × 680 px, 흰 배경, 짙은 본문, 차분한 적색 강조. 운영체제의 한글 sans-serif 폰트를 사용한다.
- 작성일: 2026-10-19
- 목적: 문제와 제약 → AI 후보 생성 → 독립 검증 → 장치별 컴파일과 평가 → 채택 회로의 관계와 평가 피드백에 의한 수정 과정을 설명한다.
- 구분: 코드 에이전트, 게이트 시퀀스 모델, 확산·강화학습은 후보 생성의 서로 다른 접근이며 필수적인 순차 단계가 아니다.
- Classiq 표기: `LLM → Qmod 명세 → 합성기 → 게이트 회로`를 독립된 구현 예로 명시한다. Qmod는 해당 경로의 중간 표현이며 모든 생성 모델이 사용하는 공통 표현이라는 의미가 아니다.
- 평가 구분: 의미 정확도, 회로 비용, 실제 QPU 검증을 세 가지 독립 항목으로 제시한다. 시뮬레이션·동등성 검사 및 자원 추정만으로 실제 장치 성능이 확인된다고 표현하지 않는다.
- 도식의 추상화: 장치별 컴파일 후 의미가 보존되는지 재검증할 수 있으며, 실제 연구에서는 여러 단계가 반복된다. 본 그림은 주요 관계를 간결하게 표현한 것이고 특정 제품의 완전한 아키텍처가 아니다.
- 검토 완료: Python XML 파서로 문법·viewBox·텍스트 요소를 확인했다. Sharp로 원본 크기 1200 × 680 px의 PNG를 임시 경로에 렌더링한 뒤 전체 이미지를 시각 검토했다. 한글이 표시되며 텍스트 넘침·겹침 없이 주요 화살표와 세 평가 항목이 분리되어 보이는 것을 확인했다. 임시 PNG는 납품 파일에 포함하지 않는다.

## 개념 근거

- Anthropic, “Designing more efficient quantum circuits with Claude” (2026-10-16): https://www.anthropic.com/research/designing-efficient-quantum-circuits
- Gu et al., “Discovering state-of-the-art quantum circuits with large language models” (2026): https://arxiv.org/abs/2610.22367
- Classiq 공식 문서의 Qmod 및 합성 흐름: https://docs.classiq.io/latest/

위 출처는 개념 근거이며, 본 그림의 레이아웃·도형·문구는 이번 리뷰를 위해 직접 작성했다.
