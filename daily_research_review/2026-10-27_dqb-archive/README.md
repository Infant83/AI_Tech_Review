# Daily Quantum Brief · 2026-10-27 공개 보관본

원 DQB 5쪽을 보존하며 공개 범위와 서지를 보완한 6쪽 한국어 보관본이다. 한영 목록은 같은 한국어 PDF를 안내한다. 신규 심층 리뷰 발행과 별개의 아카이브 등록이다.

- 1쪽의 메일·검색 수집 경위 문단을 실제 삭제했다.
- 5쪽의 불완전한 참고문헌 목록을 6쪽의 APS 번호 목록으로 옮겼다. 원저자·원제와 확인한 arXiv v1을 기록하고, PRX 논문 [4]의 직접 링크를 정식 DOI `10.1103/6ps1-mw9l`로 바로잡았다.
- 논리 메모리의 기저별 조건과 상태 tomography의 범위, 생성모형 MMD²의 고전 propagator 평가 경로를 원문 대조한 보충 설명으로 남겼다. 원 과학 본문·표·수치와 기존 쪽번호를 조용히 바꾸지 않았다.
- 원래 5쪽은 선언한 삭제·서지 영역 밖의 144 dpi 픽셀이 같다. 공개 PDF의 본문·메타데이터·원문 링크·첨부·실행 동작을 검사한다. 실제 시각 검수 결과는 `notes/production-qa.json`에 남긴다.

출판 원본은 `dist/2026-10-27-daily-quantum-brief.pdf`, 재생성 코드는 `artifacts/build_public_archive.py`, 등록 정보는 `reports/archive-entry.json`이다. 개인 원본·메일 식별정보·수집 파일·QA 이미지는 Git과 공개 사이트에 포함하지 않는다. 재생성 시 원본과 한국어 글꼴 및 비공개 QA 출력 폴더를 호출자가 전달하며, 시각 검수 상태는 `pending`으로 돌아간다. PyMuPDF 1.26.7, Pillow, ReportLab을 사용한다.

원문 대조는 [Harper 등 v1](https://arxiv.org/html/2610.32347v1), [Monaco 등 v1](https://arxiv.org/html/2610.32571v1), [Compendium v1](https://arxiv.org/html/2610.32595v1), [PRX 정식 출판 정보](https://journals.aps.org/prx/abstract/10.1103/6ps1-mw9l), [LYNX v1](https://arxiv.org/html/2610.32518v1)을 사용했다. 논문의 QPU·대규모 학습과 원 결과 전체를 독립 재현한 것은 아니다. 후속 VQE 리뷰는 별도 기획·승인 대상으로 관리한다.
