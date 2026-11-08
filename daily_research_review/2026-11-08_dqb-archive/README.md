# 2026-11-08 Daily Quantum Brief 공개 보관본

원 DQB 4쪽의 공개 보관본을 제작한다. 원문 대조에 따른 정정·조건 1쪽과 APS 참고문헌 1쪽을 덧붙인다. 아카이브 등록과 신규 심층 리뷰 게재는 별도 상태로 관리한다.

## 제작과 검수

`artifacts/build_public_archive.py`는 호출자가 제공하는 원 PDF·폰트·비공개 QA 경로를 사용한다. 원본 해시와 4쪽 구성을 확인하고, 선언한 삭제·정정 영역 밖의 144 dpi 픽셀 동일성을 검사한다. 재빌드는 `public_reviewed`와 시각·독립 감수 상태를 초기화한다. 원본·메일·원 논문·QA 화면은 저장소에 넣지 않는다.

수집·소셜 경위와 내부 메모를 실제 삭제하고 원문 진입점 여섯 개를 유지한다. APS 목록은 본문·표 최초 인용순 [1]–[6]으로 원저자·원제·판본을 갖춘다. 출판사 Article in Press의 권·논문번호를 추정하지 않는다. 실제 원문 열람 범위·역할과 미확보 자료는 `reports/reference-manifest.json`, 최종 문서 검수는 `notes/production-qa.json`을 따른다.

## 원문 대조에 따른 정정

- QeMCMC는 고정 K=532의 단일 sparse Gaussian QUBO instance에서 얻은 단계당 감쇠율이다. 49변수 블록 proposal과 Kawasaki pair-swap 단계의 작업량을 구별한다. 선행 연구의 별도 회로·문제 조건을 이 하드웨어 실험의 성능 추세로 합치지 않는다.
- RSU-QSCI의 샷 비교는 exact FCI 입력·8 seeds 평균의 N2/STO-3G(10e,8o) 무잡음 모사다. 고정 spin sector의 3,136 determinants와 SCI 보존 상한 2,000, 별도 GQE ground-state 변형의 candidate 상한 100,000을 구별한다. 동일 보존 상한이 실제 동일 CI 차원을 보장하지 않는다.
- Josephson trijunction의 DC bias는 중심 위상을 진행시킨다. 정해진 모드·위상차 선택과 실제 시간 진화를 구별했다. Duality scattering은 36개 system sites와 8개 unary ancilla를 명시하고, Hamming weight=1의 유효 결과와 momentum sector별 활용을 구별했다.
- Kerr-cat의 TX=448±57 s는 평균 광자 수 33.8의 기록이며 그 조건의 TZ를 측정했다고 쓰지 않는다. 두 시간을 함께 측정한 광자 수 24.2의 TX=3.55±0.23 s, TZ=113±24 ns와 4 μs readout당 flip 확률을 기록했다.
- 응답함수의 여섯 route는 자원 척도·정밀도 정의를 변환해 읽는 이론 비교 지도다. 서로 다른 관측 대상의 수치를 한 순위로 합치지 않는다. 예고된 별도 SM A–J를 확보하지 못한 범위를 명시한다.

root는 원 4쪽과 보관본 6쪽 전체의 본문·렌더를 확인했다. 독립 조사 담당 dqb1108_sampling은 [1] 및 선행 연구, dqb1108_chemistry는 [2·6], dqb1108_hardware는 [3–5]를 원문과 대조했다. [6]의 공식 코드 패키지 41개 파일 해시를 확인했으며 수치 실험은 실행하지 않았다. 원 연구의 QPU·실험·화학 계산 재현이나 사람 독자 평가를 수행한 기록으로 해석하지 않는다. 공개 등록·배포·실제 URL 확인은 총괄 담당이 별도로 기록한다.

최종 독립 감수: dqb1108_hardware는 6쪽 전체와 개인정보·URI·동작·픽셀 보존을, dqb1108_chemistry는 [2·6]의 수정 조건·서지·열람 범위를 최종 SHA256 `a9954a26d053c33b8a3342d96aea0b5e26e81af021cb26cca29255f9fe06a800`에 대조해 통과를 기록했다. strict pypdf 경고는 0개다. PDF 태그 접근성이나 실제 독자 평가는 이 검수에 포함하지 않는다.
