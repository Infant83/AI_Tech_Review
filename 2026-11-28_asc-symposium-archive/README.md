# ASC Symposium2026 공개 세미나 노트

책임 편집자 김현중 · AI 보조 OpenAI Codex · 공개판 기준일2026-11-28

NHR-Atomistic Simulation Center Symposium2026에서 확보한 일곱 발표의 일부를 정리한 한국어 그림 보강판v2를 공개 보관한다. 원판44쪽의 수식·그림26개·문답·원래 쪽번호와 근거 구분을 보존하고, 공개판의 기록 범위·그림 크레딧·정식 원자료 안내5쪽을 더한49쪽이다. 별도 온라인 중복 본문이나 새 시리즈 묶음을 만들지 않고 기존 렉처 노트와 통합 필기 리더에서 읽는다.

## 내용과 판정

Julien Steffen의 미세조정·동역학, Omid Shayestehpour의Prokyon, Martí Raya Moreno의exciting 분광학, Birte Höcker의효소 설계, Philip Loche의전극 계면, Lu Qiao의펌프-프로브 해석, Moritz Leucke의대규모RPA를 다룬다. 원판은 화면에 표시된 자동 자막과 공유 화면의 부분 기록이며 전체 발표 전사나 직접 음성 청취 기록이 아니다.

원판의 `checked_with_open_items`를 유지한다. RPA 정규화·spin·Green/Fourier 부호, 가려진 식과 축, Prokyon 단위·불확실성 보정, 효소 실험 조건, 서로 다른 하드웨어와 계산 단계의 비용, 불완전 문답의 열린 조건을 보존한다. 원판44쪽 전체와 기존 최종 학술 감수 기록을 읽고, 선택한1차 문헌의 식·초록·서지 및 그림 출처를 대조했다. 새로운MLIP·DFT·MD·BSE·RPA·HPC·fit·효소 실험이나 원판 전체 계산 묶음을 재실행하지 않았다.

## 그림과 공개 범위

26개 그림은 본문의 방법·결과·비교 조건을 설명하고 비평하는 데 필요한 발표화면 일부의 인용이다. 각각의 원래 과학적 내용·축·수치·색·가림과 보이는 크레딧을 유지한다. `artifacts/figure-credits.json`과 PDF46–49쪽에서 발표자·발표명·행사·확인 가능한 원논문 및 발췌·한국어 캡션의 관계를 연결한다. 자유이용허락이나 발표자의 감수를 받은 판본으로 표시하지 않는다. 관련 논문·모델·슬라이드의 권리 대상을 구분하며, CC BY와CC BY-NC-ND의 제삼자 예외·조건을 원자료별로 남겼다. 개별 원본 슬라이드나 이미지 갤러리는 배포하지 않는다.

원판의S/C/Q/R/A와 observed·derived·external·open은 원판의 근거·해석 표식으로 유지한다. 본문 원래 글자·페이지·그림은 그대로이며 숨은 로컬 파일 링크13개는 공개판 내부의 검토 범위12개·그림 크레딧1개로 바꿨다. 개인 메일·원본 첨부·전체 회의 캡처·생자막·내부 원장·QA 화면·비공개 경로는 공개 파일에 포함하지 않는다.

## 제작·감수와 AI 활용

원문·PDF 보존·전체44쪽 및 새 부록5쪽의 개별 시각 검수는 `symposium_pdf_review`, 과학·권리·그림·서지 대조는 `symposium_science_rights`, 한영 소개와 독립 등록·연속성 검수는 `symposium_archive_audit`, 편집·등록·발행 통합은 `root`가 담당한다. AI Tech Review Editorial Harness2026.08, 저장소의 과학 설명 준칙·독자 진입 감수·APS 인용 기준을 적용한다. 사람의 전체 문장 감수나 실험 재현으로 표시하지 않는다.

`artifacts/ai-model-provenance-source-v2.json`은 보존된 원판v2 집필 턴설정을 소급 대조한 원판 집필 역할 기록이며, 원 작성의 다른 감수자까지 추정하지 않는다. `artifacts/ai-model-provenance-archive.json`은 이번 편집·원문 대조·과학 감수·PDF 제작·독립 감수·발행 감수의 실제 기록이다. 두 기록의 확인 가능한 설정은gpt-6.1-sol, 추론 강도ultra이며 클라이언트 턴설정의 증거다. 현재 기본 설정이나 서버 가중치 판본으로 과거 작업을 추정하지 않는다. 원 기록과 비공개 식별자는 공개하지 않는다.

## 출판 자산과 검증

- `dist/2026-11-28-asc-symposium2026-notes-ko.pdf`: 정제한 공개 보관판49쪽,6,065,485bytes.
- `reports/pdf-public-qa.json`: 원판44쪽의 문자·픽셀·26개 이미지·189개 이름 목적지·64개 목차·64개 내부 이름 링크·7개 공개HTTPS 보존과 전체 시각 검수.
- `artifacts/prepare_public_pdf.py`: 명시한 원판·검수 렌더·부록·저장한 모델 기록을 입력으로 공개판을 만드는 도구. 원 저술·메일·계산 파이프라인은 실행하지 않는다. 새 부록 폰트만113,068bytes로 부분집합화하며 원판 폰트는 보존한다.
- `archive/entries/2026-11-28-asc-symposium2026-notes-ko.json`: 고정 문서ID·발행일·한영 소개의 원본 등록.

공개 PDF SHA-256: `72d042cea809785ede0f795570bb535e81566a53baae8db36a6a51df1d0e29b0`.

실제 배포 스냅샷을 기준으로 독립 후보의 이전 ID·날짜·PDF·필기 연결, 페이로드와 봉인된 배포물을 검증한다. 한영 모바일 목록·검색·필기 저장과 일반 새로고침·공개PDF를 확인하고, build·deploy·recovery-copy·notify-readers와 실제HTTPS 확인을 모두 마친 뒤에만 완료로 기록한다. 동시 작업의 최신 원격 게시를 보존하며 오래된 `site/` 전체를 덮어쓰지 않는다.

2026-11-28 게시 확인: 검수한 소스 `0fa2a07b73ce4afee3e4f326768930286dd7eead`의 [배포 기록](https://github.com/Infant83/AI_Tech_Review/actions/runs/46109864746)에서 build·deploy·recovery-copy·notify-readers가 모두 성공했다. 실제 HTTPS의 한영 목록·검색·필기 링크와 49쪽 PDF 해시, 이전 아카이브·PDF·필기 런타임의 연속성을 확인했다. 격리한 실제 Chrome에서 일반 서비스 워커와 기존 캐시를 유지한 채 새 문서를 불러왔고, 마우스로 만든 로컬 필기·책갈피·읽던 위치가 일반 새로고침 뒤에도 복원되며 기존 QAE 노트도 그대로 유지됨을 확인했다. 독자 동기화는 98개·새 글 1개·알림 큐 1건이며 개별 알림 수신을 확인했다는 뜻은 아니다.

[필기하며 읽기](https://infant83.io/AI_Tech_Review/lectures/reader/?id=2026-11-28-asc-symposium2026-notes-ko) · [공개 PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-28-asc-symposium2026-notes-ko.pdf)
