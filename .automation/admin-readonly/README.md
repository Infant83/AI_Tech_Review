# 로컬 읽기 전용 관리 목록

공개 자료의 등록 원본과 이미 검증한 로컬 배포 묶음을 읽는 격리된 후보다. 자료를 수정하거나 게시하지 않는다. 운영 API·인증·원격 미리보기는 포함하지 않는다.

```sh
python3 scripts/preview_admin_inventory.py --baseline-snapshot output/verified-baseline/snapshot.json --output output/admin-preview-unique
```

`release.json`, `reader-publications.json`, `reader-updates.json`, `snapshot.json`은 기존 `publication_release.py baseline`으로 검증한 동일 묶음을 사용한다. 명령이 네트워크에서 기준본을 얻지는 않는다. 공개 근거 없이 입력만 보려면 `--baseline-snapshot` 대신 `--without-baseline`을 명시한다. 이 경우 공개 소속은 `unknown`이며 미게시라는 뜻이 아니다.

산출물은 해당 작업 사본의 `output/` 아래 새 폴더에만 만든다. 기존 폴더·심볼릭 링크는 거절하고 `.keep`를 먼저 둔다. 로컬 열람이 필요하면 생성된 폴더에서 loopback에만 서버를 연다.

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory output/admin-preview-unique
```

브라우저에서 `http://127.0.0.1:8765/`를 연다. 확인 후 서버를 종료한다. 내부 QA 화면과 산출물을 Git이나 공개 배포에 넣지 않는다. 관리용 코드도 독자 초기 자산이나 사이트 빌드에 연결하지 않는다.

등록 행, 알림 카탈로그, 공개 소속, 내용 비교와 검토 입력은 각각 다른 근거다. `unknown`은 비교 근거 부족을 뜻하고, 봉인 metadata는 개별 URL의 새 HTTPS 확인이 아니다. PDF 판본·코스 최신 별칭은 명시된 관계만 사용한다. 현재 목록 토큰은 읽은 입력을 식별하며 쓰기 권한·분산 잠금·편집 승인이나 배포 성공을 뜻하지 않는다.

원장 누락/중복·잘못된 경로/링크·한도 초과·읽는 중 변경은 reason code로 실패한다. 입력별5MB·총 JSON16MB, 응답2MB·2,000행을 넘으면 조용히 자르지 않는다. 화면은 검색200문자·50/100행 로컬 페이지 나눔을 사용한다.

범위와 후속 검토는 기존 [관리 일감](../../operations/issues/OPS-4b849a94-be8d-4cf0-a73e-d12a21104824.json)과 [v1 계약](../../operations/decisions/DEC-85dc450e-2d67-4b89-9ef8-584db1c75ca4.md)을 따른다. 이 후보는 별도 일반 게시 승인자가 아니다.

## 로컬 메타데이터 요청 사전검사 · A 후보

