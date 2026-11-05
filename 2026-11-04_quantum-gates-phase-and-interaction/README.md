# 양자 회로를 읽는 물리학

2026-11-05 · AI Tech Review Letters · Quantum Computing

단일 큐비트의 상대위상에서 CNOT–Rz–CNOT의 패리티와 ZZ 상호작용을 거쳐, 작은 MaxCut 문제의 답을 측정하기까지 따라가는 기술 해설이다. 스핀의 에너지·시간발전·회로의 생성자를 연결하고, 직접 진폭을 더해 상쇄가 생기는 한 자리를 계산한다. 삼각형 예제는 결합 구조에 맞춘 각도 선택을 보여준다.

## 원고와 자료

- [한국어 원고](reports/review_ko.md) · [English manuscript](reports/review_en.md)
- [승인한 기사 기획](article-plan.md) · [설명 설계](review-explanation-brief.md) · [표지 기획](cover-art-brief.md)
- [행렬 보충 유도](artifacts/gate-derivation.md) · [검산 코드](artifacts/check_examples.py) · [계산 기록](artifacts/example-checks.json) · [원전과 APS 서지](artifacts/reference-manifest.json)
- [표지](artifacts/hero.webp) · [최종 생성 프롬프트](artifacts/hero-prompt.txt) · [표지 제작 정보](artifacts/cover-spec.json)

한영 전문·수식·서지와 독립 과학·설명 감수를 마쳤다. 한글 11쪽·영문 12쪽 PDF의 전23쪽과 원본·모바일 도식 12개를 개별 시각 검수했다. 한영 1440/390px 화면, 계산 도구의 세 단계·각도 보존·초기화·키보드 조작과 인용·내장 글꼴·출력 해시 검사를 통과한 발행 패키지다. 폴더의 11월 4일은 기획일이며 발행일과 근거 기준일은 11월 5일이다.

## 계산과 의미

기저는 왼쪽 비트부터 쓰는 00·01·10·11이며 CNOT은 왼쪽 a가 제어, 오른쪽 b가 표적이다. 점수 C를 최대화하는 Farhi–Goldstone–Gutmann 원전 규약을 따라, 문제 위상 exp(−iγC) 다음 혼합 exp(−iβΣX)을 적용한다. SDK의 비트 문자열 표시 순서와 본문의 수학 기저를 혼동하지 않는다.

한 간선의 점수는 C=(I−ZZ)/2이고 γ=π/2, β=π/8에서 최적해 확률은 1이다. 삼각형에서 같은 각도는 평균 점수 0.75, γ=arctan(1/√2)·β=γ/2에서는 평균 점수 2를 준다. 원고는 두 결과를 함께 읽으며 각도 재선택을 설명한다. 두 예제 모두 리뷰의 이상적 상태벡터 교육 계산이다.

원본 도식은 phase_readout·parity_interaction·problem_to_probability의 한영 데스크톱·모바일 판본 12개다. phase-widget.js는 브라우저에서 복소 진폭·확률·기댓점수를 계산한다. 한 간선과 삼각형, 세 단계, 각도 조절·재설정·해석해 예제를 제공한다. 독립 NumPy 계산과 86설정×3단계를 대조한 최대 차이는 4.3×10⁻¹⁵ 이내였다. 실제 DOM의 해석해 각도는 1e−14 이내로 보존되며, 모바일 제어·초기화·키보드 조작을 별도 확인했다.

## 표지

두 파동형 종이 띠가 어긋난 리듬을 지닌 채 만나 밝은 마루와 깊은 골로 펼쳐진다. 상대위상이 후속 간섭에서 결과에 영향을 주는 관계를 독립된 종이 부조 비유로 표현했다. 주름의 개수·높이는 큐비트 수나 정량 확률에 대응시키지 않는다. 내장 image_gen으로 새로 생성했으며 외부 작품의 픽셀은 입력하지 않았다. 최종 그림을 자르거나 기하를 보정하지 않고 RGB WebP로 인코딩했다.

전체 그림, 320×180, 390px 및 흑백을 실제 확인했다. 두 입력·만남·펼쳐진 명암이 유지된다. 최종 WebP는 1672×941이며 EXIF·GPS·XMP가 없다. 원문과 공개 한영 캡션·alt는 표지 제작 정보에 보존한다.

## 실제 역할과 검증 범위

- root: 한국어 집필, 개념 표지, 설명·편집 통합과 게시.
- gate_article_physics: 원전·서지 대조, 별도 상태벡터 검산, 한영 원고·도식·위젯의 과학 검토.
- gate_article_editorial: 영어 전문 번역, 한국어 설명 검토와 한영 대응 감사.
- agent_standards: 원본 한영 반응형 도식·계산 도구, 글꼴·HTML/PDF 제작과 실제 출력 검수.

작성 시스템은 OpenAI Codex이며 정확한 모델 식별자는 보존되지 않았다. 편집자가 기사 기획을 승인하고 게시를 요청했다. 전체 원고의 감수는 AI 에이전트가 수행했으며 사람의 문장 단위 승인과 독자 이해도 실험은 별도 수행 기록이 없다.

Peruzzo와 Barenco는 출판 서지와 저자 공개 원고의 접근 범위를 구분해 기록했다. 공식 게이트 문서는 확인일의 현행 정의를 사용하며, 실행하지 않은 QPU나 숫자 SDK 판본을 추정해 적지 않는다. 재현 코드의 NumPy 2.0.2와 공식 권장 인용을 함께 밝힌다.

## 제작과 배포

artifacts/build_figures.py, build_fonts.py, build_review.mjs, build_pdf.py가 도식·폰트·HTML·PDF를 만든다. 런타임과 글꼴 경로는 명령 인자나 환경 변수로 전달한다. 공개 리뷰에는 최종 한영 HTML·CSS·표지·명시한 SVG·계산 도구 JS·PDF만 배포한다. 계산 코드와 기록은 저장소 원본에 연결한다. 원문 수집·내부 메모·QA 화면·호스트 절대경로는 공개 기사에 포함하지 않는다.

## 공개 페이지와 파일

- 한국어: https://infant83.io/AI_Tech_Review/reviews/2026-11-04_quantum-gates-phase-and-interaction/
- English: https://infant83.io/AI_Tech_Review/reviews/2026-11-04_quantum-gates-phase-and-interaction/en/
- [한국어 HTML](dist/index.html) · [한국어 PDF](dist/review_ko.pdf)
- [English HTML](dist/en/index.html) · [English PDF](dist/en/review_en.pdf)

한글 PDF는 3,446,989바이트, 영문 PDF는 3,367,770바이트다. 최종 자산의 허용 목록·출판 원본·해시는 figure-manifest.json에 기록한다. 실제 배포와 HTTPS 대조 결과는 내부 게시 기록에서 별도로 확인한다.

로컬 게시 검사에서 공개 파일 2076개를 확인했고 오류는 0건이었다. 다른 리뷰 52개·기존 아카이브 문서 107개·독자 기록 58개와 업데이트 기록 128개를 보존했다. 기존 리뷰·렉처·아카이브 파일 1876개는 바이트가 같고, 렉처 허브 두 페이지는 자료 수 107→109와 그에 따른 버전만 바뀌었다. 언어별 PDF의 dist·아카이브·사이트·사이트 아카이브 네 사본이 일치한다.
