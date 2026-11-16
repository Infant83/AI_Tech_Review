# DQE · 다음 촉매 실험을 정하는 에너지 차이

원호 날짜와 근거 기준일은 2026-11-16이다. 사용자가 승인한 DQE 일일 보관·짧은 한영 안내 범위에서 편집부(AEDAUT)가 작성·과학 감수하고 운영팀(ADOPT)의 기존 출판 도구로 등록한다. 같은 날짜 DQB·DRB의 ID·주소·본문을 유지한다.

## 내용과 실제 열람

가상 촉매의 반응 장벽 보정, 명목 순위와 최악 오차에서의 순위 보장, 네 고정 구조의 VQE 역할과 측정 예산을 다룬다. 모델·솔버 오차가 각각 어떤 검증을 요구하는지와 실험 추천·전체 처리시간의 연결을 안내한다. 숫자 정답·풀이·판정은 한영 웹에서 기본 접힌 영역에 둔다. 관련 HI-VQE 리뷰는 서로 다른 알고리즘임을 밝히고 전자구조의 양자·고전 분업과 정확도·전체 시간의 비교로 연결한다.

`root`의 집필·통합과 별도로 `dqe_science`가 산술·오차의 16개 부호 조합·단위·알고리즘 역할·원출처·한영 본문·별도 목록 요약을 읽었다. Jacobsen 논문은 출판사·연구기관 서지를 확인했고 본문은 읽지 못했다. CI-NEB 저자 공개 논문 4쪽을 읽었으며, Hempel 논문은 출판사 초록·공개 요약·서지 및 원문 초록·서론·매핑 설명을 확인했다. 22쪽 전체를 읽거나 원 실험을 재현하지 않았다. 실제 열람 범위와 정식 서지는 [감수 기록](artifacts/scientific-reference-audit.json), 산술 재현은 [검산 코드](artifacts/verify_exercise.py)와 [계산 결과](artifacts/exercise-calculations.json)에 남긴다. 사람의 문장별 감수나 독자 평가를 수행한 것으로 표시하지 않는다.

## PDF 공개판

4쪽 공개 파생판은 과학 문제·해설·수식·원호 날짜와 원 출처 세 링크를 보존한다. 4쪽의 이전 주제·내부 이력 메모를 제외하고, 세 참고문헌의 전체 저자·정식 제목과 CI-NEB DOI 링크, 공개 편집·AI 보조 검수 이력을 보완했다. 제3자 논문 그림은 복제하지 않았다.

`dqe_pdf`가 원본·공개판 4쪽을 모두 렌더해 읽고 파일을 검사했고, `root`가 원본과 최종 공개판의 8개 렌더를 독립 확인했다. 선언한 4쪽 두 영역 밖의 144 dpi 픽셀과 1–3쪽 추출 본문이 같다. 엄격 파싱·메타데이터·개인정보·URI 4개·첨부·자동 실행 검사 결과는 [PDF QA](artifacts/public-pdf-qa.json)에 기록했다. 원본·메일 식별정보·QA 화면은 비공개 보존한다. 공개 PDF SHA-256은 `a4a06b8b0c537b18832e9c0d55052c6511375d2cde5932cde1ed1c4ccb084a07`이다.

## 등록과 공개 검증

검수 PDF는 `2026-11-16-daily-quantum-exercise`, `daily-quantum-exercise`로 등록했고 한영 원고는 기존 컴파일러를 사용했다. [한국어 안내](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-16/)·[영어 안내](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-16/en/)·[PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-16-daily-quantum-exercise.pdf)를 공개했다.

실제 이전 배포 `d8eb871ea3ade13967e169f7eea13b9246c1340a`를 기준으로 만든 독립 후보는 새 DQE 한 건만 추가했고, 기존 한영 브리핑 24개 페이지는 바이트 단위로 같았다. 필요한 로컬 Python 67건과 검색·탐색 12건을 통과했다. `archive_architecture`가 Chromium의 390×844 화면에서 두 언어·접힌 해설의 마우스와 키보드 동작·언어 전환·같은 날짜의 세 시리즈·검색·DQE 분류·PDF 열기·실제 다운로드를 검수했다. `root`도 모바일 진입·펼친 해설·달력·검색 화면을 확인했다. QA 화면은 비공개 보존한다.

출판 소스 `4b0c294034f1936f721f059902a735b470fe4ee6`의 [배포 작업](https://github.com/Infant83/AI_Tech_Review/actions/runs/43874538422)은 build·deploy·recovery-copy·notify-readers 모두 성공했다. CI 테스트는 906건 중 897건 통과·9건 건너뜀·실패 0건이다. 복구 사본은 CI가 정확한 배포물 2,660개 파일·805,668,952바이트를 검증하고 업로드한 결과이며, 이 작업에서 로컬 복원 시험은 하지 않았다. 기존 리뷰·렉처 알림 카탈로그 73건 동기화가 성공했으며, DQB·DRB와 마찬가지로 새 DQE를 별도 알림 기사로 등록한 것은 아니다.

별도 담당자 `heartbeat_public_check`의 실제 HTTPS 검사와 `root`의 query 없는 공개 주소 GET 검사에서 한영 전체 HTML·본문과 PDF가 검수본의 SHA-256에 일치했다. 원호 날짜·기본 접힌 해설·언어/PDF 링크·기존 canonical 리다이렉트·이전 DQE 및 같은 날짜 DQB·DRB 보존도 확인했다. [공개 검증 요약](artifacts/publication-qa.json)에 실제 범위와 해시를 남겼다. 과학 본문과 PDF에는 완료 기록을 위해 추가 변경하지 않았다.
