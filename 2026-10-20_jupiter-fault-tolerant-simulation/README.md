# JUPITER 매직상태 배양 모사 리뷰

- 근거 기준일: 2026-10-20
- 한국어 정본: `reports/review_ko.md`
- 전체 영어판: `reports/review_en.md`
- 공개 출력: `dist/` 및 `dist/en/`
- 원본 설명 도표·수식·제작 코드: `artifacts/`
- 그림별 출처와 해석 범위: `figure-manifest.json`

NVIDIA/Jülich의 고전 GPU 모사와 실제 QPU 실험을 구분한다. 104개의 물리 위치, 45비트 부호화 레지스터, 512 TiB의 상태벡터 메모리를 각각 설명하며, 원 배양 연구·추가 flag 연구·실제 Willow 실험의 숫자는 서로 다른 조건으로 귀속한다. 논문과 공개 기술 설명의 대조 및 교육용 계산을 수행했으며 JUPITER 계산은 재실행하지 않았다.

표지는 내장 imagegen으로 생성한 개념 일러스트다. 정확한 수식·메모리 값·과정도는 결정론적으로 제작했다. 사적인 메일 원문·헤더·첨부 취득 정보와 원문 수집 파일은 이 폴더에 포함하지 않는다.

## 재생성

`artifacts/build_figures.py`는 matplotlib·numpy·fonttools·brotli와 Nanum Gothic 글꼴을 사용한다. `build_fonts.py`에는 `--regular`·`--bold`로 정규·굵은 글꼴을 지정한다. 글꼴의 공개 라이선스는 `artifacts/font-license.txt`에 포함한다.

`artifacts/build_review.mjs`는 marked·mathjax-full을 사용하며, 의존성 위치는 `REVIEW_NODE_MODULES` 또는 `CODEX_PRIMARY_RUNTIME_NODE_MODULES`로 지정한다. `artifacts/build_pdf.py`는 Playwright와 Chrome을 사용하고 런타임은 `--node`·`--modules`로 지정할 수 있다. 개인 환경 경로를 공개 출력에 넣지 않는다.

`python artifacts/validate_calculations.py`로 메모리·qutrit 부호화·위상 오차 예시를 검산한다. 위상 예시는 닫힌 수식 외에 두 진폭의 반복 진화와 확률 재귀로도 대조한다. 생성 PDF는 모든 페이지를 렌더링해 확인하며 반응형 그림은 별도 모바일 도표를 사용한다.
