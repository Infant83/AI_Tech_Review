# 2026-10-26 Daily Quantum Brief 공개 보관본

- `dist/2026-10-26-daily-quantum-brief.pdf`: 원 DQB 4쪽에 명시적 편집·정정 기록 1쪽을 덧붙인 한국어 공개판.
- `reports/archive-entry.json`: 한영 목록에서 같은 한국어 PDF를 안내하는 아카이브 등록 제안.
- `artifacts/build_public_archive.py`: 검토한 원본만 받아 공개 정정판을 만드는 코드. 등록·게시를 수행하지 않는다.
- `notes/production-qa.json`: 공개 가능한 제작 검사·변경 좌표·해시·실제 출력 검사 기록.

1쪽의 수집 경위 문단을 실제 redaction으로 제거했다. 원문과 대조한 화학식·지수 16구간의 깨진 글리프 21개를 호환 가능한 표기로 복원하고 참고문헌 [3]의 잘못된 저자·제목을 정정했다. 직접 링크 5개와 원래 표·쪽번호를 유지했다. 모든 수정 좌표 밖은 144 dpi 픽셀이 원본과 같다. 원 논문의 과학 계산을 독립 재현한 자료는 아니다.

전체 5쪽을 Poppler로 렌더링해 확인했다. 원본·수집 자료와 QA 이미지는 공개 배포하지 않으며 `tmp/`·`research/`는 제외한다. 이 폴더를 사이트 배포 대상으로 복사하지 않고 등록한 최종 PDF만 게시한다.

## 재생성

PyMuPDF, ReportLab, Pillow 및 Poppler의 `pdftoppm`이 필요하다. 원본과 글꼴은 호출자가 전달한다. 정정 구간에는 Noto Sans KR Regular, 정정 기록에는 Nanum Gothic Regular/Bold와 필요한 라틴 글리프의 fallback을 사용했다.

```sh
python artifacts/build_public_archive.py \
  --source-pdf SOURCE.pdf \
  --repair-font NotoSansKR-Regular.otf \
  --font-regular NanumGothic-Regular.ttf \
  --font-bold NanumGothic-Bold.ttf \
  --font-fallback FALLBACK.ttf
```

재생성하면 시각 검수 상태는 `pending`으로 돌아간다. 최신 5쪽을 확인한 뒤 기록을 갱신한다. 책임 편집자와 실제 에이전트 역할은 PDF의 정정 기록에 공개했다.
