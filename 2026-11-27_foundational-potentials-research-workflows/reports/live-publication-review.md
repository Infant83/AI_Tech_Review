# 실제 공개·복구·독자 등록 검증

2026-11-28 KST · 편집부(AEDAUT) 게시 감수, 운영팀(ADOPT) 배포·복구 확인 · figure_source_audit

「원자의 에너지 함수를 함께 쓰는 시대」의 한영 리뷰를 실제 HTTPS에서 확인했다. 게시 소스는 `c7cb3a0e3cae37839f2ef4192b60281132901a45`, 최초 게재일은 2026-11-28 KST다. 원고·근거·PDF 판본일 2026-11-27과 구별한다. 공개 주소·후보·실제 배포에 결속한 기계 판독 결과는 같은 폴더의 `live-publication-review.json`에 기록했다.

- [한국어 리뷰](https://infant83.io/AI_Tech_Review/reviews/2026-11-27_foundational-potentials-research-workflows/)
- [English review](https://infant83.io/AI_Tech_Review/reviews/2026-11-27_foundational-potentials-research-workflows/en/)
- [공개 배포와 후속 검증 작업](https://github.com/Infant83/AI_Tech_Review/actions/runs/46028207334)

## 실제 배포와 공개 파일

위 Actions 실행의 build·deploy·recovery-copy·notify-readers 네 job이 모두 성공했다. 실제 실행의 소형 `publication-validation` 아티팩트를 내려받아 `release-check.json`의 `ok: true`, 차단 목록 0개와 `payload-check.json`의 `ok: true`, 실패 목록 0개를 확인했다. 원시 비교에 남은 한 항목은 쓰지 않는 파생 목록 썸네일 캐시의 제거이며, 출판 release guard가 명시적으로 허용하는 경로다. 원 표지·본문·PDF 손실이 아니다.

실제 HTTPS 31경로는 모두 200과 예상 콘텐츠 형식으로 응답했다. 구성은 기사 24파일, 아카이브 PDF 2파일, 공개 메타데이터 5경로다. 기사 중 HTML을 제외한 22파일과 아카이브 PDF 2개가 검토한 후보와 바이트 단위로 같았다. 한영 HTML도 후보와 그대로 일치했으며, 이번 응답에서 별도의 Cloudflare 내용 변환은 관찰되지 않았다. 차이를 없애기 위한 임의의 HTML 제거·정규화는 하지 않았다.

기사·아카이브 26파일은 실제 `publication-release.json`의 snapshot 파일 SHA와도 같다. release 자체를 제외하고 검사한 30경로의 SHA는 전체 sealed artifact 목록과 일치한다. 원논문 결과 PNG 두 개의 국·영문 사본 네 개는 확보한 원본과 같은 SHA다. 공개 웹의 최초 게재 head는 2026-11-28, 본문 issue 정보와 작성·검증 정보의 원고·근거 기준일은 2026-11-27이다. 그림 1–5, 참고문헌 11개와 원그림 두 캡션의 CC BY 4.0 링크도 실제 공개 HTML에 있다.

### 공개 PDF 네 주소

| 언어·경로 | 쪽수 | 바이트 | SHA-256 |
|---|---:|---:|---|
| 국문 기사·아카이브 | 10 | 5,438,210 | `35245bad09bab9cdaa33ce3112ce83cd0c39077a5518f36e41f1ba530995d6bc` |
| 영문 기사·아카이브 | 11 | 5,358,976 | `7634d1ccf9f7e9a2983ae18a3588adac1c4a29955a7a012010ccdfb9d1708b67` |

각 언어의 기사 PDF와 아카이브 PDF가 승인한 최종 원본과 같다.

- [국문 기사 PDF](https://infant83.io/AI_Tech_Review/reviews/2026-11-27_foundational-potentials-research-workflows/review_ko.pdf)
- [영문 기사 PDF](https://infant83.io/AI_Tech_Review/reviews/2026-11-27_foundational-potentials-research-workflows/en/review_en.pdf)
- [국문 아카이브 PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-28-foundational-potentials-research-workflows-ko.pdf)
- [영문 아카이브 PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-28-foundational-potentials-research-workflows-en.pdf)

## 공개 release와 목록의 일치

실제 release와 `reader-publications.json`의 revision은 모두 게시 소스 `c7cb3a0e3cae37839f2ef4192b60281132901a45`다. 공개 카탈로그 SHA는 `a979f0d33a0d7776f47cbf285a02285ce62428c9fc8be59771cc6fac8926e689`로 release의 값과 같다. release를 다시 요청한 원 바이트도 같았으며 SHA는 `ddbbd4211ad4ba0af23cc59b58689d8fd2b71c355f9e22510818c6dd62a09c9f`다.

로컬 검토 후보 카탈로그의 revision `a64133e617207d595095ec97c6b208d6489e218c`와 실제 카탈로그의 차이는 revision 필드뿐이다. articles 배열과 나머지 값은 그대로다. 직전 실제 release의 기존 식별자와 기록은 모두 보존됐다.

| 구분 | 이전 실제 공개 | 이번 공개 |
|---|---:|---:|
| 리뷰 | 60 | 61 |
| 아카이브 문서 | 194 | 196 |
| canonical 출판 항목 | 93 | 94 |

증가분은 이번 리뷰 한 건, 한영 아카이브 문서 두 건, canonical 출판 항목 한 건이다. 허브 새 카드의 게재일도 2026-11-28로 확인했다.

## 복구 사본과 독자 등록

실제 recovery-copy job은 배포한 Pages 아티팩트를 가져와 release·카탈로그·파일 인벤토리를 대조하고 복구 아카이브를 생성·검증했다. 로그의 결과는 `ok: true`, 게시 소스와 같은 revision, **2,881파일·930,415,447바이트**다. 복구 tar.gz 자체의 SHA는 `8b92375b53feacdb7d9b243c4c6a193daaaa8c93f76ea77f61ff852dc5912637`다.

보존 아티팩트 `publication-recovery`의 ID는 **15213511954**, 크기는 837,151,124바이트, 업로드 아티팩트 digest는 `sha256:0e1105df389a3fed69204d5a8a4bf3abe84b5f50829670ec2b6e26c11fbb1501`, 만료 시각은 **2026-12-27T15:55:04Z**다. 내부 tar.gz의 해시와 업로드 포장 digest를 구별했다. 여기서는 실제 job의 검증 결과·아티팩트 메타데이터·digest를 대조했으며, 큰 복구 파일을 추가 다운로드하거나 로컬 복원을 수행하지 않았다.

notify-readers job의 실제 동기화 결과는 `synced: 94`, `newArticles: 1`, `queuedEvents: 1`, `baseline: false`, `ok: true`이고 revision도 이번 게시 소스와 같다. 이는 공개 검증 후 카탈로그 등록과 알림 이벤트 대기열 등록이 성공했다는 뜻이다. 개별 독자에게 알림이 전달됐음을 확인한 것으로 표시하지 않는다.

## 통합 담당자의 실제 Chrome 확인

통합 담당자(root)는 실제 공개 한영 페이지를 Chrome 1440px·390px에서 확인했다. 언어별 참고문헌 11개와 인용 대상, 이미지 여섯 개, 자체 피규어의 모바일 SVG 선택이 정상이며 문서 전체의 가로 넘침은 없었다. 모바일 원그림 두 개는 각각 342px 영역 안의 860px 그림을 스크롤하고 키보드로 초점을 받을 수 있다. 국문 데스크톱, 영문 모바일, 국문 허브 새 카드의 실제 렌더링도 시각 확인했다. 이 감수자는 통합 담당자의 구조화한 검사 기록을 읽었으며 브라우저 조작을 직접 수행한 것으로 표시하지 않는다.

초기 영문 모바일에서 Like 일시 불가 표시가 관찰됐다. 그 첫 상태의 HTTP 코드나 원인을 확인한 증거는 수집하지 않았다. 후속 새 세션에서 config 요청 200, 미로그인 subscription 요청 401, 새 기사의 like 조회 200과 `{ok: true, count: 0, liked: false}`가 확인됐고 화면은 `Like 0`으로 정상 표시됐다. 좋아요를 누르거나 값을 변경하지 않았다. 최초 표시를 특정 등록 경쟁 상태나 다른 원인으로 단정하지 않는다.

## 남은 범위와 모델 기록

실제 CI payload 검사는 통과했으며 기존 운영 경고 두 개는 남아 있다. 지연 검색 메타데이터는 gzip 99,058바이트로 80KB 성장 경고를 넘고, 공개 아티팩트는 seal 전 928,938,166바이트로 800MB 내부 경고를 넘는다. 이는 기존 미디어·용량 운영 과제에서 추적할 항목이며 이번 기사 공개 실패로 표시하지 않는다.

원 연구의 MLIP·DFT·MD·에이전트 시뮬레이션을 새로 실행하지 않았다. 과학 대조와 최종 PDF 시각 검수의 수행 범위는 기존 원고·제작 기록에 이어진다. 이번 확인은 실제 공개 바이트·목록·배포·CI 복구 검증·독자 등록과 통합 담당자의 화면 검수다.

이번 실제 공개 감수의 모델·추론 강도는 `artifacts/ai-model-provenance-live-audit-final-20261128.json`에 `gpt-6.1-sol`, `ultra`, `turn_context`로 남겼다. 게재 작업 시간창을 지정한 최종 수집의 공개 값은 시작 시 수집과 같다. 기존 파일을 덮어쓰지 않았으며 원 대화·식별자·설정 원문 증거는 저장소 밖에 보존했다. 이 확인 때문에 이미 승인한 기사·PDF를 다시 생성하지 않았다.
