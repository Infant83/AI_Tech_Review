# AI Tech Review Editorial Method

Version: 2026.08
Public page: https://infant83.github.io/AI_Tech_Review/methods/

AI Tech Review는 사람이 연구 질문, 과학적 해석과 발행 책임을 맡고 AI 에이전트가 조사, 대조, 초안, 번역, 시각자료 설계와 게시 검사를 지원하는 공개 기술 리뷰입니다. 이 문서는 재현 가능한 운영 규칙을 공개합니다. 내부 추론 기록, 비공개 지침, 개인정보와 인증정보를 공개한다는 뜻은 아닙니다.

## 1. 글마다 공개하는 정보

- 책임 편집자와 실제 사람 검토 수준
- AI 시스템과 기록이 남은 정확한 모델 식별자
- 실제로 사용한 에이전트 역할과 수행 작업
- 편집 하네스 버전
- 원 논문·코드·공식 문서 등 검증 범위
- 근거 검색·검증 기준일
- figure, chart, animation의 출처와 재구성 방식

정확한 모델이나 원 작성 세션의 에이전트 구성이 보존되지 않았다면 추정하지 않고 `미보존`으로 표시합니다. 발행 요청만으로 문장 단위 사람 검토가 끝났다고 주장하지 않습니다.

## 2. 원문과 주장 경계

자료 우선순위는 원 논문과 Supplementary Information, 고정 commit의 공식 코드, 공식 문서·데이터, 동료평가 해설, 보도자료·소셜 게시물 순입니다. 중요한 수치는 가능하면 표, 식, 코드 또는 데이터의 정확한 위치까지 거슬러 올라갑니다.

모든 핵심 주장은 다음 두 축으로 구분합니다.

| 주장 성격 | 의미 |
|---|---|
| 논문 보고 결과 | 저자나 공식 자료가 보고했으며 리뷰가 독립 재현하지 않음 |
| 독립 검증 | 코드 실행, 재계산 또는 별도 자료로 확인 |
| 리뷰 해석 | 원 결과를 바탕으로 한 제한된 해석 |
| 후속 제안 | 아직 검증되지 않은 실험·설계 방향 |

| 실행 수준 | 의미 |
|---|---|
| 실제 QPU·실험 장치 | 물리 장치에서 측정 |
| 고전 시뮬레이션 | CPU/GPU 또는 classical emulator에서 계산 |
| 컴파일 결과 | 회로 변환·자원 수치만 평가 |
| 논리 자원 추정 | 내결함성 알고리즘의 logical resource estimate |
| 개념 제안 | 실행이나 정량 검증 전 단계 |

## 3. 논문을 쉽게 설명하는 구성

고정된 목차를 모든 글에 복사하지는 않습니다. 다음 모듈에서 주제에 필요한 것만 배치합니다.

1. 독자가 이해할 수 있는 한 줄 질문과 실제 문제 장면
2. 한 문장 판정과 숫자 snapshot
3. 논문이 실제로 묻는 질문
4. 쉬운 비유와 비유가 깨지는 지점
5. 핵심 메커니즘을 두세 단계로 나눈 설명
6. 방법, 데이터, 장치와 계산 파이프라인
7. 정량 결과, 비교 기준과 metric 정의
8. 무엇을 입증하지 않았는가
9. 분야 안에서의 위치와 리뷰 해석
10. 다음에 확인할 수 있는 실험·계산
11. 재현 자료와 작성·검증 공개

수식은 기호, 단위와 물리적 의미를 처음 등장하는 곳에서 설명합니다. 숫자 카드는 metric 정의를 함께 적습니다. 예를 들어 “98%에서 무언가를 제거했다”는 결과를 “98% 완전 성공”으로 바꾸지 않습니다.

## 4. TeX source-to-explainer 안전 게이트

