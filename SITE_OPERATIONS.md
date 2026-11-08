# 사이트 성장과 복구 관리

지속적인 개발 팀의 역할, 사용자·다른 세션의 피드백 인계, 일감·실행·사고 기록과 주기적 개선은 [개발 운영 정책 초안](DEVELOPMENT_OPERATIONS_POLICY.md)과 [개발 계획 초안](DEVELOPMENT_ROADMAP.md)에 정리한다. 기존의 아래 운영·게시 검증을 재사용하며 추가 상시 승인 게이트를 만들지 않는다.

게시물의 원본·글별 등록 JSON을 편집하고 후보를 다시 만든다. 검색 자료·카드·페이지·QML 회차 HTML은 생성물이다. 통계·개인 필기·계정 데이터는 공개 정적 파일과 별도 저장소에 있다. 일반 게시 작업은 해당 요청의 권한과 기존 검증 절차를 따른다. 이번 사이트 개편 검토를 매 게시물의 추가 승인 게이트로 확대하지 않는다.

## 글·검색·렉처

- 목록은 리뷰 6건, 아카이브·브리핑 12건씩 실제 HTML 페이지로 만든다. JavaScript가 없어도 페이지 링크로 과거 글에 접근한다. 검색은 전체 자료를 대상으로 한다. 주제·정렬 필터가 전체 목록을 필요로 할 때만 다른 목록 페이지를 읽는다.
- 검색 엔진과 자료는 검색창 사용 시 불러온다. 정규화와 색인 생성을 작은 비동기 묶음으로 나눠 화면에 실행 기회를 돌려준다. `scripts/site_payload_budget.py`는 검색 80KB gzip부터 성장 경고, 100KB부터 기존 예산 실패를 낸다. 실제 목록 페이지의 HTML·JS·CSS와 썸네일도 검사한다.
- QML 원본은 `2026-10-20_quantum-machine-learning-lecture-series/dist/index.html` 한 곳이다. 공개 후보 생성 시 원본 섹션을 회차와 부록 페이지로 나눈다. 본문·수식 SVG를 다시 쓰지 않고 링크만 해당 회차로 연결한다. 기존 코스 URL·앵커·PDF·문서 ID를 유지한다. 코스 전체 인쇄본은 기존 PDF다. 공개된 회차 파일을 직접 수정하지 않는다.
- 허브 요약·부제·분류·태그 편집과 본문 개정의 구분은 [글 등록 안내](PUBLICATION_WORKFLOW.md)를 따른다. 같은 문서의 동시에 시작한 편집은 기존 버전 토큰·입력 해시로 확인한다.

## PDF 개정판

`archive_documents.py`로 기존 PDF를 교체하면 정확한 이전 bytes를 `archive/editions/<문서 ID>/<SHA-256>.pdf`에 보존한다. 기존 문서 ID와 현재 PDF 주소는 유지한다. 이후 후보의 `archive-manifest.json`에는 검증한 구판 경로·크기·해시만 추가된다. 판본 파일을 수작업으로 덮어쓰지 않는다.

공용 PDF 학습 리더의 ‘저장·가져오기·도움말’에 구판이 있는 자료만 판본 선택이 나타난다. 구판 링크는 `?id=<기존 ID>#edition=<구판 SHA-256>`이며, 필기와 읽던 위치는 각 PDF의 기존 SHA-256에 그대로 대응한다. 클라우드 노트의 링크도 원래 PDF 해시를 지정한다. 새 판본으로 필기를 자동 복사하지 않는다. 이전 판본의 정확한 원본을 다시 열면 그 판본의 기존 필기를 사용할 수 있다. 개편 전 이미 덮어쓴 PDF의 옛 bytes를 이 기능이 소급 복원하지는 않는다.

## 공개 PDF 저장소 이전

현재 정적 배포본은 PDF를 계속 포함한다. 아래 도구는 **이전 준비용 내보내기**이며, 외부 업로드·운영 라우트 변경·원본 삭제를 하지 않는다.

```sh
python3 scripts/public_media.py --site output/후보/site --output output/media-export
python3 scripts/public_media.py --output output/media-export --verify
```

내보내기는 검증된 공개 산출물의 PDF만 읽고, 동일 PDF를 `pdf/sha256/<앞 두 글자>/<SHA-256>.pdf` 객체 하나로 만든다. `media-manifest.json`이 기존 공개 URL 여러 개를 같은 객체에 연결한다. PDF bytes를 바꾸지 않는다. 이 객체 묶음과 매핑은 R2·S3 계열·다른 정적 파일 서버로 옮길 수 있다. R2용 전달 코드는 별도 어댑터이며 사이트 본문·목록·검색은 계속 정적 파일이다.

외부 활성화 순서:

1. 공개 PDF 전용 버킷을 준비한다. 개인 필기·계정·개인 PDF 저장소와 섞지 않는다. 현재 CLI 연결에서 R2 조회 권한이 없으므로 R2 작업에는 공급자의 정상 권한 연결이 필요하다. 토큰을 Git이나 문서에 넣지 않는다.
2. `objects/`를 같은 키로 업로드한다. 업로드 뒤 전체 bytes를 다시 읽어 manifest SHA-256·크기와 대조한다. 파일 이름이나 ETag만으로 SHA 검증을 대신하지 않는다.
3. `worker/`의 생성 manifest와 전달 코드를 별도 시험 환경에서 확인한다. 기존 모든 URL, GET·HEAD·조건부 요청·바이트 Range·실제 PDF 리더와 구판 필기를 검사한다. 예제 설정에는 운영 라우트가 없다.
4. 같은 도메인의 기존 경로를 새 저장소에 연결한다. 크로스 오리진을 도입하면 CORS와 Range 헤더·브라우저 저장소 영향을 별도 확인한다. 새 게시 PDF는 객체 업로드·검증이 완료된 뒤에만 목록에 포함한다.
5. 운영 HTTPS 검증과 되돌림 시험을 마친 뒤 정적 사본 제거 및 연속성 검사의 원격 자산 지원을 별도 적용한다. 현재 검증기는 로컬 PDF를 계속 요구한다. 준비 도구만 도입한 이번 단계에서 배포 저장량이 줄었다고 간주하지 않는다.

