# Reader engagement 운영 안내

기존 GitHub Pages HTML·아이콘·URL을 유지하고, 좋아요와 새 글 알림에 필요한 API만 Cloudflare Worker에 둔다. Worker는 `api.infant83.io`, 웹페이지는 `https://infant83.io/AI_Tech_Review/`를 사용한다. API·DB 장애가 나도 원래 정적 글을 읽을 수 있다.

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

발행 API는 `https://infant83.io/AI_Tech_Review/reader-publications.json`만 직접 가져온다. 임의 URL을 받지 않는다. 서버 nonce, 캐시 우회, redirect 거부와 writer lock 안의 revision·전체 metadata 비교를 적용한다. 같은 revision의 다른 내용은 409다. 같은 내용을 재처리해도 이벤트를 중복 생성하지 않으며, 과거에 처리한 revision으로 카탈로그 상태를 되돌리지 않는다. 공개 배포가 아직 맞지 않으면 409로 실패하여 CI가 재시도한다.

GitHub source commit과 Pages 배포 branch commit은 다를 수 있다. `revision`은 카탈로그를 생성한 main source SHA다. 외부 게시와 API DB 변경을 하나의 트랜잭션으로 묶을 수는 없으므로 GitHub 배포를 직렬화하고, CI와 Worker 양쪽에서 공개 feed를 확인한다.

## 전송·장애 복구

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
