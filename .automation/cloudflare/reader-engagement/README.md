# Reader engagement 운영 안내

## 개인 학습 노트와 공유 계정 · 2026-11-05

`migrations/0004_study_notebooks.sql`과 `src/study.js`는 기존 기기별 좋아요·알림과 별도로 패스키 계정과 비공개 필기 저장소를 제공한다. 로그인은 `@simplewebauthn/server` 14.0.3으로 WebAuthn 등록·인증 응답을 검증한다. Face ID·Touch ID·보안 키 등 인증기의 사용자 확인이 필수이며, 사이트 RP ID는 `infant83.io`, 허용 브라우저 Origin은 `https://infant83.io`다. 개발 모드는 기존의 명시적 loopback Origin 설정만 따른다. 새 OAuth 앱이나 이메일·비밀번호·서버 비밀값은 요구하지 않는다.

등록·로그인 challenge는 API 호스트의 HttpOnly 쿠키에 연결하고 D1에서 5분 만료와 1회 사용을 강제한다. 등록 응답은 attestation `none`, resident credential과 사용자 확인을 요청한다. 로그인은 서명·challenge·RP·Origin·사용자 확인·credential counter를 검증한다. iframe 로그인은 지원하지 않는다. 인증 성공 시 256비트 난수 세션의 SHA-256 해시만 D1에 기록하며 원본은 `__Host-study_session` HttpOnly·Secure·SameSite=Strict 쿠키에 둔다. 세션은 30일 후 만료되며 로그아웃하면 서버 세션도 제거한다. 패스키 자체의 기기 간 전달·복구는 사용자의 플랫폼 패스키 관리자에 따른다. 이 서버가 패스키 개인키나 복구 비밀을 보관하지 않는다.

노트의 소유자는 계정이며 `0005_study_permissions.sql`부터 공유 권한을 구분한다. `viewer`는 필기를 읽고 자신의 읽던 위치·책갈피만 저장한다. `contributor`는 새 필기를 더하고 자신이 작성한 필기만 지울 수 있으며, 기존 필기·다른 작성자의 필기와 작성자가 미기록인 이전 필기를 지울 수 없다. `editor`와 `owner`는 기존 필기를 포함해 함께 추가·삭제할 수 있다. 소유자만 공유 권한을 발급·변경·회수한다. 모든 획 ID는 불변이므로 수정은 지우기와 새 ID 추가로 표현한다.

256비트 초대는 선택한 권한으로 24시간·1회 사용하며 서버에는 토큰 해시만 보관한다. 새 초대에서 권한을 생략하면 `viewer`가 기본값이다. 기존에 발급한 편집 초대와 기존 `owner`·`editor` 멤버십은 migration이 보존한다. 이미 참여한 계정이 다른 초대를 수락해도 기존 권한을 조용히 올리거나 낮추지 않는다. 기존 구성원의 권한은 소유자의 명시적 변경으로만 바뀐다. 로그인한 수신자는 유효한 초대의 권한·문서 제목을 수락 전에 확인할 수 있으며, 미리보기 자체는 노트 열람 권한을 만들지 않는다. 공유 링크는 사용자가 전달하며 서버가 메일을 발송하지 않는다.

획의 `author_id`와 쓰기 요청의 `actor_id`는 서버가 세션 계정으로 기록하며 클라이언트 JSON에서 받지 않는다. SQLite의 INSERT·UPDATE 권한 trigger가 실제 쓰기 트랜잭션 안에서 현재 멤버십과 작성자를 다시 검사한다. 애플리케이션 검사 이후 권한이 바뀌거나 한 요청의 나중 작업이 금지되어도 전체 D1 batch가 취소된다. 일부 허용된 획만 저장하거나 다른 사람의 필기를 지우는 tombstone을 남기지 않는다. 새 요청마다 멤버십을 확인하며 다른 노트 ID를 추측해도 필기나 구성원 목록을 반환하지 않는다.

필기는 페이지별 정규화 좌표와 고유 stroke ID로 저장한다. 새 stroke의 ID는 불변이며 지우개는 영구 tombstone을 기록한다. 두 기기의 추가 필기를 합치고 재전송은 중복으로 저장하지 않는다. 늦게 접속한 기기가 지운 stroke를 다시 보내도 되살리지 않는다. 실행 취소로 지운 필기를 복원할 때 클라이언트는 새 ID를 생성해야 한다. SQLite trigger가 변경 순서를 부여하므로 `pages?since=...`로 공유 변경을 순차 수신할 수 있다. 현재 프런트의 주기적 동기화를 위한 계약이며 WebSocket 수업 모드를 구현했다고 표시하지 않는다. 읽던 페이지와 책갈피는 공유 필기와 달리 각 계정의 멤버십에 따로 보관한다.

변경 피드는 현재 stroke 상태를 기본키로 함께 조회한다. 현재 지워진 획의 과거 `put`도 좌표 없이 `delete`로 반환하므로, 나중에 초대된 보기 전용 계정이 `since=0`으로 요청해도 지우기 전 필기를 복구할 수 없다. 원래 revision·순서는 유지해 페이지 나눔과 오프라인 삭제 전파를 보존한다. 이는 API 응답의 비노출 처리이며 저장된 변경 원장의 물리적 영구 삭제 기능은 아니다. 이미 다른 기기로 전달·내보낸 사본을 회수하지도 않는다.

공개 렉처는 현재 게시 카탈로그의 `lecture:` ID만 연결한다. 개인 PDF는 `publicId:null`과 SHA-256 fingerprint·제목·쪽수로 식별한다. `0006_study_library.sql`부터 소유자가 명시적으로 선택하면 원본 PDF를 비공개 R2에 보관할 수 있다. R2가 연결되지 않았거나 원본을 올리지 않았다면 다른 기기에서 같은 파일을 가져와 fingerprint를 확인한다. 개인 필기·계정·초대·원본 파일은 공개 발행 카탈로그나 정적 자산에 포함하지 않는다. 서버의 요청 오류 로그에는 원문 필기나 이름·초대 토큰을 출력하지 않는다.

요청 한도는 JSON 1 MB, 한 번에 stroke 작업 100건, stroke당 점 5,000개, 계정당 활성 소유 노트 100권·휴지통 포함 보관 노트 200권, 노트당 stroke/tombstone 25,000개와 활성 필기 JSON 약 12 MB다. 로그인·등록·노트 생성·수정·초대는 기존 회전 IP 해시 또는 계정 해시를 이용해 별도로 제한한다. 만료된 세션·challenge·초대는 기존 정리 Cron에서 제거한다.

