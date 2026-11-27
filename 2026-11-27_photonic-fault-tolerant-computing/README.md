# 큐비트에서 광자 내결함성 계산까지

2026-11-27 · 편집부(AEDAUT)의 수신 자습 강의 아카이빙. 운영팀(ADOPT)의 기존 PDF 아카이브·필기 리더·출판 절차를 사용한다. 한국어 통합본과 Level 1–7 분리본은 서로 다른 문서로 보존한다.

상대 위상과 측정에서 출발해 잡음과 오류정정, 논리연산·매직 상태, 컬러 코드, 측정기반 계산과 광자 융합으로 이어지는 독립 자습용 저술이다. 실제 강연이나 질의응답의 채록으로 표시하지 않는다. 영문 입구는 한국어 PDF의 소개다.

## 문서와 공개 주소

- 시리즈: `photonic-fault-tolerant-computing`
- 국문 안내: `lectures/photonic-fault-tolerant-computing/`
- 영문 안내: `lectures/photonic-fault-tolerant-computing/en/`
- 통합본 ID: `2026-11-27-photonic-fault-tolerant-computing-notes-ko`
- 단계별 ID: `2026-11-27-photonic-fault-tolerant-computing-l001-notes-ko`부터 `2026-11-27-photonic-fault-tolerant-computing-l007-notes-ko`까지

각 PDF의 정식 보존 주소는 `archive/files/<문서 ID>.pdf`, 필기 주소는 `lectures/reader/?id=<문서 ID>`다. 문서 ID와 공개 PDF 판본은 이후 갱신에서도 기존 출판 절차에 따라 보존한다.

## 출판 원본

`build_course.py`에는 과학 감수에서 대조한 한영 제목·소개·학습 순서와 작성·검수 공개, 원전 목록을 보존한다. 완성된 공개 PDF 검수 기록의 실제 쪽수·SHA-256과 파일 바이트를 대조한 뒤 아래 네 안내 자산만 만든다. PDF를 수정하거나 아카이브에 등록하는 기능은 없다.

```sh
python3 2026-11-27_photonic-fault-tolerant-computing/build_course.py
```

기본 입력은 같은 주제 폴더의 `reports/pdf-qa.json`과 저장소의 정식 보존 파일 `archive/files/`다. 필요할 때 `--qa`와 `--pdf-dir`로 이미 검수한 공개판 입력을 지정한다. 완성된 과학 공개문과 원전, 통합본을 포함한 8개 공개 PDF의 기록·해시가 없으면 안내 자산을 만들지 않는다.

| 안내 자산 | 용도 |
| --- | --- |
| `dist/index.html` | 국문 학습 순서·통합본·7단계 요약과 자료 링크 |
| `dist/en/index.html` | 같은 자료의 영문 소개 |
| `dist/notes.css` | 모바일·키보드·밝은 화면과 어두운 화면을 위한 스타일 |
| `dist/unit-registry.json` | 시리즈 소개와 각 공개 PDF의 ID·쪽수·해시 연결 |

공개 bundle에는 위 네 파일, 검수한 L001–L007 PDF 사본 7개와 `notes.pdf`만 명시적으로 포함한다. `notes.pdf`는 최신 단원 L007의 정확한 사본이다. 통합본은 그 사본을 대체하지 않으며 정식 아카이브 파일을 직접 연결한다. 원자료·수집 기록·검수 화면은 bundle에 포함하지 않는다.

## 통합본과 단원 등록부

등록부는 `ai-tech-review-course-registry` 버전 1을 사용한다. `compilation_archive_id`는 통합본 대표 ID와 같아야 하고 `compilation_public_pages`에는 실제 공개판 쪽수를 적는다. `units`에는 L001–L007만 순서대로 넣고 `latest_unit`은 L007로 지정한다. 각 단원의 `pdf`는 `<archive_id>.pdf`, `sha256`과 `public_pages`는 공개 PDF 검수 결과와 같아야 한다.

통합본을 단원 목록에 넣지 않는다. 렉처 목록은 1개 시리즈와 7개 단원을 보여 주며, 전체 아카이브는 통합본까지 8개 PDF를 보존한다. 접힌 카드에는 전체 과정의 소개가 남고, 펼치면 통합본과 각 단원의 작은 필기·PDF·다운로드 링크가 나타난다.

## 감수와 발행

원문에서 수행한 검산과 이번 아카이빙에서 실제 재실행한 계산을 구분한다. 공개 PDF의 보존·링크·개인정보·조판 검수와 과학 감수의 최종 결과는 해당 보고에 기록한다. 안내의 작성·검수 공개도 그 완료된 범위에 맞춘다. 실행하지 않은 SDK·QPU·광학 실험을 실행했다고 표시하지 않는다.

`archive/entries`의 문서별 등록과 기존 `PUBLICATION_WORKFLOW.md`를 따라 별도 후보를 만든다. 실제 이전 배포와의 연속성·페이로드 검증, 완료된 배포와 실제 HTTPS 한영 안내·PDF 해시·8개 필기 링크를 확인한 뒤 발행 성공을 기록한다. 다른 출판 작업의 원본과 배포 변경을 보존한다.
