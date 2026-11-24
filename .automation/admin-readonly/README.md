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

성공은 `validated_preflight_only`, 현재 값과 같은 patch는 `no_change`다. 둘 다 저장/게시 완료가 아니다. 실패는 종료코드1과 `reason`만 반환한다. `source_conflict`·`input_conflict`·`release_changed`는 새 근거 확인이 필요하며, 초기화 누락·스키마 변경·검토 근거 부족은 안전하게 거절한다. A는11/21 정식 독립 감수와 소스 통합을 마쳤다. 로컬 전후 확인은 원자적 snapshot이나 분산 잠금이 아니며, 아래 B1은 별도의 합성 후보 저장 실험이다. 실제 원본의 저장·인가·공개 아티팩트·발행 연결은 후속이다.

## B1 · 합성 standalone Git 후보의 첫 로컬 저장기

`scripts/admin_request_jobs.py`는 **명시적으로 새로 만든 작은 합성 fixture만** 다룬다. `init-fixture`는 기존 저장소를 등록하거나 clone하지 않는다. 고정 합성 리뷰·한영 원고·검토 입력·로컬 baseline을 새 standalone Git repo에 만들고, sandbox/Git 내부 identity와 보호 표식을 결속한다. `apply`는 없는 store를 초기화하지 않는다. 이 도구로 실제 리뷰를 편집하거나 원본/원격 main을 갱신하지 않는다. 서버·계정 인가·DB·C의 빌드·공개 알림도 없다.

```sh
mkdir -p output/admin-b1-local
touch output/admin-b1-local/.keep
PYTHONDONTWRITEBYTECODE=1 python3 scripts/admin_request_jobs.py init-fixture --sandbox output/admin-b1-local/fixture
PYTHONDONTWRITEBYTECODE=1 python3 scripts/admin_request_jobs.py apply --sandbox output/admin-b1-local/fixture --request output/admin-b1-local/fixture/example-request.json --baseline-snapshot output/admin-b1-local/fixture/baseline/snapshot.json
```

첫 명령의 목적지는 새 폴더여야 한다. 요청을 바꿔 볼 때에는 이 fixture의 `example-request.json`에서 허용 patch와 새로운 UUID를 준비한다. 기존 key의 patch·target·기준을 바꾸면 `idempotency_conflict`다. 고정 synthetic 대상 외의 새 작업은 지원하지 않는다. stdout은 값/내부 경로/원시 오류/멱등 키를 제외한 상태·operation ID·fingerprint·candidate SHA 또는 reason JSON이다.

store의 불변 key inventory가 claim hash를 예약하고, 불변 claim은 원고 값을 복사하지 않고 operation/fingerprint·대상·기준/결과 SHA를 보존한다. 새 요청은 frozen 요청과 A 결과의 fingerprint/세 기준, 고정 Git registration blob SHA를 다시 결속한다. 실제 후보는 원본 Git tree의 등록 한 파일만 바꾼 commit이다. receipt ref 자체가 실제 commit 객체를 가리켜야 하며 tag의 자동 해석으로 대신하지 않는다. Git receipt metadata의 operation/phase/parent·before/after hash와 **정확한 예상 전체 tree OID**가 일치해야 재생한다. 예상 tree는 메모리에서 계산하므로 replay는 Git object/ref를 쓰지 않는다. journal 상태 파일은 파생 표시이며 없어지거나 손상되면 검증된 receipt로 다시 만든다.

실제 로컬 `update-ref` transaction에서 sandbox main의 expected SHA를 verify하고 receipt ref를 expected old SHA에서 새 결과로 바꾼다. Git transaction의 응답이 timeout/I/O로 끊기거나 실패 뒤 진단 조회도 불가능하면 `outcome_unknown`을 유지하고 같은 key의 receipt를 대조해 조정한다. 다른 글과 무관한 main 전진도 `source_conflict`다. 실제 원본/원격 main CAS의 구현이 아니다. 후보는 raw blob·tree·commit plumbing으로 만들고 workingtree·index·기존 main·한영 원고·baseline은 바꾸지 않는다. 같은 store의 협력 프로세스는 지우지 않는 lock inode로 직렬화하며 분산 잠금은 없다.

