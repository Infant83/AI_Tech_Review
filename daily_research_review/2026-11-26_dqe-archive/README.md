# DQE · 2026-11-26 · 함께 멈추는 공급망의 조달 선택

전자부품 공장의 합성 긴급 조달 문제다. 같은 주문을 공동 중단 시나리오마다 평가하며 기대 부족 비용과 전량 충족 확률을 구별한다. 한영 안내는 예비 물량의 판단, 서비스 제약을 보존한 이차화, 제약 전처리와 실제 의사결정 시간을 연결한다. 수치 풀이와 Go/Pivot/No-Go 판정은 기본 접힌 영역에 있다.

- 원호·근거 확인·웹 안내 작성일: 2026-11-26.
- 문제: PDF 1쪽. 해설: 2쪽부터. 비교·판단: 4쪽. 참고문헌: 5쪽.
- 공개 경로: `briefings/exercises/2026-11-26/`와 `briefings/exercises/2026-11-26/en/`.
- 공개 PDF: `dist/2026-11-26-daily-quantum-exercise.pdf`와 같은 bytes의 아카이브 등록본.

## 과학·출처·한영 검토

AEDAUT의 별도 담당자가 원 PDF 5쪽의 전체 추출문을 읽고 조건·단위·수식·답을 대조했다. `artifacts/science/verify_exercise.py`는 표준 라이브러리 유리수 산술로 주문 8개와 이차화 할당 16개를 계산한다. Boolean 다항식의 계수를 독립 복원하고, MILP 위반 지시자의 존재와 원래 확률 제약의 동치, 벌점 경계·전처리·스트레스·전체 시간을 확인했다. `calculations.json`과 `scientific-reference-audit.json`에 결과·자료 식별·실제 열람 범위와 원고 해시가 있다.

공식 웹 출처 4건의 관련 본문을 직접 읽었다. Gurobi의 ICRON 제약기업 적용 사례는 익명 고객에 관한 공급업체 보고이며 출판일을 표시하지 않는다. Multiple scenarios는 Gurobi Optimizer Reference Manual 14.0, D-Wave의 두 문서는 Ocean SDK 9.5.0 표시를 확인했다. 원문 제목·기관·해당 URL·확인일을 APS 기준으로 한영 및 PDF에 맞췄다. 학술논문 전문을 읽은 것으로 표시하지 않는다.

기존 분자 역설계 리뷰의 BQM 구성·정확 해·QPU 비교 절을 한영으로 읽고, 원래 제약과 반환 표본의 검증·임베딩 자원에 관해 연결했다. QML 11강은 국문 자원 계산·라우팅·shots와 시간 설명을 읽어 QAOA 확장에 연결했다. 어닐링과 게이트형 회로의 비용표를 혼용하지 않는다. 실제 기업 데이터 분석·MILP 제품 실행·회로 모사·QPU 실행은 수행하지 않았다.

한영 본문·목록 제목·별도 요약은 독립 감수했다. 양의 부족 비용이 최적해에서 부족량을 정한다는 조건을 국문에 명시하고, 제약기업이라는 표현으로 pharmaceutical 사례를 구체화했다. 현재 브리핑의 허용 HTML에 맞춰 정책 비교는 네 항목 목록으로 제공한다. 원고를 연속해 읽고 가까운 DQE와 비교해 일반적 가치 평가나 고정된 한계 종결을 덧붙이지 않았다. 사람의 별도 문장 검토·독자 이해도 평가는 수행하지 않았다.

## PDF 보존과 공개 적합성

원본은 공개 저장소 밖에 보존한다. 공개판은 1–4쪽의 추출 텍스트와 144 dpi 픽셀이 원본과 같으며, 5쪽의 세 편집 영역 밖 픽셀 변화는 없다. 원호 날짜·과학 내용·출처 HTTPS URI 4개를 유지하고 내부 전달·학습 이력을 삭제했다. 5쪽 제목과 정식 서지·공개판 안내를 보완했다. `artifacts/build_public_archive.py`는 입력과 폰트를 호출자가 제공하는 재현 도구다.

PDF 담당자는 원본 5쪽, 최종 PyMuPDF 144 dpi 5쪽과 독립 Poppler 110 dpi 5쪽을 전부 렌더해 읽었다. 총괄 담당자도 최종 5쪽을 독립 열람했다. 잘림·겹침·누락 글자 없이 문제·해설·수식·서지·쪽 번호가 읽힌다. 엄격 파싱·본문 개인정보·메타데이터·XMP·URI·첨부·자동 실행·폰트의 배포 조건을 확인했다. 추가 임베딩 폰트의 수정 명칭·저작권·판본·OFL·권한 정보를 보존했다. 자세한 결과는 `artifacts/public-pdf-qa.json`에 있다.

공개 PDF는 5쪽, 87,039 bytes이며 SHA-256은 `24c8cfccd15b6a393733c6e750ded36aad53e82f931d10fe3faeb5b6f968f2df`이다. 원 첨부 해시·메일·수신 이력·비공개 링크·QA 화면·내부 경로는 공개하지 않는다.

## 등록과 공개 검증

검수 PDF를 `daily-quantum-exercise` 시리즈의 `2026-11-26-daily-quantum-exercise`로 등록하고, `scripts/build_briefing_editorial.py`로 한영 안내를 컴파일했다. 기존 DQB·DRB와 원호 날짜·주소를 보존한다. ADOPT이 실제 공개 baseline과 독립 후보·달력·검색·언어 전환·접힌 해설·모바일·PDF 열기/다운로드 및 배포를 검증한다. 단계별 결과는 `artifacts/publication-qa.json`을 따른다. 실제 HTTPS 확인 전에는 게시 완료로 표시하지 않는다.

## 공개 완료 · 2026-11-26

[한국어 안내](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-26/)·[English guide](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-26/en/)·[검수 PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-26-daily-quantum-exercise.pdf)를 실제 HTTPS로 확인했다. 소스 `db790e12a4c406e25308dc46e314f9b092d4f72e`의 [배포 작업](https://github.com/Infant83/AI_Tech_Review/actions/runs/45833052212)에서 실제 Pages 게시 단계와 build·deploy·recovery-copy·notify-readers가 모두 성공했다. 전체 CI는 1,134건 중 1,125건 통과·9건 건너뜀·실패 0건이다. 로컬 등록·브리핑·검색 검사 95건과 Node 검색·탐색 12건도 통과했다.

390×844 한영 브라우저 검사 20건과 화면 12장을 감수했다. 기존 달력 ID 106개·날짜별 한영 본문 72개·기존 PDF 경로 295개의 보존을 확인했고, DQE 8건은 실제 새 탭·다운로드 bytes를 대조했다. Nov26의 기존 DQB 한영 본문·PDF를 유지하며 미수신 DRB를 만들지 않았다. 총괄 담당자도 모바일 화면 10장을 독립 열람했다. 실제 HTTPS는 총괄 14건·별도 운영 담당 34건을 대조해 모두 통과했다. 공개 한영 본문 전체와 새 PDF가 후보와 정확히 같고 DQE 8건의 HTTPS PDF해시가 승인본과 일치한다.

복구 사본은 2,793파일·864,384,684bytes이며 CI에서 정확한 배포물의 검증·업로드를 확인했다. 전체 복구물을 로컬로 내려받거나 복원하지 않았다. 독자 카탈로그83건 동기화는 성공했으며 새 article과 알림 대기 event는 각각0건이다. DQE독자 알림을 보냈다는 뜻으로 표시하지 않는다. 완료 기록을 남기는 동안 원고·컴파일 본문·PDF는 수정하지 않았다.