[관리 쓰기 계약](../../operations/decisions/DEC-5e30f3a0-1003-4432-bda1-688bdb73ceb1.md)의 A만 구현한 별도 로컬 도구다. 기존 공개 리뷰 하나의 `subtitle`·`category`·`tags`·`summary` 변경 요청을 검사하며 **등록·원고·출판 요청·Git·DB를 저장하거나 후보 생성·발행·알림을 실행하지 않는다.** 인증·지속 멱등성·실제 ref CAS·HTTP API도 없다. 읽기 화면에 수정 버튼이나 원격 API를 추가하지 않는다.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/admin_requests.py --root . --request output/requests/request.json --baseline-snapshot output/verified-baseline/snapshot.json
```

세 경로는 운영자가 각각 지정한다. baseline은 기존 검증 경로로 취득한 같은 `release.json`·`reader-publications.json`·`reader-updates.json`·`snapshot.json` 묶음이어야 한다. 도구가 네트워크에서 취득하거나 최신 운영 상태를 증명하지 않는다. 요청 JSON에는 파일 경로·URL·actor/role을 넣지 않는다. 결과만 stdout JSON에 출력하며 문구·내부 경로·원시 예외·멱등 키는 출력하지 않는다. 출력 리다이렉션과 요청 파일 보관은 운영자가 보호된 `output/` 폴더에서 별도로 관리한다.

요청은 다음 필드를 정확히 포함한다. 같은 이름의 JSON 중복 키·비정상 상수·잘못된 UTF-8·알 수 없는 필드도 거절한다.

| 필드 | 값 |
| --- | --- |
| `schemaVersion`, `operation` | 정수 `1`, 문자열 `review_hub_metadata_update` |
| `sourceId` | `review:` 접두어 없는 기존 native 리뷰 folder ID |
| `expectedSourceRevision` | 확인한 로컬 source commit의 소문자40자리 SHA |
| `expectedInputs` | `review_inputs`가 반환한 `source_sha256`·`registration_sha256`·`article_registration_sha256` 세 값 |
| `expectedReleaseRevision` | 지정한 완전한 공개 묶음의 source revision |
| `expectedReleaseEvidence` | `releaseSha256`·`catalogSha256`·`updatesSha256`: 각 파일 원시 bytes의 소문자 SHA-256 |
| `patch` | 허용 네 필드 중1개 이상. null/삭제·다른 필드·중첩 경로는 지원하지 않음 |
| `idempotencyKey` | 정규 표기의 비어 있지 않은 UUID. 형식 검사만 하며 저장·중복 실행 방지 기능은 없음 |

요청은32,000B 이하, subtitle1,000/category200/summary8,000문자 이하, tags40개·각200문자 이하다. 기존 등록의 single-line·필수값 검사도 동일한 순수 native validator로 병합 객체 전체에 적용한다. 문구나 Unicode를 정규화·절단하지 않는다. fingerprint는 operation/schema·대상·세 기준·patch의 정렬된 UTF-8 JSON에서 계산하며 멱등 키와 확인 시각은 제외한다. 서로 다른 문구나 기준은 다른 fingerprint가 된다.

첫 후보는 현재 v2 지속 요청에 본문 원본·보호 등록이 결속되고, 실제 baseline에 해당 리뷰가 있으며 **주 웹판과 등록된 번역 웹판 모두의 declared after hash가 baseline의 content hash와 같은 경우**만 받는다. 나머지 reference에도 선언이 있으면 after가 같아야 한다. 바뀌지 않은 그림·첨부에 새 선언을 요구하지 않으며, 모든 첨부 bytes의 실제 연속성은 후속 C 후보 검사로 확인한다. v1·웹판 선언 누락/부분/불일치·미게시 대상은 `revalidation_required`다. 새 감수나 `--review`를 자동 수행하지 않으며, 이는 이 사전검사기의 제한이다. 일반 게시의 기존 권한·검증을 변경하지 않는다.

소비한 source가 실제 로컬 Git commit과 같은지도 확인한다. 검토 중인 dirty 입력·등록 집합 변경·symlink·입력 변경·잘못된 묶음은 거절한다. Git HEAD와 공개 revision이 다른 것 자체는 장애가 아니며, 요청에 제시한 각각의 근거와 비교한다. 같은 공개 revision의 다른 재빌드도 원시 묶음 hash가 다르면 `release_changed`다.

성공은 `validated_preflight_only`, 현재 값과 같은 patch는 `no_change`다. 둘 다 저장/게시 완료가 아니다. 실패는 종료코드1과 `reason`만 반환한다. `source_conflict`·`input_conflict`·`release_changed`는 새 근거 확인이 필요하며, 초기화 누락·스키마 변경·검토 근거 부족은 안전하게 거절한다. 로컬 전후 확인은 원자적 snapshot이나 분산 잠금이 아니며, 작업 ledger·저장·인가·후보·발행 연결과11/21 독립 검토/통합은 후속 단계다.