`candidate_saved_local`은 합성 Git 후보의 저장일 뿐 공개 아티팩트·게시 성공이 아니다. 같은 요청은 같은 결과를 replay하며, 그 사이 main이 전진했으면 `sourceAdvanced:true`로 구분한다. 기존 결과의 replay 때문에 A를 다시 실행하거나 새 commit을 만들지 않는다. `no_change`는 로컬 tombstone만 남기고 Git commit/ref·후보·빌드·배포·알림을 만들지 않는다.

중단 후 claimed Git receipt가 있으면 같은 요청과 근거를 재검증해 같은 operation을 재개할 수 있다. 결과 ref 성공 뒤 journal 실패는 `outcome_unknown`이며, 재조회는 실제 Git 결과를 대조해 같은 SHA로 조정한다. inventory 예약 직후/claim 직후 중단처럼 claim/receipt 근거가 부족하거나 key 기록이 없어진 경우에는 `outcome_unknown`/`store_inconsistent`로 중단한다. 자동 재초기화·새 key 배정·TTL 만료·claim/receipt 삭제는 하지 않는다. 이 보수적 중단은 자동 완전 복구 기능이 아니며, 수동 근거 조정/보존 사본의 복구 연결은 후속이다.

symlink·연결된 Git common-dir·remotes·외부 alternates·replace/graft·local hook/filter/include 설정·attributes를 거절한다. Git 자식 프로세스와 A 자식은 inherited `GIT_*`/global/system config 영향을 제거한 환경에서 실행하고 hook·signing·filter 경로를 차단한다. 로컬 principal은 고정 fixture 설정이며 실제 사람/에이전트의 서버 인가가 아니다. 사용자가 OS 권한으로 모든 identity/이력을 위조하거나 통째로 없앤 상황을 탐지·복구한다고 주장하지 않는다.

입력 요청32KB·control JSON64KiB, sandbox 파일3,000개/합계16MB·작업128개로 제한한다. 한도 초과는 거절하며 정리·삭제로 우회하지 않는다. 파일 예약/교체는 fsync와 부모 directory sync를 사용하지만 전원 차단·디스크 손상·원격 내구성 보증이 아니다. Git object/ref transaction과 파일 journal을 하나의 원자적 트랜잭션으로 표시하지 않는다.

B1은11/22 c3a4a5d의12그룹 정식 독립 감수와 소스통합을 마쳤다.11/24에는527b9d8에서 Git 실행 파일 선택도 좁게 보완했다. 당시 첫 후보/11월22일 검토 목표는 역사 이력이며 현재 단계는 로컬 합성 도구 완료다. 실제 원본 연결·운영용 key/store 보존/복원·분산 writer·인가/API·배포는 해당 계약의 후속 B/C/D/E로 남는다. 기존 일반 게시의 권한·승인 규칙은 바꾸지 않는다.

## B2a · 원본 읽기 전용 인수 명세