노트별 `stroke_count`는 tombstone을 포함한 고유 ID 수, `ink_bytes`는 활성 stroke JSON 크기다. migration이 기존 값을 한 번 채우고 기존 변경 trigger의 노트 UPDATE 안에서 함께 갱신한다. 각 저장에서 전체 노트의 `COUNT/SUM`을 반복하지 않고 노트 기본키 한 건으로 용량을 확인한다. 추가·삭제·재전송·권한 오류의 트랜잭션 취소 때 카운터가 실제 행과 일치하는지 검사한다. 이 카운터는 실제 D1 저장 공간 과금 수치가 아니며 변경 이력·인덱스·행 메타데이터 공간은 별도로 든다.

최대 100건 저장 요청은 필요한 `(page,id)` 키를 한 JSON 매개변수에 담아 한 번에 미리 읽는다. `json_each`를 바깥 루프로 두고 stroke의 `(notebook_id,page,id)` 복합 기본키를 조회하므로 전체 노트를 스캔하지 않는다. 실제 query plan과 100건 요청의 D1 binding 호출 수를 검사한다. 인증·권한·rate limit·용량·실제 batch 저장·최신 권한 확인을 포함해 약 7회로 유지하며 획 수만큼 별도 binding 왕복을 만들지 않는다. 위치·책갈피만 저장하는 빈 작업 요청은 필기 미리 읽기를 건너뛴다.

| 경로 (`/v1/study/` 아래) | 동작 |
| --- | --- |
| `POST auth/register/options` `{displayName}` | 새 계정의 패스키 등록 옵션·challenge 쿠키 |
| `POST auth/register/verify` `{response}` | 등록 검증 후 `{account}`와 세션 쿠키 |
| `POST auth/login/options` `{}` | discoverable 패스키 로그인 옵션·challenge 쿠키 |
| `POST auth/login/verify` `{response}` | 실제 assertion 서명 검증 후 `{account}`와 세션 쿠키 |
| `GET me` | `{account,features,limits,usage}`; 미로그인 account/usage는 `null` |
| `POST logout` `{}` | 현재 세션 폐기 |
| `GET notebooks?includeDeleted=1&cursor=0&limit=200` | 허용 노트 목록·`nextCursor`; 휴지통은 소유자만 포함 |
| `POST notebooks` `{publicId,title,fingerprint,pageCount}` | 소유 노트 생성 또는 같은 fingerprint의 기존 소유 노트 반환 |
| `GET notebooks/:id` | 현재 권한·capabilities·페이지별 stroke·작성자·삭제 ID·본인 위치·책갈피 |
| `POST notebooks/:id/operations` `{operations,position?,bookmarks?}` | 추가·삭제와 본인 학습 위치 저장. 빈 작업 배열 허용 |
| `GET notebooks/:id/pages?since=N` | 변경 최대 100건과 작성자, `revision`·`more` 및 현재 노트 권한. 필기 변경 없이도 권한 변경 반영 |
| `POST notebooks/:id/invites` `{role}` | 소유자가 `viewer`·`contributor`·`editor` 중 선택한 24시간·1회용 초대 발급 |
| `POST invites/preview` `{token}` | 로그인한 수신자에게 초대의 권한·제목·문서 식별정보 확인. 멤버십을 부여하지 않음 |
| `POST invites/accept` `{token}` | 처음 참여하는 로그인 계정에 초대 권한 부여. 기존 구성원 권한은 유지 |
| `GET notebooks/:id/members` | 소유자에게 `{accountId,displayName,role}` 목록 |
| `PATCH notebooks/:id/members/:accountId` `{role}` | 소유자가 기존 비소유자 구성원 권한 변경 |
| `DELETE notebooks/:id/members/:accountId` | 소유자가 비소유자 구성원 권한 회수 |

작업의 JSON 형태는 `{type:'put',page,stroke:{id,color,width,points:[{x,y,p}]}}` 또는 `{type:'delete',page,id}`다. `x,y,p`는 0–1, `width`는 페이지 너비의 0–0.1 범위 양수다. 노트 메타데이터에는 `capabilities:{canRead,canAdd,canDeleteOwn,canEditAll,canManageMembers}`가 있다. 노트 생성 응답의 `revision`과 변경 응답의 `revision`은 정수이며, 변경 페이지 응답에는 실제 마지막 수신 순서와 `notebookRevision`이 별도로 있다. 전체 snapshot은 `{notebook,pages:[{number,strokes}],deleted:[{page,id}],strokeAuthors:[{page,id,accountId}],position:{page},bookmarks}` 형태다. 이전 필기의 `accountId`는 `null`이며 변경 피드에서는 `authorId`로 전달한다.

신규 migration 적용 후 Worker를 바로 배포한다. `0005`의 엄격한 쓰기 trigger는 새 서버 작성자 필드를 요구하므로 이전 Worker가 계속 실행되는 사이의 저장 요청은 재시도가 필요할 수 있다. 기존 알림과 pub/sub 키를 교체하거나 기기별 구독을 자동 변경하지 않는다. `npm test`는 pinned esbuild로 테스트 Worker를 묶은 뒤 기존 Miniflare 검사와 독립 서명 생성기를 이용한 패스키·권한별 직접 API·권한 변경 경합·혼합 batch 취소·공유 동시 필기 검사를 실행한다. 실제 iPad 생체인증·플랫폼 패스키 복구 테스트를 대신한 것으로 표시하지 않는다.

## 개인 원본·학습본·초안 · 0006

`0006_study_library.sql`은 같은 PDF에서 여러 학습본을 만들 수 있도록 기존 노트 테이블을 재구성한다. 부모를 지우기 전에 자식 테이블을 백업·분리하고 기존 ID, 권한 네 종류, 획·삭제 이력, revision, 카운터, 초대, 계정·기존 인증 정보를 보존한다. 채워진 이전 스키마에서 원형 보존과 실패 트랜잭션 rollback을 검사한다. 운영 적용 전 보호된 D1 백업을 확보하고 migration과 새 Worker를 함께 적용한다.