정적 배포물 600MB부터 경고를 확인하고, 700MB 이전에 이전 시험을 마치며, 800MB 전에 실제 미디어 분리를 완료하는 것을 관리 목표로 삼는다. 이 숫자는 내부 관리 기준이며 공급자 요금제 한도가 아니다. Git 이력은 파일을 정적 배포에서 빼도 자동으로 줄지 않는다. 과거 Git 이력 재작성은 이 작업에 포함하지 않는다.

## 복구 사본

성공한 운영 배포 후 CI는 실제 Pages 아티팩트에서 전체 파일·카탈로그·스냅샷·소스 커밋을 묶고 모든 파일 SHA-256을 재검증한 `publication-recovery` 아티팩트를 만든다. 최근 세 개, 각각 최대 30일 보존한다. 실패한 빌드는 기존 복구 사본을 지우지 않는다. GitHub 아티팩트 저장 사용량은 별도로 발생하므로 전체 사본 약 0.4~0.5GB × 3 규모를 확인한다. 장기 보관할 기준본은 만료 전에 별도 저장소에 복사하고 해시를 확인한다.

```sh
python3 scripts/release_backup.py create --site output/후보/site --output output/release.tar.gz
python3 scripts/release_backup.py verify --archive output/release.tar.gz
python3 scripts/release_backup.py restore --archive output/release.tar.gz --output output/restore-drill
```

`create`에는 `publication_release.py seal`을 거친 정확한 아티팩트를 넣는다. 복원은 새 폴더에만 쓰고 운영 서버를 변경하지 않는다. 복원 후 목록·기존 글·PDF·해시를 확인한다. 공개 서버가 중단돼도 복원한 `site/`와 스냅샷을 로컬 비교 기준으로 사용할 수 있다. 실제 롤백은 최신 글의 제거와 알림·카탈로그 상태까지 검토하는 별도 작업이며 자동 우회 배포 명령을 추가하지 않는다.

이 사본은 **공개 정적 파일**만 복원한다. D1 계정·조회수·필기 동기화, 개인 기기의 IndexedDB, 개인 PDF나 인증 정보의 백업이 아니다. 개인 학습 자료는 기존 사용자 내보내기·백업 절차와 별도 운영 DB 복구 절차가 필요하다.

## 점검 주기

지원 목표는 최신 및 직전 안정판 Chrome·Edge 일반 모드·Firefox·macOS/iOS Safari다. IE11과 Edge의 IE 모드는 검색·PDF 필기·패스키 기능의 지원 대상에 포함하지 않는다. 이는 호스팅 공급자와 별개인 브라우저 기능 기준이다. 정확한 최소 버전은 해당 버전의 시험 없이 보장하지 않는다.

화면 검수는 320px 휴대폰 폭부터 2560px 와이드 화면까지, 세로·가로와 한영·명암 모드에서 검색 제출·범위 변경·지우기, 과거 목록, 렉처 회차·기존 앵커, PDF 쪽 이동을 직접 확인한다. 데스크톱의 화면 크기·터치 에뮬레이션과 WebKit 엔진 시험을 실제 Windows·Safari·iPhone/iPad·펜 입력·생체인증 시험으로 기록하지 않는다. 알림과 동기화는 실제 도메인의 보안·권한 환경에서 별도로 확인한다.

알림 권한을 허용하지 않은 방문자는 초기 화면에서 기존 Push 구독을 조회하지 않는다. 허용한 독자의 기존 구독 조회와, 알림 신청 버튼에서 권한을 얻은 뒤 구독하는 흐름은 유지한다. 자동 시험에는 기본·거부·허용 권한별 회귀 검사를 포함한다.

매 게시 시: 등록 스키마·중복 ID·원본 변경 의사·실제 이전 배포본과의 연속성·용량 예산·변경된 동선의 화면을 검증한다. 배포 후 실제 HTTPS 문서·PDF·리더와 알림 상태를 확인한다.

매주: 정적 배포/Git 증가량, 검색 80KB 경고, 깨진 링크와 API 오류, 기존 Cloudflare Web Analytics의 경로·기기별 LCP·INP·CLS를 확인한다. 실사용자 75백분위 관리 목표는 LCP 2.5초·INP 200ms·CLS 0.1이다. 로컬 압축량 감소를 실제 휴대폰의 속도 개선 수치로 바꾸어 말하지 않는다.

매월: 최근 복구 사본을 독립 폴더에 복원해 파일 해시·대표 경로를 확인하고, 아티팩트 만료·보관 용량·의존성·운영 한도를 점검한다. 임시 후보 정리 명령은 [글 등록 안내](PUBLICATION_WORKFLOW.md)의 보호·유지 규칙을 따른다. 원본·출판 요청·개인 자료를 임시 후보처럼 삭제하지 않는다.

공식 참고: [GitHub Pages 한도](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [R2 Workers API](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/), [R2 S3 호환성](https://developers.cloudflare.com/r2/api/s3/api/), [Core Web Vitals](https://web.dev/articles/vitals).
