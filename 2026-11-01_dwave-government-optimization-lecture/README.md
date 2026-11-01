# D-Wave 정부 과제 최적화 웨비나 · 렉처 자료 공개 보관

2026-11-01 작성·편집된 한국어 v3 자료 두 편을 기존 렉처 노트 분류에 등록한다. 상세 노트는 13쪽이며 실제 문답 13건과 수학 보충 3개를 포함한다. 학술 검토는 8쪽이며 Stride의 모형 크기, MILP, QPU 시간, 초기해와 전역 최적성 인증을 검토한다. 공식 원영상은 [Quantum Optimization for Mission-Critical Government Challenges](https://www.youtube.com/watch?v=KYMj2DEKkr0)다.

등록부는 `archive/manifest.json`, 학습 시작점은 `lectures/`, 보관본은 `archive/files/`다. 한영 목록은 같은 한국어 PDF를 안내한다. 별도의 영어 번역본이나 HTML 강의 본문을 제작한 것으로 표시하지 않는다. 문서 작성일을 등록 날짜로 쓰며 파일명에 있던 행사 예정일과 구분한다.

## 공개판 편집과 보존

공개 PDF는 `output/pdf/`에 있다. 개인 원본은 Git과 사이트 배포에서 제외한 비공개 보관 영역에 보존한다. 공개판에서는 내부 운영·수집 기록과 일반 질문자 식별정보를 제거했다. 발표자·진행자 크레딧, 질문과 답변·상대시각, 과학적 한계, 원래 쪽번호와 모든 공식 출처 링크를 유지한다. 과학적 쟁점인 R004–R007과 주장·문답·출처 식별자의 대응도 유지한다. 원판의 참고문헌 식별 방식은 보존하며 새 APS 형식의 독립 논문 리뷰로 재작성한 자료가 아니다.

`artifacts/build_public_archive.py`는 검토한 원본 해시를 확인한 뒤 실제 redaction과 메타데이터 정리를 수행한다. 원판에서 직접 옮기지 않은 문구는 공개판 편집 안내와 과학 검토 범위의 간결한 재배치다. 출력 21쪽 모두를 Poppler로 렌더링했으며 원본과 변경 사각형 밖의 픽셀, 수식 이미지와 URI 목록이 일치하는지 확인한다. 본문·메타데이터·PDF 객체의 주소·경로·첨부·실행 동작도 검사한다. 원본·전사·QA 화면은 공개하지 않는다.

## 검토 범위

이 자료는 공식 녹화본 자막을 한국어로 재구성한 편집자 주석판이다. 녹화가 설명 도중부터 시작하며 직접 음성 청취·전체 화면 대조·벤치마크 재현을 수행하지 않았다는 원판의 한계를 유지한다. 기업 사례 수치는 이해관계자 보고이며 독립적인 고전 대비 우위·양자 기여 또는 전역 최적성 인증을 뜻하지 않는다. 현재 공식 Stride 속성과 하이브리드 시간 정의는 공개 등록 시 다시 확인했다. 원영상의 웹 검색 도구 조회는 제한되었으므로 이번 등록에서 영상 전체를 재검수했다고 표시하지 않는다.

책임 편집자는 김현중이다. OpenAI Codex의 `root`가 공개판 편집·등록·게시를, `archive_structure`가 게시 위치·기존 형식·공개 범위 대조를, `public_pdf_qa`가 별도의 PDF 출력·메타데이터 검수를 담당한다. 정확한 실행 모델 식별자와 원판의 원 작성 에이전트 식별자는 미보존이다. 사람의 문장별 전체 감수 또는 새 과학 실험은 수행하지 않았다. 세부 해시와 실제 검사 결과는 `notes/production-qa.json`에 기록한다.

## 재생성

PyMuPDF, Pillow, Nanum Gothic 글꼴이 필요하다. 원본 두 편과 글꼴은 호출자가 전달한다.

```sh
python3 artifacts/build_public_archive.py --source-dir SOURCE_DIRECTORY --font FONT_FILE
```

재생성하면 시각 검수 상태는 `pending`이 된다. 전체 PDF를 확인한 뒤 두 편을 `scripts/archive_documents.py`의 `lecture-notes`로 등록하고 `python3 scripts/publish_public_site.py --hub-only`로 한영 렉처 목록과 전체 아카이브를 갱신한다. 배포 완료와 실제 HTTPS 파일·해시 확인은 로컬 빌드와 구분한다.