`admin_source_intake.py`는 기존 A와 같은 요청·완전 baseline을 확인하고 새 보호 폴더에 `descriptor.json`만 작성한다. 결과 `source_intake_plan_only`는 읽은 입력의 명세이며 후보 저장·접수한 key의 replay·인가·발행이나 복구 사본이 아니다. source는 operator가 지정한 standalone/linked worktree이며 source 코드·builder는 실행하지 않는다. 신뢰한 도구 위치와 source 경로는 별개다.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/admin_source_intake.py --root /controlled/source --request output/protected/request.json --baseline-snapshot output/verified-baseline/snapshot.json --output output/new-intake
```

출력의 부모 폴더는 이미 있어야 하고 목적지는 새 경로여야 한다. `.keep`를 먼저 만들고 배타적으로 완전 명세를 기록한다. 실패한 부분 출력은 보호된 채 남으며 새 목적지에서 다시 인수한다. source 내부 출력은 `output/` 아래만 허용하고 baseline/Git 경로 안에는 기록하지 않는다. stdout은 작은 상태/digest/reason이며 경로·본문·patch·멱등 키를 포함하지 않는다.

명세는 실제 source commit/tree, A의 동일 frozen readset/native3SHA, 정확 ledger membership·모델 AST·선택 dist의 경로/mode/Git blob OID/size/rawSHA, baseline 원시3SHA/snapshot SHA와 신뢰한 도구 code hash를 결속한다. JSON payload는 기존 한도 안에서만 보관하고 원고/첨부 bytes·문구는 복제하지 않는다. 결정적 `intakeDigest`와 확인 시각/관측 I/O 수치는 분리한다. 일부 경로의 새 Git HEAD를 원래 source 판본으로 쓰지 않는다.

whole-tree metadata20,000행/4MiB, dist1,000경로/고유 경로 합128MiB·한 파일64MiB, JSON5,000,000B/총16,000,000B·요청32,000B, 실제 반복 읽기512MiB·Git 명령20초/전체120초, descriptor2,000,000B/stdout16KiB로 제한한다. 초과는 자르지 않고 거절한다. source 설정/객체 경로와 선택 입력·HEAD가 바뀌거나 baseline이 없으면 거절하며, 무관한 미추적/진행 파일은 보존한다. source config의 위험한 include/filter/fsmonitor/alias·promisor/외부 alternates/replace/graft는 거절하고 Git 자식의 inherited 설정·credential/자동 취득·optional writes를 차단한다.

Git 실행 파일은 inherited PATH 대신 고정 설치 위치의 실행 가능한 정규 파일을 검증해 선택한다. Homebrew의 버전 경로는 Git Cellar 안으로만 해석하며, 지원 binary가 없으면 거절한다. B1 합성 도구도 같은 설치 경로 선택과 고정 child PATH를 사용하며 기존 CAS/receipt·합성 전용 범위는 유지한다. 선택 source의 `commondir`·`config.worktree`는 부재도 결속하므로 읽는 중 신설·소실을 거절한다. 실제 linked worktree 호환을 위한 `[codex] localEnvironmentConfigPath` 한 설정은 불활성 metadata로만 받으며 값이 가리키는 파일을 읽거나 실행하지 않는다. 원시 설정 bytes는 계속 변경 검사에 포함한다. dist 합계는 hash를 계산한 실제 bytes로 산정하고 첫 읽기부터 남은 고유 경로 예산을 적용한다.

출력은 source 읽기 전에 root부터 부모까지 no-follow directory FD로 고정한다. 새 디렉터리·보호 표시·부분 파일·hard link·unlink·fsync는 고정한 FD에 상대적인 연산으로 수행하고 부모/leaf의 경로와 열린 객체가 같은지 다시 확인한다. 부모와 첫 open 뒤 leaf의 관측 가능한 교체는 `output_changed`로 거절하며 다른 경로로 쓰기를 돌리지 않는다. 첫 leaf FD는 운영자 euid 소유·정확0700·빈 디렉터리인지 확인하며 모든 출력 파일은 배타 생성한다. 중단/실패의 보호 출력은 남기고 같은 목적지를 재초기화하지 않는다. 이 경로는 POSIX no-follow/dir-FD 지원이 필요하며 지원하지 않는 환경에서는 거절한다. 완전한 파일이 남아 있어도 CLI의 `ok:false`는 성공한 인수가 아니다.

이는 제어된 로컬 운영자와 부모 경로를 위한 도구다. POSIX mkdir는 열린 directory FD를 반환하지 않으므로 mkdir와 첫 open 사이의 임의 same-UID 프로세스가 소유·mode·empty 조건을 만족하는 일반 디렉터리로 교체한 것을 원자적으로 식별한다고 보장하지 않는다. leaf identity 결속은 첫 open부터이며 mkdir가 만든 바로 그 inode의 원자적 획득·출력 namespace 잠금·source 전체의 원자적 snapshot·후속 writer 인가를 뜻하지 않는다. 비신뢰 주체가 부모 경로를 변경할 수 있는 공유 서버의 출력 경로로 활성화하는 것은 후속 설계다.

B2a는11/24 527b9d8의 로컬5기준 정식 검증과 소스통합을 마쳤다. 최종 전체554검사(553통과·기존 선택1skip)와 범위별 독립 근거는 [실행 기록](../../operations/runs/20261123T113702Z-50a20771-a812-4af3-9049-572406a1f132.md)을 따른다. candidate Git/keyclaim·원본 writer·서버/API/DB·발행은 구현하지 않았다. 후속 [B2b1 계약](../../operations/decisions/DEC-5e30f3a0-1003-4432-bda1-688bdb73ceb1.md#b2b1--선택-입력의-독립-git-보존과-불변-판본-매핑)은 선택 원본 bytes의 독립 Git 보존/불변 판본 매핑만 채택했으며 구현 전이다. 모든 첨부/ID/URL/한영 실제 연속성은 C/E에서 별도로 검증한다.
