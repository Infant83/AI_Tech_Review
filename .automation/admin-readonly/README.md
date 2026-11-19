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
