# ATRL: Agentic Atelier for Tech Review Letters

에이전틱 시대의 지식 흐름과 연구 공방의 탄생

표기 발행일·근거 기준일: 2026-11-09. 개정 23 공개판 게재·검증: 2026-11-10.

논문을 읽으며 얻은 질문이 조사·계산·집필·감수와 운영의 왕복을 거쳐 설명으로 자라는 과정을 ATRL 공방의 사례로 살핀다. 사람의 기획, AEDAUT의 편집·저술, ADOPT의 개발운영이 하나의 워크플로를 이루며, 그 협업 아키텍처 자체도 연구와 창작의 대상이 되는 변화를 논의한다. 기획·권한·자료·판본의 관계, 작은 교육용 비교, 고정된 55편의 게재·개정 기록과 외부 연구 시스템을 함께 읽는다.

- [한국어 웹](https://infant83.io/AI_Tech_Review/reviews/2026-11-09_atrl-agentic-atelier/) · [English](https://infant83.io/AI_Tech_Review/reviews/2026-11-09_atrl-agentic-atelier/en/)
- [한국어 원고](reports/review_ko.md) · [English manuscript](reports/review_en.md)
- [한국어 PDF](dist/review_ko.pdf) · [English PDF](dist/en/review_en.pdf)
- [출판 원본](dist/index.html) · [공개 파일 명세](artifacts/publication-output-manifest.json) · [게재·공개 검증](artifacts/publication-verification.json)

그림 9는 제본된 출판물과 같은 책등에 연결된 모형·방법·감수 기록을 펼치고, 다음 질문을 오른쪽 노트로 잇는다. 일부 장면과 대표 이미지는 AI 생성·편집 개념 그림이며, 수식·자료·문구는 정확한 벡터로 구성했다. 교육용 감쇠 모형은 가상의 신호를 다루고, 55편의 관찰은 공개 메타데이터 고정판에 근거한다. 이를 실제 실험이나 하네스의 품질·생산성 인과 효과로 확대하지 않는다.

## 출판 원본 재생성

최종 원고는 `reports/`, 자립형 그림 36종은 `figs/`에 있다. `artifacts/`에는 현재 웹·PDF 조립 코드, 글꼴 부분집합과 라이선스, 최종 표지 및 공개 표 자료를 선별해 보존한다. 이미지의 이전 후보·중간 제작기와 내부 검수 캡처는 배포하지 않는다. Node.js 환경에 marked, mathjax-full, Playwright와 Chrome이 필요하며, Python 출력기는 지정한 Node.js 런타임을 사용한다.

```sh
REVIEW_NODE_MODULES=/path/to/node_modules node 2026-11-09_atrl-agentic-atelier/artifacts/build_review.mjs --public-base=https://infant83.io/AI_Tech_Review/reviews/2026-11-09_atrl-agentic-atelier/
python3 2026-11-09_atrl-agentic-atelier/artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules
```

리뷰 등록은 `publication/reviews/2026-11-09_atrl-agentic-atelier.json`, 지속 출판 요청은 `publication/requests/`를 사용한다. 게재 절차는 저장소의 [게시 작업 안내](../PUBLICATION_WORKFLOW.md)를 따른다. 검토된 원고 개정 23과 기본 하네스 2026.08·2026-11-06 보완판은 서로 다른 판본이다. 편집자가 기획·개정 방향과 게시를 지시했으며, 문장 단위 사람 재독이나 독자 이해도 조사를 수행했다고 표시하지 않는다.
