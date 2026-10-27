# 2026-10-23–25 Daily Quantum Brief 공개 보관본 준비

기존 공개 목록에서 빠져 있던 DQB 세 호를 2026-10-27에 검토했다. 최종 한국어 공개 보관본은 `dist/`에, 한영 목록용 문구와 등록 제안은 `reports/archive-entries.json`에 있다. 등록·사이트 생성·공개 배포는 이 준비 작업과 별도 단계다.

- 10월 23일: 「좋은 목적함수보다 공정한 비교가 먼저다」, 5쪽.
- 10월 24일: 「양자 재료 계산은 어디서 시작해야 하는가」, 5쪽.
- 10월 25일: 「국소화에서 탈출하는 최적화, 오류를 편향시키는 하드웨어」, 4쪽.

세 호 모두 첫 쪽의 개인 자료 수집 경위 문단을 실제 PDF redaction으로 제거하고 짧은 공개 보관본 편집 기록을 넣었다. 원본의 과학 본문·표·쪽수와 원문 링크 총 18개를 유지한다. 원본과 QA 이미지는 공개 배포 대상이 아니다.

10월 24일 [7]의 임의 요약 제목을 원제 **On the Role of Problem Structure in Single-Layer QAOA**로 바로잡고 세 저자의 크레딧을 모두 적었다. 원문 제출일은 2026-10-21이며 해당 본문 출처 행도 정정했다. 근거는 [arXiv:2610.30511v1](https://arxiv.org/abs/2610.30511v1)의 원제·저자·submission history다. 다른 원본 참고문헌의 짧은 서지는 보존했으며, 전체 참고문헌의 APS 재편집을 수행한 것으로 표시하지 않는다.

`notes/production-qa.json`에는 입력·출력 SHA-256, 정확한 변경 좌표, 쪽별 변경 영역 밖의 144 dpi 픽셀 동일성, 원문 URI·메타데이터·첨부·실행 동작 검사와 실제 출력 검수 범위를 남겼다. 전체 14쪽을 Poppler로 렌더링한 접촉시트에서 보고 변경 구간을 확대 확인했다. 깨진 null·대체 글리프, 개인 주소·비공개 경로·인증 쿼리, 내장 첨부·실행 동작은 발견하지 못했다.

원문 식별과 일부 대표 수치는 arXiv 초록·APS 저널 초록·출판사 기탁 Crossref 서지와 대조했다. 이 작업은 원 논문의 실험·과학 계산 재현이나 사람의 문장별 감수를 뜻하지 않는다. 책임 편집 김현중, AI 보조 OpenAI Codex, 실제 준비·검수 역할 `dqb_backlog_archive`. 정확한 실행 모델 식별자는 기록하지 않았다.

## 재생성

`artifacts/build_public_archive.py`는 검토한 SHA-256의 입력만 받으며 공개 등록·게시를 수행하지 않는다. PyMuPDF, Pillow, 한국어 TrueType 글꼴이 필요하다.

```sh
python artifacts/build_public_archive.py \
  --source-dir PRIVATE_ISSUE_DIRECTORY \
  --font-regular NanumGothic-Regular.ttf \
  --qa-dir PRIVATE_QA_DIRECTORY
```

재생성 시 출력 시각 검수는 `pending`으로 돌아간다. 최신 출력의 전체 페이지와 변경 구간을 다시 확인한 뒤 상태를 갱신한다.
