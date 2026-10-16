# PDF 리뷰 아카이브

이 폴더는 Daily Quantum Review, 금요일 주간 리뷰, 사용자가 제공하는 개별 PDF 아티클을 리뷰 허브에 등록하는 원본입니다. `manifest.json`에 명시적으로 등록된 PDF만 공개 사이트에 복사됩니다. `files/`에 파일을 넣는 것만으로는 게시되지 않습니다.

사용자가 PDF를 제공하면 먼저 PDF 전체와 공개 제목·요약을 확인합니다. 개인 메일 주소, 수신자, 메일 시각, 비공개 링크, 로컬 경로 등 공개하면 안 되는 내용이 포함되어 있지 않은지 확인한 뒤 등록합니다. `--public-reviewed`는 이 확인을 마쳤다는 표시입니다. 스크립트의 파일 형식 검사는 PDF 내부의 모든 내용을 검토하지 않습니다.

## 최초 등록 · 2026-10-17

Daily Quantum Brief 54건(2026-08-22~2026-10-17, 총 260쪽)을 등록했습니다. 제목은 PDF 표지, 요약과 태그는 원문 내용에 근거합니다. 문서 분류 이름은 Daily Quantum Review이며 원래 시리즈명은 Daily Quantum Brief로 보존합니다. 영문 목록의 제목은 날짜별 안내이며, 한국어 PDF의 영문 번역본을 뜻하지 않습니다.

Codex의 PDF 수집·점검 역할이 전체 본문, 문서 메타데이터, 링크와 첨부 파일에서 이메일·메일 헤더·내부 경로·인증정보를 점검했고, 대표 표지를 시각 확인했습니다. 52건은 원본과 동일합니다. 8월 25·26일 자료는 PDF의 Author 메타데이터만 제거했으며 본문·페이지 수·링크·전체 페이지 렌더링의 동일성을 확인했습니다. 등록부의 공개 확인 표시는 이 배포 자료 점검을 뜻하며, 사람의 문장 단위 검토나 과학적 주장의 독립 재현을 뜻하지 않습니다.

공개 목록에는 메일 식별자, 송수신자, 메일 제목·시각, 첨부 다운로드 주소를 보존하지 않습니다. PDF 본문의 연구 결과와 해석은 발행 당시의 내용입니다. 이후 제공되는 주간·수시 자료도 같은 절차로 등록합니다.

등록 예시:

```sh
python3 scripts/archive_documents.py /absolute/path/review.pdf \
  --date 2026-10-16 \
  --series daily-quantum \
  --title 'Daily Quantum Review · 2026년 10월 16일' \
  --summary '이번 호에서 다루는 양자컴퓨팅 연구를 요약합니다.' \
  --language ko \
  --id 2026-10-16-daily-quantum-review \
  --tag Quantum \
  --source-title 'Daily Quantum Review' \
  --public-reviewed
```

`--series`는 `daily-quantum`(Daily Quantum Review), `weekly-review`(주간 리뷰), `article`(기타 아티클) 중 하나입니다. `--language`는 `ko` 또는 `en`입니다. 날짜는 실제 발행일을 사용하고, ID는 그 날짜와 영문 소문자·숫자·하이픈으로 만듭니다. 영문 제목·요약이 있으면 `--title-en`, `--summary-en`을 추가할 수 있습니다. 공개 표시 문구에는 이메일 주소·URL·개인 컴퓨터의 경로를 넣지 않습니다.

같은 ID의 자료를 수정할 때만 `--replace`를 추가합니다. 이미 등록된 PDF가 교체되므로 수정할 파일을 확인한 뒤 사용합니다. 등록되지 않은 동명 파일은 `--replace`로도 덮어쓰지 않습니다. 원본 입력 PDF는 그대로 유지됩니다.

등록 후 리뷰 허브를 다시 생성합니다:

```sh
python3 scripts/publish_public_site.py --hub-only
```

파일을 브라우저에 올리는 업로드 기능은 없습니다. PDF 제공 → 내용 확인 → 이 명령으로 등록 → 허브 생성 → 사이트 게시 순서로 진행합니다. 게시 전에는 생성된 허브에서 제목·분류·PDF 링크를 확인합니다.

`manifest.json` 형식:

```json
{
  "version": 1,
  "documents": [
    {
      "id": "2026-10-16-daily-quantum-review",
      "date": "2026-10-16",
      "series": "daily-quantum",
      "title": "Daily Quantum Review · 2026년 10월 16일",
      "summary": "이번 호에서 다루는 양자컴퓨팅 연구를 요약합니다.",
      "language": "ko",
      "file": "files/2026-10-16-daily-quantum-review.pdf",
      "tags": ["Quantum"],
      "source_title": "Daily Quantum Review",
      "public_reviewed": true
    }
  ]
}
```

선택 필드는 `title_en`, `summary_en`, `source_title`뿐입니다. 제목·출처명은 최대 240자, 요약은 최대 1,600자, 태그는 각각 최대 48자로 12개까지 등록합니다. 개인 메일이나 원본 저장 경로 같은 인계용 정보는 이 공개 등록부에 추가하지 않습니다. 등록부가 없거나 비어 있으면 첫 등록 시 생성됩니다.
