# 양자 알고리즘 리뷰의 실제 게시 검증

2026-11-27 · 편집부(AEDAUT) 게시 판본 대조 및 운영팀(ADOPT) 읽기 전용 배포 검증 · foundation_calculations

## 배포한 판본

[Actions run 45944956993](https://github.com/Infant83/AI_Tech_Review/actions/runs/45944956993)의 소스 커밋은 `4c86b1447b6cf7e5b156f7216ed022cf44023195`다. GitHub의 현재 연결 상태를 확인하고 해당 run과 실제 HTTPS 자료를 읽었다. 빌드가 끝난 뒤 deploy 성공을 확인한 다음 공개 응답을 대조했다.

| Job | 결과 |
|---|---|
| build | success |
| deploy | success |
| recovery-copy | success |
| notify-readers | success |

[국문 기사](https://infant83.io/AI_Tech_Review/reviews/2026-11-24_quantum-algorithms-principles-applications/)와 [영문 기사](https://infant83.io/AI_Tech_Review/reviews/2026-11-24_quantum-algorithms-principles-applications/en/)의 실제 디렉터리 URL, 두 `index.html` 주소 모두 HTTP 200·`text/html`로 응답했다. 이 HTTP 클라이언트의 응답은 검증 후보와 바이트가 같고, 실제 sealed release에 기록된 HTML 해시와도 같다. 이번 응답에서는 Cloudflare의 분석 코드·메일 링크 변환을 별도로 관찰하지 않았다. HTML을 비교하기 위해 스크립트나 링크를 일반적으로 제거하는 정규화는 적용하지 않았다.

## PDF와 기사 자산

아래 네 주소가 HTTP 200·`application/pdf`로 응답했으며, 같은 언어의 승인 PDF와 SHA-256이 정확히 같다.

| 판본 | 공개 PDF |
|---|---|
| 국문 기사 첨부 | [review_ko.pdf](https://infant83.io/AI_Tech_Review/reviews/2026-11-24_quantum-algorithms-principles-applications/review_ko.pdf) |
| 영문 기사 첨부 | [review_en.pdf](https://infant83.io/AI_Tech_Review/reviews/2026-11-24_quantum-algorithms-principles-applications/en/review_en.pdf) |
| 국문 아카이브 | [archive PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-27-quantum-algorithms-principles-applications-ko.pdf) |
| 영문 아카이브 | [archive PDF](https://infant83.io/AI_Tech_Review/archive/files/2026-11-27-quantum-algorithms-principles-applications-en.pdf) |

- 국문: 4,259,558 bytes, SHA-256 `8d3c3b5f0e2860c577043fd6cab856174f7edbf04b66d33263acfe512dcb446b`.
- 영문: 4,193,444 bytes, SHA-256 `162dba7c7dfc139bef62cea28a829f46fd4cc73b14b89982bb9e662f3bf36bc0`.

기사의 비-HTML 자산 18개(SVG 12·CSS 2·PNG 2·PDF 2)는 원래 `dist/`, 검증 후보, sealed release, 실제 HTTPS 응답 사이에서 크기·SHA-256이 일치한다. 기사·아카이브·목록·release를 포함한 29개 공개 경로에서 HTTP 200과 파일 종류에 맞는 content-type을 확인했다.

## 목록과 연속성

실제 `publication-release.json`과 `reader-publications.json`의 소스 revision은 위 커밋과 같으며, release가 지정한 catalog SHA-256과 실제 catalog bytes가 일치한다. 비교를 마친 뒤 release를 다시 읽어 같은 bytes임을 확인했다. 로컬 후보의 독자 catalog와 실제 catalog는 같은 기사 배열을 담고 있으며 소스 revision만 배포 커밋으로 바뀌었다.

실제 목록은 리뷰 60개·아카이브 문서 193개·독자 publication 93개다. 새 기사의 최초 게재일과 두 아카이브의 날짜는 2026-11-27, 근거 기준일은 2026-11-24다. 독자 갱신 목록에서 새 기사와 한영 기사·첨부·아카이브 경로가 같은 publication에 연결된다.

작은 `publication-validation` artifact를 내려받아 CI의 후보 보고서·연속성 검사·payload 검사를 대조했다. release 검사 `ok=true`, blockers 0개이며 추가된 것은 새 리뷰·한영 아카이브·해당 publication이다. 실제 sealed snapshot의 missing files와 declared hash mismatches는 모두 0개다.

## 복구 사본과 독자 등록

`recovery-copy` job은 배포한 아티팩트의 2,847개 파일·압축 전 896,165,567 bytes를 검증하고 복구 archive SHA-256 `7a0e7c9fa71d1e8c60980ac60f35784bda4c5d9e51b4d881301a9e825ecbf2bb`를 보고했다. 업로드한 `publication-recovery` artifact ID는 **15174567409**, GitHub artifact digest는 `sha256:74fdcf56e654988bba2be737cf5d9d190af7b28e2e73bb2f263a6911faad9d29`다. 이 digest는 GitHub 업로드 artifact의 값이며 내부 복구 archive 해시와 구별한다. 만료 예정은 2026-12-27이며, 보존 처리에서 현재 artifact 확인이 통과했다.

이번 확인에서는 큰 복구 파일을 로컬로 내려받아 풀지 않았다. job의 실제 검증 결과·소스 revision·artifact ID·digest를 대조한 범위다.

`notify-readers`의 실제 HTTPS 확인·동기화 단계는 `ok=true`, synced 93, newArticles 1, queuedEvents 1, baseline false를 보고했다. 이는 publication 등록과 알림 이벤트 대기열 기록의 성공이다. 개별 독자 단말의 수신 여부를 확인한 결과로 확대하지 않는다.

전체 경로·상태·타입·크기·해시와 job/아티팩트 정보는 [기계 판독 기록](live-publication-review.json)에 있다. 통합 담당자(root)는 별도로 실제 Chrome에서 한영 1440·390px 화면을 읽었다. HTTP 200, 이미지 4개, 참고문헌 대상 27개, 모바일 그림 선택, 가로 넘침 없음을 확인하고 화면을 시각 검수했다. 이 브라우저 확인의 수행 주체와 본 기록의 HTTP·job 대조 주체를 구별한다. 이 검증에서 원고·등록정보·사이트를 수정하거나 Git push·배포·추가 메시지 발송을 실행하지 않았다.
