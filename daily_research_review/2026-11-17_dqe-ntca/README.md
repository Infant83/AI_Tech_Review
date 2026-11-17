# 요청형 DQE · 비선형 진폭 변환을 세 플랫폼으로 옮기기

2026-11-17 발행용 새 교육 문제다. PennyLane의 [Nonlinear transformation of complex amplitudes](https://pennylane.ai/demos/nonlinear_transformation_of_complex_amplitudes)와 관련 원논문을 읽고, 근사 오차 없이 비교할 수 있는 세제곱 블록 곱으로 재구성했다. PennyLane을 포함해 Qiskit·Classiq의 구현과 검증 범위를 안내한다. 원 데모의 QSVT·분류기 학습 전체를 이식하거나 재현한 것으로 표시하지 않는다.

## 회차와 내용

당일 공개 DQE가 아직 없어 오늘자 요청형 회차로 작성했다. 메일에서 수신한 원호가 아니며 기존 정기 문제 생성·발송·확인 예약을 바꾸지 않는다. ID는 `2026-11-17-daily-quantum-exercise-ntca`, 한영 웹 주소는 `briefings/exercises/2026-11-17/ntca/`와 대응 `/en/`이다. 같은 날짜 정기 수신호의 ID와 날짜 주소를 별도로 유지한다.

PDF는 6쪽이다. 문제는 1쪽, 해설은 2쪽, 세 플랫폼 안내는 4쪽부터다. 새 작업 레지스터에 U로 상태를 준비한 뒤 주소를 XOR하고 모든 작업 0인 가지를 선택해 성분별 세제곱을 얻는다. 실수와 복소수 입력, 상태·성공확률·명시적 자원·준비 호출·위상 진단을 함께 검산했다. 숫자 정답과 플랫폼 실행 안내는 한영 웹의 기본 닫힌 details 안에 둔다. PDF SHA-256은 `75e5a4831ce00cf7e14e5c476663da5fcacb7e585333b4a83883291675cb7ac1`이다.

## 코드와 실제 검증

- [PennyLane](artifacts/platforms/pennylane/): 0.45.1, 로컬 default.qubit 무잡음 상태벡터. 실수·복소 입력의 두 경로, 추가 길이 2·4·8 입력, 대각 블록과 위상을 검사했다.
- [Qiskit](artifacts/platforms/qiskit/): 2.6.2, 로컬 Statevector. 같은 계산과 명시적인 비트 인덱스·기저 순서를 검사했다.
- [Classiq](artifacts/platforms/classiq/): 1.35.0, 네 로컬 모델 생성·JSON·클라이언트 스키마와 인위적 DataFrame 후처리 검사. 클라우드 합성·시뮬레이션·QPU 실행은 하지 않았다. `--cloud`를 선택하는 코드와 공식 인증 절차는 별도 안내한다.
- [독립 과학 검산](artifacts/science/): 별도 NumPy 회로, 정식 서지·열람 범위, 한영 대응과 최종 산출물 해시를 기록했다.

플랫폼마다 별도 Python 3.12 가상환경과 해당 requirements 파일을 사용한다. 실행 결과 JSON은 SDK 시뮬레이터의 결과와 수학적 기준값·모델 형식 검사를 구분한다. 원시 Classiq 모델의 소스·디버그 경로와 인증정보는 공개 산출물에 포함하지 않는다. 실제 QPU나 일반 QSVT 구현·원 분류기 성능을 재현한 기록은 없다.

## 제작과 발행 검사

편집부(AEDAUT)의 root가 문제·한영 원고와 PennyLane 코드를 집필·통합했고, dqe_science가 원출처·별도 계산·한영 글을 독립 감수했다. archive_architecture는 Qiskit과 같은 날짜 회차 보존, heartbeat_public_check는 Classiq과 공개 확인, dqe_pdf는 PDF 제작과 전 페이지 출력을 맡았다. 운영팀(ADOPT)의 기존 출판 도구를 사용한다. 사람의 문장별 감수나 독자 평가는 수행하지 않았다.

새 PDF는 원 저자의 코드·그림 전체를 복제하지 않은 독립 교육용 작성물이다. [PDF QA](artifacts/public-pdf-qa.json)는 전 페이지 렌더, 수식·글리프, URI 11개, 메타데이터·개인정보·첨부·실행 동작 검사를 기록한다. PDF 담당과 별도 통합 담당이 전체 출력을 확인했으며 QA 화면·자료 수집 원문·개인 경로는 공개하지 않는다.

요청형 회차가 정기 메일 원호를 덮어쓰지 않도록 DQE 보조 경로만 추가했다. 기존 발행호 주소·ID를 유지하는 단위·통합·보존 검사를 수행했다. 실제 이전 배포 `e5269e1ce2c205428c6d57be8fce5ec49a392c30`에서 새 DQE 한 건만 추가했으며, 기존 한영 브리핑 30개 페이지는 바이트 단위로 같았다. 같은 날짜 정기 DQE와 요청형 회차의 공존·검색·정확한 보존 경로도 별도 통합 검사했다.

## 공개 완료

[한국어 안내](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-17/ntca/)·[영어 안내](https://infant83.io/AI_Tech_Review/briefings/exercises/2026-11-17/ntca/en/)·[6쪽 PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-17-daily-quantum-exercise-ntca.pdf)를 공개했다. Chromium 390×844에서 접힌 해설의 마우스·키보드 동작, 언어 전환, 달력·목록·검색·분류와 PDF 열기·실제 다운로드를 확인했다.

출판 소스 `d3006ee39e6596150562672166ddcf5c0437bde6`의 [배포 작업](https://github.com/Infant83/AI_Tech_Review/actions/runs/44005850393)은 build·deploy·recovery-copy·notify-readers 모두 성공했다. CI 테스트는 911건 중 902건 통과·9건 건너뜀·실패 0건이다. 복구 사본은 정확한 배포물 2,671개 파일·807,912,518바이트를 CI에서 검증해 업로드했으며 이 작업에서 로컬 복원 시험은 하지 않았다. 기존 리뷰·렉처 카탈로그 74건을 동기화했고 별도 DQE 알림 기사나 이벤트를 새로 등록하지 않았다.

독립 담당자가 실제 깨끗한 공개 주소를 GET으로 읽고, 압축 해제한 한영 전체 HTML과 PDF가 검수본 해시에 맞는지 확인했다. 공개 코드 폴더 세 곳과 Python·설치 파일 여섯 개도 HTTP 200 및 원본 바이트를 대조했다. 기존 DQE 두 호와 같은 날짜 DQB·DRB의 PDF까지 보존했다. [검증 요약](artifacts/publication-qa.json)에 수치·실행 범위·공개 해시를 기록했다. 개인 메일의 상태나 정기 예약은 변경하지 않았다.