`copy`는 읽을 수 있는 노트의 활성 필기를 새 획 ID로 복제하여 요청한 계정이 소유하는 개인 학습본을 만든다. 공유 구성원은 복사하지 않는다. `reset`은 같은 원본의 필기 없는 새 학습본을 만들며 기존 공유 노트·필기·학습 위치를 지우지 않는다. 같은 소유자의 사본은 이미 보관한 원본을 재사용한다. 다른 소유자의 사본에는 원본 R2 참조를 넘기지 않으므로 현재 기기에 있는 동일 PDF를 활용하거나 새 소유자가 자신의 저장 한도에서 원본을 별도로 올린다.

휴지통 이동·복원은 소유자만 가능하다. 휴지통에서는 구성원 열람·필기·초대 수락을 중지하며, 소유자가 복원하면 기존 ID·권한·필기를 유지한다. 휴지통 이동은 발표를 종료하고 그 노트의 검토 중/승인된 공개 신청을 철회한다. 휴지통이나 원본을 자동 영구 삭제하지 않으며 보관된 원본도 500MiB 한도에 포함된다. 영구 삭제·계정 삭제·잃어버린 모든 패스키의 관리자 복구 기능은 아직 없다. 사용자가 내보낸 사본이나 이미 받은 다른 기기의 자료를 회수하지 않는다.

### 선택적 R2 연결

기본 `wrangler.jsonc`에는 R2 binding이 없다. 버킷이 준비되지 않아도 나머지 개인 학습 기능을 배포할 수 있으며 `GET me`의 `features.documentStorage`가 `false`가 된다. 업로드/다운로드는 기다리지 않고 `document_storage_unavailable` 503을 반환한다. `wrangler.r2.example.jsonc`에 `STUDY_DOCUMENTS` → `infant83-study-documents` 예제를 둔다. 운영자가 올바른 계정의 R2 이용 가능 상태·권한을 확인하고 비공개 버킷을 만든 후 정식 설정에 binding을 추가한다. `r2.dev`나 공개 custom domain을 켜지 않는다. 계정·가입·과금 설정을 이 코드가 자동으로 변경하지 않는다.

원본은 파일당 50MiB, 업로더 계정당 합계 500MiB까지 보관한다. 진행 중 업로드 예약도 합계에 포함하여 동시 업로드가 한도를 넘지 않게 한다. `GET me`와 `GET usage`에서 실제 보관 바이트·한도·노트 수를 표시한다. 원본은 `%PDF-` magic, 실제 바이트 수와 SHA-256을 확인하고 업로더/fingerprint 키에 조건부 생성한다. 새 내용은 새 fingerprint/학습본으로 저장하며 기존 원본을 덮지 않는다. 동일 계정의 같은 원본은 중복 보관하지 않는다. nonce 임시 객체는 검증 후 제거하고 실패/만료 예약은 정리한다. 원본 GET은 매 요청마다 현재 멤버십을 확인하고 R2 응답을 기다린 뒤에도 회수 여부를 다시 확인한다. 응답은 `private, no-store`다.

업로드는 native `crypto.DigestStream`과 `FixedLengthStream`으로 읽으므로 50MiB 파일 전체를 JavaScript 메모리에 모으지 않는다. 최대 파일의 실제 production CPU는 아직 측정하지 않았으며 Workers Free의 요청당 CPU 10ms에서 50MiB 전량 처리를 보장하지 않는다. 실제 invocation CPU/실패율을 확인한 뒤 필요하면 R2 native checksum 검증이나 실행 요금제를 별도로 검토한다. 로컬 wall time을 production CPU 측정으로 표시하지 않는다.

