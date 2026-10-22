# 짧은 주제 약어로 확장한 리뷰 아이콘

- 날짜: 2026-10-22
- 범위: 기존 월넛·수채화 페이지형 R 아이콘 개편. 기사 표지·본문·PDF 개편은 해당하지 않는다.
- 요청: Q·AI를 주제를 나타내는 글자로 읽히게 하고, 실제 페이지에서 다루는 짧은 약어를 더 자유롭게 배치한다. 긴 키워드는 쓰지 않는다.
- 보존: 접힌 저널 페이지의 R, 월넛 브라운·베이지·차분한 청록, 오른쪽 아래 안료 번짐, 약한 표면빛.
- 선택 토큰: Q / AI / DFT / VQE / LLM / OLED / GPU. 모두 1–4글자이며 각 한 번 사용한다.
- 약어 의미: Q는 Quantum의 브랜드 축약, AI는 artificial intelligence, DFT는 density functional theory, VQE는 variational quantum eigensolver, LLM은 large language model, OLED는 organic light-emitting diode, GPU는 graphics processing unit.
- 해석: 분야·방법·장치에 관한 편집 주제를 나타낸다. 크기·위치·색은 실제 성능·인과·연구량·증거 수준을 나타내지 않는다.

## 세 발상 비교

| 안 | 배치 | 판단 |
|---|---|---|
| A · 자유로운 여백 주석 | R의 위·아래 여백과 페이지 가장자리에 약어를 크기·각도가 다르게 배치 | 기존 실루엣을 가장 잘 보존하면서 요청한 자유로움을 더함. 실제 생성 비교 |
| B · 페이지를 따라 흐르는 주제 | R의 여백과 종이면을 함께 쓰고 회전·명암으로 주제를 통합 | 더 유연하고 통합된 구성이 가능하지만 작은 글씨와 R 윤곽의 경쟁 주의. 실제 생성 비교 |
| C · R 바깥의 주제 고리 | 작은 약어가 외부 공간을 둘러싸는 구성 | 작은 아이콘에서 외곽이 산만해지고 iOS 크롭 위험. 기획에서 제외 |

## 근거와 검수 계획

- 현재 공개 리뷰·렉처의 HTML 가시 텍스트, 허브 메타데이터와 공개 글의 주제를 대조한다. 원문 수집·개인 자료는 입력하지 않는다.
- 공개 한국어 리뷰·렉처 46개를 별도 에이전트가 확인: DFT 26, OLED 33, GPU 21, VQE·LLM 각 18개 페이지에서 약어 확인. 주제별 기사 수를 엄밀히 분류한 값은 아니다.
- 키워드 근거는 keyword-audit.json에 기록한다. ML은 AI와 의미가 겹쳐 제외한다.
- 제작: built-in image_gen으로 기존 원본을 편집하고, 실제 생성 결과의 글자 철자·중복·배치·재질을 검토한다. 원본을 코드로 다시 그리거나 임의로 글자를 덧붙이지 않는다.
- 180/64/32/16px, 흑백, 이전 아이콘과 비교한다. 축소본에서는 R 실루엣을 우선하며 모든 약어 판독을 보장하지 않는다.
- 최종 프롬프트·원본 해시·선택 근거·판독 한계·생산 검증 기록을 남긴다. 공개 사이트에는 승인한 최종 아이콘만 복사한다.

## 상태

발행 가능: 실제 시안·축소·문자 검토 및 전체 사이트 생산 검증을 통과했다. 자산 버전은 `20261022-topic-keywords`다. 검수 기록은 `production-validation.json`, 내보내기 해시는 `release-manifest.json`에 남긴다.

두 실제 편집안 제작 완료. 별도 디자인 검토자는 A를 선택했다. 일곱 약어의 철자·개수, 기존 팔레트·R 형태, 배치의 자유로움을 실제 이미지에서 확인했다. 원본은 `selected-A-keywords.png`이며 `candidate-A.png`와 바이트가 같다. 축소 검토 및 생산 통합 기록은 별도 파일에 남긴다.

별도 판독 검토자도 A를 추천했다. 실제 180px에서 일곱 약어를 구별할 수 있으나 VQE·LLM·OLED는 시선이 머물러야 하며, 64px부터 완독을 보장하지 않는다. 32/16px에서는 R의 실루엣을 확인했다. 180px 흑백에서도 문자와 바탕의 명암 차이를 확인했다. 실제 iOS 설치와 사람 대상 선호도·접근성 시험은 수행하지 않았다.

## 캡션과 대체 텍스트

- 한국어: 접힌 저널 페이지의 R과 Q·AI·DFT·VQE·LLM·OLED·GPU를 자유롭게 배치한 AI Tech Review Letters 아이콘. 약어는 리뷰·렉처가 다루는 주제이며 실제 장치·데이터의 도식이 아니다. AI 생성 편집 이미지.
- English: AI Tech Review Letters icon with a journal-page R and freely arranged Q, AI, DFT, VQE, LLM, OLED and GPU subject abbreviations. An AI-edited publication symbol, not a diagram of an actual device or dataset.
- 공개 범위: 최종 PNG·ICO와 PNG를 내장한 SVG만 사이트에 복사한다. 프롬프트·시안·QA 보드·검토 기록은 게시 사이트의 배포 파일에 포함하지 않는다.
