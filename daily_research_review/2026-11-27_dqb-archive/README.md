# DQB 공개 보관과 한영 편집글 · 2026-11-27

원 DQB 3쪽의 과학 본문·도표 2개·호 날짜·과학 URI 13개를 보존하고, 계산 조건과 정식 APS 서지를 덧붙인 5쪽 공개 편집판이다. 원 3쪽의 수집 경위와 내부 체크리스트는 실제 삭제했다. 원 자료의 발행명·크레딧은 보존하고 새 편집 절에는 Agentic Tech Review Letters(ATRL)를 사용한다. 원본과 검수 화면은 비공개 보존한다.

공개 PDF는 239,528바이트이며 SHA-256은 `a52eaf6cf8231675a24205ac1c76c47c6b912bcfbab04607a1a5955a84a9c677`다. 원 과학 URL 6개와 13개 주석 좌표, 삭제 영역 밖의 본문 줄·144 dpi 픽셀을 보존했다. Poppler 144 dpi 화면을 전쪽 확인하고 엄격 파싱·메타데이터·URI·첨부·실행 동작·개인정보 검사를 별도로 수행했다.

## 원문 대조와 편집 범위

QAOA의 경계 수·깊이·문제 크기와 FakeBrisbane 잡음 모사 조건, 샷 감소에 함께 반영된 학습량 차이를 구별했다. 양자화학 비용 논문에서는 PT2 수렴 진단과 QPE 정밀도, CPU 요금과 미래 QPU 요금 가정, FeMoco 외삽법별 가격 범위를 설명했다. CutQAS의 저널판·이전 원고와 분할별 오차·회로 자원, Rydberg 측정의 회전 증강과 고전 PQMC 투영, LatentRL-QAS의 후보·표현 전이와 새 에이전트 학습을 구별했다. 원 도표의 수치나 과학 본문을 교체한 정정은 없다.

별도 한영 편집글 「P450의 기준 에너지를 다시 확인하다」는 같은 해밀토니안·스핀 조건에서 수렴한 두 계산의 약 31.8 mHa 차이에서 시작한다. 최종 궤도 순서가 같더라도 초기화와 최적화 이력이 다른 에너지에 머물 수 있다는 사례를 통해, 참조 상태 확인이 고전 난도와 양자 상태 준비·반복 비용의 판단에 미치는 영향을 설명한다. 기존 「양자 계산의 전체 비용을 설계하다」의 정확도·상태 준비 논의를 이어받으며 별도 목록 요약도 작성했다. 기존 글의 본문·제목·URL이나 승인 대기 기획 5건은 변경하지 않는다.

## 실제 역할과 한계

root는 원 3쪽 전체 텍스트·화면과 비용 논문의 본문·그림 설명·선택 부록, 기존 전체 비용 리뷰의 한영 관련 절을 읽고 편집글을 작성·통합했다. CutQAS 표 4·6과 LatentRL-QAS의 선택 결과·전이 조건도 추가 대조했다. `dqb1127_sources`는 QAOA v5와 Rydberg v1의 본문·통합 부록을 대조하고 기존 리뷰·기획 관계를 확인했다. `dqb1127_pdf`는 CutQAS 저널 본문·부록·표와 이전 v1의 관련 절, LatentRL-QAS 본문·선택 부록을 대조하고 공개 PDF를 제작했다. 공식 코드의 README·커밋 정보와 데이터 저장소 메타데이터 확인은 코드 실행·전체 데이터 다운로드와 구별한다.

비작성자 `dqb1127_publication_audit`는 비용 논문의 선택 방법·결과·부록을 따로 대조하고 한영 원고·제목·별도 요약·인용·작성 공개 정보를 감수했다. [비용 논문 검토](artifacts/source-audit-cost.json), [문헌별 실제 범위](artifacts/reference-manifest.json), [PDF 제작 검사](artifacts/public-pdf-qa.json), [한영 편집글 감수](artifacts/editorial-independent-review.json)를 구별한다. PDF의 비제작자 감수·명시 등록·후보·배포·실제 URL 확인은 별도 단계다.

책임 편집자는 김현중이며 AI 보조는 OpenAI Codex다. 정확한 모델 식별자는 미보존이다. Editorial Method v2026.08과 2026-11-26 개정 문체 감수 기준을 적용했다. 원 논문의 계산·학습·실험·증명을 재현하지 않았고, 이번 공개 편집판과 웹 원고의 별도 사람 검토·사람 독자 평가도 기록되지 않았다. 원 DQB의 작성 시스템이나 사람 검토 여부는 소급 추정하지 않는다. 원호 날짜·웹 작성일·추가 근거 기준일은 2026년 11월 27일이며 각각 표시한다. 새 심층 리뷰나 다른 기존 본문의 실질적 확장은 이번 작업에 포함하지 않는다.

최종 PDF의 [비제작자 전쪽 감수](artifacts/pdf-independent-review.json), [QAOA·Rydberg 담당 감수](artifacts/pdf-source-review-qaoa-rydberg.json), [root의 실제 추가 확인](artifacts/root-pdf-review.json)을 완료했다. 원문 대조의 [공개 범위 기록](artifacts/source-audit-qaoa-rydberg.json)도 보존한다. 측정 사진의 통계적 독립성을 단정한 표현을 좁히고 새 참고문헌의 APS sentence case를 보완한 뒤 최종 해시로 재확인했다.

## Publication candidate verification

The final candidate passed release policy, payload/seal checks, full static validation and one complete actual-byte inventory: 2,801 files including the seal, 59 reviews, 183 archive documents and 84 catalog articles. All 182 prior archive records, 299 PDF paths, 74 dated editorial pages plus the two NTCA pages, Classiq L018/course files and the Avatar revision were preserved. The payload adds only the reviewed PDF and two editorial pages; there are no removed paths or unrelated article changes. Existing payload/search size warnings remain recorded operational follow-ups.

The initial browser check found a manual byline repeating the current common builder's automatic responsible-editor/AI byline. Removing the first paragraph in each manuscript preserved the scientific text, references, footer, titles, summaries and PDF exactly. A fresh candidate and actual-byte inventory confirmed the final output; initial evidence remains private history. The 25 focused briefing tests passed on the first candidate and were reused because no test or implementation code changed. See the [independent preservation audit](artifacts/candidate-independent-review.json) and [editorial correspondence](artifacts/editorial-correspondence.json).

Root checked Korean desktop, both languages at a 390-pixel mobile viewport, language navigation, citation navigation, the selected calendar day, editorial-first controls and Korean keyboard search. The served PDF matched the registered bytes and the console warning/error list was empty. The owned tab, viewport override and preview server were cleaned up. [Browser evidence](artifacts/candidate-browser-review.json) distinguishes link/download-attribute and complete-byte checks from native PDF-viewer or click-to-save testing. Actual deployment and HTTPS verification remain separate.