2026-11-05 [R2 Standard 요금](https://developers.cloudflare.com/r2/pricing/)은 월 저장 10GB·Class A 100만 회·Class B 1,000만 회가 무료 구간이며 초과분은 각각 $0.015/GB-month, $4.50/100만 회, $0.36/100만 회다. egress는 무료다. 신규 업로드는 임시/최종 PUT과 검증 GET을 사용하므로 원본 하나당 정확히 한 연산으로 계산하지 않는다. 필기 D1, Worker 요청·CPU, 기타 기존 구독 비용은 별도다.

### 기존 계정에 패스키 추가

새 계정 등록과 기존 계정의 인증 수단 추가를 분리한다. 로그인 상태의 `auth/register/options`는 거절한다. 추가·삭제 전 현재 계정의 기존 패스키로 `auth/reauth/*` 사용자 확인을 다시 받고, 같은 세션의 5분 이내 1회 승인으로 `auth/credential/options` 또는 credential 삭제를 진행한다. 새 credential은 기존 account/user handle에 연결하며 계정을 새로 만들지 않는다. 최대 10개이고 마지막 하나는 DB trigger로 삭제를 막는다. 플랫폼 패스키 관리자에서 동기화된 키나 다른 기기·보안 키를 사용할 수 있지만 서버가 개인키나 이메일 복구 코드를 대신 만들지는 않는다.

### 비공개 초안과 공개 신청

초안은 작성자 계정만 읽는다. 직접 쓴 제목·요약·본문과 선택적으로 연결한 본인 원본 PDF를 공개 신청에 담을 수 있으며 개인 필기는 자동 포함하지 않는다. 제출 시 공개 권리 확인이 필수다. 심사 중 초안은 잠기고 제출 텍스트와 원본 참조는 snapshot으로 유지한다. 승인/반려 후 수정하면 별도 새 신청이 되며 이전 심사 snapshot은 바뀌지 않는다. 철회된 신청은 심사자에게도 열리지 않으며 R2를 읽는 도중 철회되어도 반환 직전에 다시 확인한다.

심사 API는 운영 환경의 `STUDY_REVIEWER_ACCOUNT_IDS` 허용 목록에 든 계정만 사용할 수 있다. 빈 목록은 심사자 없음이다. 일반 owner/editor 공유 권한은 이 권한을 주지 않는다. 승인 응답도 `published:false, editorialExportRequired:true`이며 공개 카탈로그·게시물·알림을 자동 생성하지 않는다. 실제 발행은 기존 편집/게시 절차에서 별도 수행한다. 심사 이력의 영구 삭제·발행 후 철회 자동화는 이번 API 범위에 없다.

### 선택적 발표 페이지 따라가기

owner/editor가 4시간짜리 발표 세션을 시작하고 발표자 또는 owner가 쪽을 바꾸거나 종료한다. 다른 유효 발표자가 쓰는 세션은 editor가 빼앗지 못한다. 현재 권한·발표 ID는 실제 SQL 쓰기 시점에 확인하므로 요청 도중 권한 회수나 발표자 교체가 일어나도 이전 요청이 새 발표를 덮지 못한다. 만료/권한 회수된 발표는 새 editor가 시작할 수 있다. 독자가 따라가기를 켠 경우 기존 delta polling에 `follow=1`을 붙여 쪽 metadata를 받는다. 다른 계정의 개인 학습 위치를 덮지 않으며 WebSocket/음성·영상 강의가 아니다.

| 경로 (`/v1/study/` 아래) | 동작 |
| --- | --- |
| `GET usage` | `{usage,limits}`; 원본 바이트·개수·노트/휴지통 수 |
| `POST notebooks/:id/copy` `{title?,includeInk?}` | 읽기 권한으로 본인 소유의 독립 사본 생성 |
| `POST notebooks/:id/reset` `{title?}` | 기존 노트를 보존하고 빈 개인 학습본 생성 |
| `DELETE notebooks/:id` `{}` / `POST notebooks/:id/restore` `{}` | owner 휴지통 이동/복원 |
| `POST notebooks/:id/document?size=N` | owner의 `application/pdf` 원본 업로드; 실제 길이·해시 검증 |
| `GET notebooks/:id/document` | 현재 읽기 구성원에게 비공개 원본 스트림 |
| `POST auth/reauth/options` `{}` / `POST auth/reauth/verify` `{response}` | 기존 계정 패스키 사용자 확인 |
| `GET credentials` | 본인 `{credentials:[{id,label,createdAt,lastUsedAt}]}` |
| `POST auth/credential/options` `{label}` / `POST auth/credential/verify` `{response}` | 본인 계정에 추가 패스키 바인딩 |
| `DELETE credentials/:id` `{}` | 최근 재확인 후 본인 패스키 삭제; 마지막 키 제외 |
| `GET/POST drafts`, `GET/PATCH drafts/:id` | 개인 초안 목록/저장/수정; `title,summary,body,notebookId` |
| `POST drafts/:id/submit` `{rightsConfirmed:true}` / `POST drafts/:id/withdraw` `{}` | 비공개 검토 신청/철회 |
| `GET review/submissions`, `GET review/submissions/:id[/document]` | 지정 심사자에게 신청/snapshot/선택 원본 확인 |
| `POST review/submissions/:id` `{decision,note?}` | 지정 심사자 승인/반려; 자동 발행 없음 |
| `GET/POST/PATCH/DELETE notebooks/:id/presentation` | 발표 상태/시작/쪽 변경/종료; POST/PATCH `{page}` |

기존 GitHub Pages HTML·아이콘·URL을 유지하고, 좋아요·새 글 알림·개인 학습에 필요한 API를 Cloudflare Worker에 둔다. Worker는 `api.infant83.io`, 웹페이지는 `https://infant83.io/AI_Tech_Review/`를 사용한다. API·DB 장애가 나도 원래 정적 글을 읽을 수 있다.

```text
GitHub main → 기존 Pages 빌드·배포 → 기존 페이지 + reader-publications.json
                                      ↓ 배포 성공 뒤 검증된 카탈로그 동기화
독자 브라우저 ↔ api.infant83.io Worker ↔ D1
                                      ↓ durable outbox
                         Queue fanout → 기기별 Queue 작업 → Apple/Google 등 Web Push
```

## 포함한 동작

- 기기 세션: 256비트 난수의 SHA-256 해시만 D1에 저장한다. 원본은 API 호스트 전용 `__Host-reader_session` HttpOnly·Secure·SameSite=Strict 쿠키다. JavaScript에 세션 토큰을 반환하지 않는다.
- 좋아요: 공개 카탈로그에 있는 글만 허용하고 기기·글당 하나로 집계한다. 영어·한국어 페이지가 같은 글 ID를 쓴다. 로그인 계정은 아직 없으며 `user_id` 열은 향후 연결용이다.
- 구독: 기기당 Web Push endpoint 하나와 `review`, `lecture` 주제 선택을 저장한다. 이 데이터는 소유 기기의 쿠키로만 읽고 바꾼다.
- 발행: 처음 동기화는 기존 글 기준선만 만든다. 기존 ID의 제목·본문 수정, 재배포, 삭제 후 같은 ID 복원에는 새 글 알림을 보내지 않는다. 이후 처음 등장한 ID만 발행 이벤트를 만든다. 기존 글 업데이트 재알림은 별도 기능을 구현하기 전까지 제공하지 않는다.
- 테스트: 본인 기기의 현재 구독 하나에만 테스트 알림을 접수한다. 기기당 60초에 한 번, UTC 하루 다섯 번이다. `queued:true`는 발송 작업 접수이며 실제 단말 도착 확인은 아니다.

리뷰 ID는 기존 폴더 이름, 렉처 ID는 `lecture:` 뒤 기존 archive 문서 ID다. 렉처의 ID와 웹 슬러그는 다를 수 있다. 기존 PDF 전용 렉처도 `/AI_Tech_Review/archive/files/<name>.pdf` 주소를 보존한다. 카탈로그는 500개, 제목은 240자까지 허용한다.

## 파일과 리소스

| 대상 | 값 |
| --- | --- |
| Worker | `infant83-reader-engagement` |
| D1 | `infant83-reader-engagement`, 바인딩 `DB` |
| Queue | `infant83-reader-notifications`, 바인딩 `READER_QUEUE` |
| 복구 Cron | 10분마다 미완료 outbox를 다시 큐에 넣음 |
| 스키마 | `migrations/0001_reader_engagement.sql` |
| 런타임 | Node 호환 레이어 없는 Web Crypto + D1 + Queues |

`wrangler.jsonc`의 account/database ID는 식별자다. 비밀 키와 배포 인증정보는 여기에 넣지 않는다. `.secrets/`, `.dev.vars*`, `.wrangler/`, `node_modules/`는 Git에서 제외한다. 이 폴더 전체를 웹사이트 정적 산출물로 복사하지 않는다.

## 비밀값 설정과 보관

| 이름 | 사용처 |
| --- | --- |
| `VAPID_PUBLIC_KEY` | 브라우저 구독 등록에 공개하는 P-256 공개키 |
| `VAPID_PRIVATE_KEY` | Worker에서만 쓰는 VAPID 개인키 |
| `VAPID_SUBJECT` | 푸시 제공자가 확인할 HTTPS 사이트 또는 mailto 연락처 |
| `READER_PUBLISH_TOKEN` | GitHub 게시 workflow → `/v1/publications/sync` 전용 비밀 |
| `RATE_LIMIT_SALT` | IP를 저장하지 않고 일 단위 회전 해시를 만드는 서버 비밀 |

다음은 새 설치에서 한 번만 실행한다. 기존 VAPID 키가 있으면 새로 생성하지 말고 복구한 키를 사용한다.

```sh
node scripts/generate-secrets.mjs --subject https://infant83.io/
```

기본 결과는 `.secrets/reader-engagement.env`에 저장된다. 파일 권한은 0600, 새 상위 디렉터리는 0700이며 기존 파일을 덮어쓰지 않는다. 값은 stdout에 출력하지 않는다. 이 파일은 비밀번호 관리자나 암호화된 별도 저장소에 백업한다. 화면 공유·채팅·공개 문서·Git·빌드 아티팩트에 넣지 않는다.

프로비저닝·배포 권한은 필요한 계정의 Workers Scripts, D1, Queues 및 custom domain을 위한 해당 zone에만 제한한다. Global API Key는 필요 없다. GitHub 게시 workflow에는 도메인 전체 관리 토큰이나 VAPID 개인키 대신 `READER_PUBLISH_TOKEN`만 전달한다. Worker의 VAPID와 salt는 Cloudflare secrets로 등록한다. 대시보드 입력 또는 Wrangler의 안전한 secret 입력을 사용하고 값을 명령행 인수로 넘기거나 출력하지 않는다.

VAPID 개인키를 분실해 새 키로 바꾸면 기존 브라우저 PushSubscription은 이전 공개키에 묶여 있어 구독을 취소한 뒤 새 키로 다시 등록해야 한다. 개인키를 유지하면 같은 발신자 키를 복구할 수 있다. `READER_PUBLISH_TOKEN`은 Worker와 GitHub secret을 함께 교체하며 구독 재등록은 필요 없다. `RATE_LIMIT_SALT` 교체는 기존 IP 제한 이력 연결만 끊는다.

## 로컬 실행

Node 22 이상과 Wrangler를 사용한다. 다음 명령은 이 폴더에서 실행한다.

```sh
npm ci
npm run check
npm test
npx wrangler d1 migrations apply DB --local
```

개발 전용 키 파일을 `.dev.vars`에 두고 다음 두 설정을 추가한다. 실제 비밀값 파일 내용은 공유하지 않는다.

```dotenv
DEV_ALLOWED_ORIGINS=http://localhost:8000
DEV_ALLOW_INSECURE_COOKIE=true
```

개발 UI와 API에서 호스트 이름을 둘 다 `localhost`로 맞춘다. 포트는 달라도 된다. `127.0.0.1`과 혼용하면 쿠키 사이트가 달라진다. 프론트 개발 설정의 API 주소는 `http://localhost:8787`이다. 개발 Origin은 명시한 loopback 주소만 추가할 수 있다. `DEV_ALLOW_INSECURE_COOKIE`는 요청 API 호스트가 loopback일 때만 `reader_session` 비보안 쿠키를 허용한다. 실서비스 호스트에서는 항상 Secure 쿠키를 사용한다.

공개 production feed가 아직 배포되지 않았어도, 생성된 로컬 카탈로그를 로컬 D1에만 넣어 UI를 확인할 수 있다.

```sh
node scripts/seed-local.mjs ../../../site/reader-publications.json
npx wrangler d1 execute DB --local --file=.wrangler/reader-local-seed.sql
npx wrangler dev --local
```

seed 도구는 SQL 파일만 작성하며 네트워크·DB에 연결하지 않는다. 로컬 seed에는 알림 이벤트가 없다. 이 SQL을 `--remote`로 적용하지 않는다. 원격 최초 기준선은 아래의 검증된 발행 동기화를 사용한다. 로컬 기기 구독도 실제 endpoint를 등록한 뒤 테스트 알림을 누르면 실제 푸시 제공자에 요청하므로, 가짜 endpoint UI 테스트와 본인 단말의 실제 푸시 테스트를 구분한다.

## 최초 배포 순서

1. Workers Free와 zone Free를 확인한다. `wrangler.jsonc`의 계정·DB ID와 `api.infant83.io` custom domain 설정을 확인한다.
2. D1과 Queue를 만들고 스키마를 적용한다. 이미 만든 리소스는 재사용한다.
3. Worker secrets 다섯 개를 설정한 뒤 Worker를 배포한다. custom domain 인증서와 HTTPS가 준비됐는지 확인한다.
4. Pages에 기존 글·아이콘과 새 컨트롤·service worker·카탈로그를 배포한다. 기존 GitHub Pages 호스팅을 계속 사용한다.
5. 해당 Pages 배포의 공개 JSON과 글 URL을 검증한 뒤 같은 JSON을 `/v1/publications/sync`에 보낸다. 첫 응답의 `baseline:true`, `newArticles:0`을 확인한다.
6. 본인 iPhone에서 홈 화면에 추가한 웹앱을 열고 구독을 등록한다. 테스트 알림의 실제 잠금화면·알림센터 표시와 글 링크를 확인한다. Android도 브라우저별로 확인한다.

리소스가 없는 새 계정의 명령 예시는 다음과 같다. 원격 쓰기이므로 운영자가 설정과 계정을 확인한 뒤 실행한다.

```sh
npx wrangler d1 create infant83-reader-engagement
npx wrangler queues create infant83-reader-notifications
npx wrangler d1 migrations apply DB --remote
npx wrangler deploy
```

## API 계약

브라우저 요청은 `credentials:'include'`를 사용한다. 쿠키를 읽는 GET을 포함해 credentialed CORS는 `https://infant83.io`만 허용한다. 일반 쓰기는 정확한 Origin이 필수다. 게시 전용 경로만 Bearer secret으로 CI의 Origin 없는 요청을 허용한다. HTML·기기 ID·요청 JSON으로 임의의 발신 대상이나 구독자 전체 발송을 지정할 수 없다.

| 경로 | 동작 |
| --- | --- |
| `GET /v1/config` | 공개 VAPID 키·지원 주제·pushEnabled |
| `POST /v1/devices` `{}` | 기존 유효 쿠키 재사용 또는 세션 생성, `{ok,deviceId}` |
| `GET /v1/articles/:id/like` | 공개 count, 쿠키가 있으면 liked |
| `PUT /v1/articles/:id/like` `{liked:boolean}` | 본인 기기의 좋아요 설정 |
| `GET /v1/subscription` | 본인 구독과 topics 조회 |
| `PUT /v1/subscription` `{subscription,topics}` | 본인 구독 등록·수정 |
| `DELETE /v1/subscription` | 본인 서버 구독 삭제 |
| `POST /v1/subscription/test` `{}` | 본인 단말 한 개에 테스트 알림 접수 |
| `POST /v1/publications/sync` `{revision,articles}` | 게시 전용 Bearer secret, 공개 feed 검증 후 동기화 |
| `GET /v1/metrics[?articleId=...]` | 공개 집계만 조회. 세션이나 쿠키 불필요 |
| `POST /v1/metrics/events` `{type,visitorId,eventId,articleId}` | 공개 집계 이벤트. 정확한 Origin 필수, 세션 생성 안 함 |
| `GET /v1/discovery[?period=all\|7d\|30d\|90d]` | 활성 글 최대 500개의 누적 카드 숫자와 활동 기간 정렬 숫자. 세션 불필요 |
| `GET /v1/discovery?from=YYYY-MM-DD&to=YYYY-MM-DD` | 한국 날짜 양 끝을 포함한 사용자 지정 활동 기간 |

### 방문·열람·공유·구독 통계

`0002_public_metrics.sql`을 기존 DB에 적용한 뒤 새 Worker를 배포한다. migration이 기록한 `since` 시점부터 방문·열람·공유·등록 전환을 집계하며 이전 수치를 추정해 채우지 않는다. 기존 구독은 현재 활성 구독 기기 수에 포함하고, 기존의 실제 새 글 발송 기록도 발송 합계에 포함한다. 테스트 알림은 발송 합계에서 제외한다. 과거 `.automation/cloudflare/ai-tech-review-public-metrics` Worker는 이 기능에 사용하지 않으며 두 집계기를 동시에 활성화하지 않는다.

이벤트 `type`은 `open`, `share`, `copy` 중 하나다. `visitorId`, `eventId`는 UUID v4 문자열이어야 한다. 브라우저는 이 사이트 전용 난수 방문 ID를 localStorage에 보관하고 성공한 사용자 동작마다 새 이벤트 ID를 만든다. 글 없는 허브 방문은 `{type:"open",articleId:null}`이다. 공유·복사는 활성 카탈로그의 글 ID가 필요하다. 알려지지 않았거나 비활성인 글은 404이며 추가 JSON 필드, 중복/미지원 query 필드, 잘못된 UUID와 512바이트 초과 본문은 거절한다.

응답은 GET과 POST가 동일하다.

```json
{
  "ok": true,
  "since": "2026-10-25T00:00:00.000Z",
  "site": {
    "visitors": 0,
    "todayVisitors": 0,
    "opens": 0,
    "shares": 0,
    "copies": 0,
    "activeSubscribers": 0,
    "subscriptionRegistrations": 0,
    "articleNotificationsSent": 0
  },
  "article": null
}
```

글 ID가 있으면 `article`은 `{id,opens,shares,copies}`다. 모든 수치는 음수가 아닌 정수이며 응답에 방문 해시, 기기 ID, endpoint, 구독 주제나 브라우저별 이력을 포함하지 않는다.

- `visitors`: 측정 시작 후 서로 다른 방문 브라우저 수다. 같은 사람의 다른 기기·브라우저나 localStorage 삭제 후 방문은 별개로 집계할 수 있으므로 사람 수나 가입 회원 수로 표현하지 않는다.
- `todayVisitors`: 한국 시간 자정 기준 당일 방문 브라우저 수다.
- `opens`: 같은 브라우저·글·한국 날짜별 한 번의 열람이다. 한국어와 영어는 같은 글 ID를 써 중복을 줄인다. 새로고침과 동시 탭은 그날 같은 글의 숫자를 다시 올리지 않는다. 허브 방문만으로 글 열람은 늘지 않는다.
- `shares`, `copies`: 프런트가 native share 성공 또는 clipboard 쓰기 성공을 확인한 뒤 전송한다. 공유창 취소·실패·단순 버튼 클릭은 보내지 않는다. API는 이벤트 ID의 재전송을 중복 집계하지 않는다. 실제 수신자 전달·링크 열람 여부는 이 수치로 알 수 없다.
- `activeSubscribers`: 만료되지 않았고 하나 이상 주제를 구독하는 현재 기기 수다. 브라우저에서 권한을 끈 사실을 서버가 즉시 알 수는 없으며, 명시적 해제·만료·푸시 제공자의 404/410을 통해 갱신된다.
- `subscriptionRegistrations`: 측정 시작 후 비활성→활성 구독 전환 횟수다. 설정 저장·주제 변경·활성 endpoint 교체·같은 endpoint의 기기 세션 이전은 증가시키지 않는다. 해제 후 재등록이나 만료 뒤 재등록은 새 전환이다. 조건 검사와 구독 쓰기는 한 D1 batch 트랜잭션이라 동시 재전송도 한 번만 센다.
- `articleNotificationsSent`: 푸시 제공자가 수락해 `sent`가 된 새 글·기기 조합의 수다. migration에서 기존 실제 기록을 합계로 옮기고, 이후 delivery별 중복 방지 표식과 trigger로 한 번만 누적한다. 공개 조회마다 전체 발송 이력을 스캔하지 않는다. 재시도 횟수, 테스트 알림, 단말 표시나 사용자의 읽음 수가 아니다.

서버에는 `RATE_LIMIT_SALT`로 용도를 구분해 해시한 방문 식별자만 저장한다. 원본 방문·이벤트 ID, 원본 IP, User-Agent는 D1에 저장하지 않는다. lifetime 방문 해시는 누적 중복 방지용으로 유지하고, 방문·글별 일일 중복 키는 2일, 공유·복사의 해시 이벤트 중복 키는 7일 후 기존 10분 Cron에서 정리한다. 기간 집계 숫자는 유지한다. salt 변경 또는 브라우저 저장소 초기화는 같은 방문을 새 브라우저로 셀 수 있으므로 분석용 식별자의 안정성에 영향을 준다.

알려진 crawler, prefetch/prerender 및 `Sec-GPC: 1`/`DNT: 1` 요청은 집계하지 않는다. 자동 트래픽의 완전한 식별이나 악의적인 수치 조작 방지를 보장하지는 않는다. 이벤트는 브라우저 해시당 시간당 120회, 회전 IP 해시당 시간당 600회이며 공유·복사는 브라우저당 하루 60회를 추가 제한한다. 거절된 이벤트는 집계 숫자를 바꾸지 않는다. 트래픽 통계 장애가 정적 글 읽기·공유·알림 구독을 막아서는 안 된다.

일일·이벤트 중복 키의 INSERT trigger가 집계를 올리므로, 중복 검사와 숫자 증가는 한 트랜잭션에서 처리된다. 15초 주기 체류 시간 전송이나 별도 유료 분석 서비스는 추가하지 않는다. 일일 방문 집계, 글 집계와 lifetime 합계만 공개한다. 현재 구현 범위는 `/AI_Tech_Review/`이며 루트 개인 랜딩페이지는 별도 연동 전까지 이 통계에 포함하지 않는다.

### 글 카드와 기간별 인기순 탐색

`0003_review_discovery.sql` 적용 후 `GET /v1/discovery`를 사용한다. 기존 글·아이콘·GitHub Pages 구성은 바꾸지 않는다. 이 경로는 공개된 활성 카탈로그의 글 ID와 집계 숫자만 반환하고, 개인별 좋아요 여부나 읽은 글 이력을 공개하지 않는다. 쿠키가 필요 없으며 기기 세션을 만들거나 갱신하지 않는다. 응답은 `Cache-Control: public, max-age=30`, `Vary: Origin`으로 최대 30초의 브라우저 캐시를 허용한다. 이는 별도 서버 캐시나 새로운 Cloudflare 유료 서비스를 추가한 것이 아니다. 클라이언트의 `no-store` 요청은 새 읽기를 수행할 수 있다.

```json
{
  "ok": true,
  "since": "2026-10-25T05:42:25.151Z",
  "activitySince": "2026-10-25",
  "range": {"from": "2026-10-19", "to": "2026-10-25", "period": "7d"},
  "articles": [
    {"id": "example", "opens": 12, "likes": 3, "shares": 2, "copies": 1, "periodOpens": 5, "periodLikes": 1}
  ]
}
```

위 값은 계약 설명용 예시다. `since`는 기존 방문 통계 시작 ISO 시각이며 `activitySince`는 빠짐없이 보존되는 일별 활동 집계의 시작 **한국 날짜**다. 카드는 누적 `opens`, `likes`를 표시하고, 기간별 인기 정렬은 `periodOpens`, `periodLikes`를 사용한다. 주제·검색 필터와 화면 페이지 분할은 동일한 글 ID 목록 위에서 클라이언트가 조합할 수 있다. API 배열은 ID 오름차순이며 인기순을 미리 적용하지 않는다. 한국어·영어는 같은 ID로 합산하고 비활성 글은 배열에서 제외한다. 500개 초과의 비정상 활성 카탈로그는 일부만 조용히 반환하는 대신 503으로 실패한다.

- query가 없거나 `period=all`이면 모든 집계 기간을 사용한다. `range`는 `{from:null,to:null,period:"all"}`이며 기간 숫자는 누적 숫자와 같다.
- `period=7d`, `30d`, `90d`는 요청 시점의 한국 날짜인 오늘을 포함한 최근 7·30·90일이다. **게시 날짜 필터가 아닌 활동 날짜 필터**다. 오래전에 게시한 글도 해당 기간에 읽히거나 좋아요를 받으면 정렬에 반영된다.
- 사용자 지정은 `from`, `to`가 모두 필요하고 `period`와 함께 보낼 수 없다. 실제 존재하는 `YYYY-MM-DD`, `from <= to`, 양 끝 포함 3,660일 이하를 엄격히 검사한다. 초과 범위를 묵시적으로 줄이지 않는다. 같은 날짜 하루 범위도 가능하다. 응답의 `range.period`는 `"custom"`이다.
- 잘못된 날짜·기간, 추가 query 필드나 중복 필드는 400이다. Origin 검사는 기존 API와 같으며 요청 body를 받지 않는다.
- `periodLikes`는 **현재 취소되지 않은 좋아요 중 등록 시각이 선택 기간에 속하는 개수**다. 과거 버튼 클릭 수나 순증감 값이 아니다. 좋아요를 취소하면 원래 등록 날짜의 합계에서도 빠지고, 다시 누르면 새 등록 날짜로 센다. 무변경 저장은 한 번만 센다. `likes`는 현재 남아 있는 전체 좋아요 수다.

일별 공개 합계는 `metrics_article_daily(day,article_id)`에 보존한다. 방문·공유 원본의 짧은 중복 키를 Cron이 삭제해도 일별 합계가 사라지지 않는다. 누적 좋아요는 `metrics_articles.likes`에 저장하며, 좋아요 INSERT·DELETE와 글 ID/등록 날짜 변경 trigger가 누적·일별 값을 함께 유지한다. 공개 조회마다 개별 좋아요 전체를 스캔하지 않는다. 조회는 상태 한 건과 활성 글·선택 날짜 합계를 한 D1 batch로 읽으며 글마다 별도 API/DB 요청을 만들지 않는다. 일별 테이블 기본키의 날짜 범위를 사용한다.

migration은 남아 있는 실제 `metrics_daily_opens`와 `metrics_actions`만 일별로 복구하고, 기존 좋아요는 보존된 실제 `created_at`으로 복구한다. 공유 ledger의 날짜는 기존 7일 TTL에서 정확히 역산한다. 기존 누적 열람·공유 합계를 임의 날짜로 나누지 않는다. 과거 ledger가 이미 삭제된 환경에서도 누적 카드 숫자는 보존되지만 일부 오래된 기간 숫자는 알 수 없을 수 있다. 이를 숨기지 않도록 `activitySince`는 기존 통계 시작 한국 날짜와 migration 전날 한국 날짜 중 더 늦은 날로 보수적으로 기록한다. 현재 서비스는 통계 도입 당일 이 migration을 적용하므로 그 이전의 공개 방문 수치를 새로 만들지 않는다. `since` 이전이나 `activitySince`보다 이른 기간은 완전한 역사 통계로 설명하지 않는다.

발행 API는 `https://infant83.io/AI_Tech_Review/reader-publications.json`만 직접 가져온다. 임의 URL을 받지 않는다. 서버 nonce, 캐시 우회, redirect 거부와 writer lock 안의 revision·전체 metadata 비교를 적용한다. 같은 revision의 다른 내용은 409다. 같은 내용을 재처리해도 이벤트를 중복 생성하지 않으며, 과거에 처리한 revision으로 카탈로그 상태를 되돌리지 않는다. 공개 배포가 아직 맞지 않으면 409로 실패하여 CI가 재시도한다.

GitHub source commit과 Pages 배포 branch commit은 다를 수 있다. `revision`은 카탈로그를 생성한 main source SHA다. 외부 게시와 API DB 변경을 하나의 트랜잭션으로 묶을 수는 없으므로 GitHub 배포를 직렬화하고, CI와 Worker 양쪽에서 공개 feed를 확인한다.

## 전송·장애 복구

2026-11-11부터 명시적으로 구독한 새 글과 사용자가 직접 요청한 테스트는 Web Push의 `Urgency: high`로 즉시 전달 시도를 요청한다. 기존 TTL24시간·암호화·VAPID·Topic·대상 선택·재시도는 유지한다. 이는 운영체제의 집중 모드나 표시 설정을 우회하는 긴급 알림 등급이 아니며, 실제 도착·배너 표시를 보장하지 않는다. 과거 `normal` 설정이 관측한 지연의 원인이었다고 확정한 것도 아니다. [Apple 전송 문서](https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers)와 [RFC8030의 전송 우선순위](https://www.rfc-editor.org/rfc/rfc8030#section-5.3)를 따른다. 기존 수락 시각·기기의 새 글 수신 시각·사용자의 실제 표시 관찰을 구분하고, 확인을 위해 과거 알림을 재발송하지 않는다.

한 fanout 작업은 주제에 맞는 기존 구독 최대 20개를 cursor로 읽고, 실제 암호화·발송은 기기당 Queue 작업 하나씩 수행한다. fanout 이후 새로 가입한 구독에는 과거 새 글 알림을 보내지 않는다. 기기가 탈퇴·endpoint 변경·주제 해제를 하면 대기 중인 작업도 발송 직전에 다시 확인한다.

D1 outbox가 원본이며 Queue 메시지에는 이벤트·기기 식별자만 들어간다. 발행 이벤트/기기 복합키와 lease로 중복·동시 처리를 억제한다. 성공은 `sent`, 404/410은 구독 정리, 429/5xx/일부 인증 오류는 최대 여섯 번 지연 재시도한다. 10분 Cron은 큐 유실·lease 만료·미완료 fanout을 복구한다. 10초 네트워크 시간 제한이 있어 2분 lease보다 먼저 요청이 끝난다.

외부 푸시 제공자가 수락한 직후 Worker가 중단되면 DB에 `sent`를 기록하기 전에 재시도할 수 있다. 외부 전송의 exactly-once는 보장하지 않는다. 같은 이벤트의 안정적인 notification tag와 outbox 상태로 중복 표시를 줄인다. OS의 알림 설정·집중 모드·네트워크 상태에 따라 실제 표시가 지연되거나 차단될 수 있다.

테스트에는 Miniflare의 실제 D1/Workers API 통합 검증, SSRF/Origin/쿠키·소유권·쿨다운·처음 기준선/편집/새 ID·500개 카탈로그·페이지별 fanout·동시 재전송·410/429 처리가 포함된다. 암호문은 별도 `http_ece` 구현으로 복호화하고 VAPID 서명도 독립 검증한다. 로컬 테스트 통과가 실제 iPhone 알림 도착이나 Cloudflare production CPU 측정을 대신하지는 않는다.

## 무료 한도와 이전

2026-10-25 공식 문서 기준이다. zone Free/Pro는 DNS·보안 상품이고 Workers Free/Paid는 실행·데이터 상품이라 별개다. 이 구성은 무료 계정 한도 안에서 사용하며 자동 유료 업그레이드를 설정하지 않는다.

| 서비스 | Free 주요 한도 |
| --- | --- |
| Workers | 하루 100,000회, invocation당 CPU 10ms |
| D1 | 하루 읽기 500만 행·쓰기 10만 행, 계정 5GB, DB 하나 500MB, invocation당 binding API 호출 50회 |
| Queues | 하루 10,000 operations, 보관 24시간. 일반 성공 메시지는 쓰기·읽기·삭제 3 operations이고 재시도가 추가됨 |

한 글에 구독자 100명이면 푸시 메시지 100개에 약 300 operations와 fanout·복구 여유분이 필요하다. 이 수치는 보장 용량이 아니라 정상 성공 경로 예산이다. D1 인덱스 쓰기·레이트 제한·재시도도 사용량에 포함되므로 대시보드의 실제 사용량과 CPU 초과를 확인한다. 전체 구독자 암호화를 한 HTTP 요청에서 실행하지 않는다. 로컬 wall time으로 Free CPU 준수를 판정하지 말고 첫 실제 테스트 전송의 Cloudflare invocation CPU를 확인한다. 한도 초과 시 무료 기능이 제한될 수 있으며, 업그레이드는 별도 결정한다.

현재 HTML 호스팅과 API가 나뉘어 있어, 추후 Cloudflare 정적 호스팅이나 다른 프레임워크로 옮길 때도 기존 URL·아이콘·API 계약을 유지할 수 있다. D1 데이터는 내보내어 이전할 수 있지만 endpoint·구독키·세션 해시도 개인정보로 보호해야 한다. 푸시 구독은 origin·service worker scope·VAPID 공개키에 연결되므로 이 세 가지를 바꾸면 사용자 재구독이 필요할 수 있다. 계정, 검색, 댓글, AI는 같은 API 뒤에 별도 기능과 권한 체계로 추가한다.

공식 근거: [Workers 요금](https://developers.cloudflare.com/workers/platform/pricing/), [D1 요금](https://developers.cloudflare.com/d1/platform/pricing/), [D1 한도와 batch 예외](https://developers.cloudflare.com/d1/platform/limits/), [Queues 요금](https://developers.cloudflare.com/queues/platform/pricing/).
