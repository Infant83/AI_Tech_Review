# 재료 계산에서 QRAM까지

2026-08-26 발행·근거 기준, 2026-11-06 편집 개정. 정본은 `reports/2026-08-26_quantum-computing-layers_final_review.md`다. 기존 제목·URL·허브 요약·표지를 유지하며 원문 지표·인용과 설명을 다듬었다. 자세한 수정·감수 범위는 [개편 기록](../.automation/writing-reviews/legacy-refresh/2026-11-06-quantum-layers/README.md)을 따른다.

`artifacts/final_review/build_review.py`가 정본을 기존 `layout.html`에 렌더링하고 그림·당시 브리핑 공개 사본을 `dist/`에 복사한다. `publish_review.py`는 보존한 공개 metrics 설정으로 해당 글을 게시한 뒤 공통 허브를 갱신한다. 원고 대신 공개 HTML만 고치는 방식으로 제작하지 않는다.

`build_public_briefing.py`는 호출자가 제공하는 비공개 원본 PDF를 받아 수집·소셜 경위·내부 메모와 Author 정보만 삭제한다. 원본·QA를 저장소에 넣지 않으며 선언 영역 밖 텍스트·144 dpi 픽셀과 원문 URI를 비교한다. 생성된 `artifacts/public-assets/daily_quantum_brief_2026-08-26.pdf`는 발행 당시 과학 본문을 유지한 공개 사본으로, 웹 리뷰의 정정 이력과 구별한다. 동일 ID의 아카이브 파일·기사 연결 파일·사이트 사본을 함께 확인한다.

새 번역·기사 PDF·표지·영상은 추가하지 않았다. 표지 원화·QRC 수치 도표를 보존하고 계산 대상 SVG의 라벨만 정정했다. 재현한 것은 원고의 출력과 공개 정보 정리 절차이며 원 논문·QPU 실험·학습을 재현한 작업은 아니다.