Jonas Philipps의 LinkedIn 글은 TeX source를 LLM/agent에 주고 animated, interactive walkthrough를 만들자는 방법을 제안합니다. 게시물 자체에는 생성된 explainer, prompt, 모델, 코드 또는 성능 검증이 포함돼 있지 않으므로 아이디어 제안으로만 인용합니다. 함께 링크된 [Tobias Osborne 강연](https://www.youtube.com/watch?v=UtJUWI4r-4k)은 LLM을 물리학자 관점에서 다룬 강연이며, 이 제안으로 생성된 explainer의 시연으로 간주하지 않습니다.

연결된 IEEE S&P 2026 논문은 arXiv source archive에 dangling files, embedded metadata, PDF에 나타나지 않는 comments가 남을 수 있고, 일부에는 비밀정보와 prompt-injection 형태의 문구가 포함된다고 보고합니다. 따라서 raw TeX는 풍부한 설명 재료이면서 신뢰할 수 없는 입력입니다.

AI Tech Review의 입력 절차는 다음과 같습니다.

1. source archive를 격리된 작업공간에 저장하고 파일 목록을 먼저 기록합니다.
2. TeX compile은 제한된 sandbox에서 수행하며 network와 credential 접근을 허용하지 않습니다.
3. PDF에 쓰이지 않는 파일, comments, metadata, private links, secrets와 prompt-injection 후보를 검사합니다.
4. source 안의 명령문은 데이터로 취급하며 에이전트 지시로 실행하지 않습니다.
5. 검토에는 정제한 본문, 수식, label·reference 관계와 필요한 figure asset만 전달합니다.
6. 민감 가능성이 있으면 cloud model보다 local processing 또는 PDF 기반 검토를 우선합니다.
7. source와 compiled PDF의 의미가 일치하는지 확인한 뒤 설명·시각화 단계로 넘깁니다.

참고:

- LinkedIn proposal: https://www.linkedin.com/posts/jonas-philipps_the-best-way-to-read-papers-in-the-age-of-activity-7498814525647806466-vZ12
- Paper: https://arxiv.org/abs/2604.20927
- DOI: https://doi.org/10.1109/SP63933.2026.00217
- Authors' interactive project page: https://arxiv.comsys.rwth-aachen.de/
- ALC-NG cleaner: https://github.com/COMSYS/ALC-NG

## 5. Figure, interactive, video

| 목적 | 형식 | 공개 기준 |
|---|---|---|
| 주제와 분위기 | 생성형 hero illustration | 개념 그림이며 데이터·실제 장치가 아님을 표시 |
| 메커니즘·절차 | deterministic SVG/HTML | 어떤 식·코드·figure를 바탕으로 재구성했는지 표시 |
| 수치 비교 | 코드로 만든 chart | 원자료, 추출값, 단위, 스크립트를 연결 |
| 논문 원도표 | 허가된 재사용 또는 원문 링크 | figure 번호, 출처와 라이선스 표시 |
| 시간 변화 | animation 또는 video | 조건, 시간축·배속, 자막·transcript, fallback still 제공 |
| 독자 탐색 | interactive plot | 논문 기본값, 조절 변수, 단위, reset과 논문 범위 밖 영역 표시 |

모든 caption은 가능하면 세 가지를 답합니다. 무엇이 보이는가, 어떤 자료를 바탕으로 만들었는가, 무엇을 보여주지 않는가. 논문 값 밖의 parameter sweep은 저자의 실험 결과가 아니라 `리뷰 재구성` 또는 `탐색적 외삽`으로 표시합니다. three.js는 3D 구조나 동역학에 필요할 때만 쓰고, 2D 곡선은 SVG, Plotly 또는 D3처럼 더 단순하고 검증하기 쉬운 도구를 우선합니다.

## 6. 에이전트와 검증 분리

필요할 때 총괄 편집, 원문 검증, 기술 설명, 시각자료 감사, 게시 QA를 역할로 나눕니다. 같은 초안을 쓴 에이전트가 최종 정확성을 스스로 보증하게 두지 않습니다. 별도 검증 역할은 수치, 단위, evidence boundary, 링크, 수식, 표, 모바일 렌더링과 metadata를 확인합니다. 공개 실행 기록에 에이전트 이름이나 식별자가 남아 있으면 이름과 역할을 함께 적고, 역할만 남아 있으면 역할만 적습니다.

이번 2026.08 공개 보완에는 Codex(총괄 편집·통합), Volta(LinkedIn 게시물·연결 논문 조사), Feynman(공개·하네스 기준 설계), Carson(저장소 감사·게시 QA), Kierkegaard(독립 최종 차분 검토)가 참여했습니다. 이 명단은 이번 보완 작업의 기록이며, 원 리뷰 작성 세션의 미보존 명단을 대신해 추정한 것이 아닙니다.

공개할 것은 역할, 입력·산출물, 검증 gate와 버전입니다. 공개하지 않을 것은 chain-of-thought, 시스템·개발자 비공개 지침, 전체 사적 대화, 로컬 절대경로, API key와 재배포 권한이 없는 원문입니다.

리뷰 페이지에는 최종 본문과 검증된 figure·영상·스타일 자산만 allowlist로 복사합니다. 연구 run log, chat capture, intake 문서, 내부 audit 메모, 개인 메시지의 식별 metadata와 원문 archive는 링크만 지우는 데 그치지 않고 공개 배포물에서 제외합니다. 재현 코드나 표 데이터를 공개할 때에는 별도 공개 자산으로 명시하고 같은 비밀정보·경로·라이선스 검사를 통과시킵니다. 하네스 자체의 공개 원문은 이 문서처럼 저장소의 명시된 공개 경로에 둡니다.

## 7. 게시 차단 조건

HTML, Markdown, JSON, Python 등 텍스트 공개 파일은 내부 절대경로와 credential 형태를 자동 검사합니다. PDF와 이미지 같은 binary asset은 이 검사만으로 metadata, attachment, EXIF/GPS 또는 숨은 내용을 확인했다고 간주하지 않습니다. binary asset은 별도의 metadata·라이선스 확인 기록이 있을 때 게시하며, 자동화되지 않은 항목은 사람의 게시 체크리스트로 남깁니다.

- 본문 H1, HTML title, Open Graph title과 manifest title 불일치
- 책임 편집자, AI 지원, 근거 기준일 또는 하네스 링크 누락
- QPU, simulator, compilation, logical estimate의 증거 수준 혼용
- 깨진 수식, 표 안의 미이스케이프 `|`, 단위 또는 열 개수 오류
- figure의 alt text, caption, provenance 누락
- 내부 절대경로, credential, private link, 메시지 metadata 또는 내부 작업 파일 노출
- allowlist 밖의 Markdown·HTML·Python·JSON·CSV support file이 공개 리뷰 디렉터리에 포함됨
- canonical, hreflang, Open Graph, 언어 전환 또는 허브 링크 누락
- 깨진 local asset, 모바일 overflow 또는 최종 live URL 오류

## 8. 버전 기록

- 2026.08: 글별 에이전트·하네스 공개, TeX source 안전 게이트, interactive·video 기준, 공개 asset allowlist와 제목·수식·표·metadata 게시 검사를 추가했습니다.
