# Daily Quantum Brief · 2026-11-09 공개 보관본

에이전틱 편집·저술팀(Agentic Editorial and Authoring Team, AEDAUT)이 원 DQB 4쪽에 정정·조건 보완 1쪽과 APS 참고문헌 1쪽을 더한 한국어 6쪽 자료를 준비했다. 현재 제호는 Agentic Tech Review Letters(ATRL)이며 원 Daily Quantum Brief 표시는 유지한다.

40-qubit spin gap은 17.6(1), exact 17.7 kcal/mol로 정정했다. 20.2(1), exact 19.3은 28-qubit 값이다. Q-DFT는 고전적으로 만든 H1–H6에서 장치 VQE를 시험했으며, 각10 s 노출과 H6의 별도100 s 시험을 구별한다. SCF 갱신·수렴은 무잡음 고전 모사다. KS 일전자 점유 부분공간과 8-qubit interacting 다전자 문제의 비교도 명료화했다.

QMC의 고전 비용비·공통 walker 비용·FCI teaching·실제 kernel, 열손실 이론의 균일 독립 채널·입력·Haar·깊이 조건, DiffSequence-Q의 매개변수·seed·모사·장치·활성검사 조건을 원문 대조했다. IBM의 운영 배치 보고와 QIML의 행사 날짜는 각각 해당 공식 기록의 범위로 읽는다. 참고문헌은 최초 인용순 [1]–[6]의 원제·전 저자·실제 v1 판본을 갖춘 APS 서지다.

수집·소셜 경위와 내부 메모를 실제 삭제하고 원문 URI 일곱 개를 보존했다. 최종 6쪽 전체 렌더, 엄격 PDF 파싱, 본문·메타데이터·URI·첨부·실행 동작·개인정보와 원4쪽의 선언 수정 영역 밖144dpi 픽셀 동일성을 확인했다. 기술 QA 화면·원본·감사 기록은 비공개로 보관한다.

root는 편집·PDF 제작·전체 페이지 확인과 게시 통합을 맡았다. dqb9_qmc는 45쪽 QC-QMC 원문·보충자료·공식 기록, dqb9_photonic은 Q-DFT18쪽과 DiffSequence-Q29쪽 전체·부록·주요 도표, dqb9_loss_industry는 83쪽 열손실 논문의 본문·정리와 필요한 부록 조건 및 IBM·QIML 공식 기록을 대조했다. 열손실 논문의 모든 증명을 인증하거나 원 연구의 실험·학습·QMC를 독립 재실행한 것은 아니다. QMC·광자 담당은 완성 보관본도 별도로 대조했다.

출판 원본은 `reports/reference-manifest.json`과 `reports/archive-entry.json`이다. `artifacts/build_public_archive.py`는 호출자가 제공한 비공개 원본과 글꼴로 최종 PDF를 다시 만들고, `--qa-dir`의 저장소 밖 경로에만 렌더·기술 검사 결과를 쓴다. 재생성하면 공개 검수 플래그를 초기화하므로 새 결과를 다시 확인해야 한다. 공개 등록과 실제 HTTPS 배포 완료는 별도로 확인한다.
