# AI for Science 리뷰 전략

2026년 5월의 AI for Science 논의는 연구자가 논문을 더 빨리 읽도록 돕는 수준을 넘어섰습니다. Google의 Co-Scientist는 가설을 만들고 서로 비판하게 하는 멀티 에이전트 구조를 Nature 논문으로 공개했고, FutureHouse의 Robin은 실험 생물학의 약물 후보 탐색까지 연결했습니다. 같은 시기 Google ERA는 과학자가 쓰는 경험적 소프트웨어를 AI가 작성하도록 돕는 연구를 Nature에 냈고, AlphaEvolve는 자동 평가가 가능한 알고리즘 설계 영역에서 이미 성과를 보였다고 발표했습니다.

메일 `ai for sci`에 들어 있던 LinkedIn 공유는 이 변화가 `AI 과학자`라는 말로 과장되기 쉬운 지점을 짚어보자는 신호로 읽힙니다. 실제 리뷰에서는 인간 과학자가 사라지는 이야기보다, AI가 연구자의 협업 구조 안에서 어떤 권한을 갖고 어떤 검증을 받아야 하는지를 다루는 편이 좋겠습니다.

## 확인한 메일

- Gmail에서 `subject:"ai for sci"`로 검색해 1건을 확인했습니다.
- 메일은 2026년 5월 22일 16:52:49 KST에 발송된 자기 전달/공유 메일이며, 본문에는 Sergei Kalinin의 LinkedIn 게시글 링크가 들어 있었습니다.
- LinkedIn 미리보기에는 `The end of the beginning for AI for Science`라는 글이 확인되었습니다. 게시글은 2026년 5월 Nature에 나온 Google/FutureHouse 계열 AI 과학 에이전트 논문들을 변곡점으로 보고, 다음 단계는 문헌·코드·시뮬레이션을 실제 실험 세계와 연결하는 일이라고 해석하는 취지였습니다.
- LinkedIn 원문은 접근 제약이 있으므로 최종 근거로 쓰지 않고, 주제 발굴 신호로만 둡니다.

## 1차 리서치 결과

### Google-대한민국 파트너십

[Google Korea 발표](https://blog.google/intl/ko-kr/company-news/inside-google/announcing-our-partnership-with-the-republic-of-korea/)는 2026년 4월 27일 Google DeepMind와 과학기술정보통신부의 국가 AI 파트너십을 공개했습니다. 이 발표에서 한국의 AI Campus, K-문샷 미션, 서울대·KAIST·AI 바이오 혁신 연구거점 협력, AlphaEvolve, AlphaGenome, AlphaFold, AI Co-Scientist, WeatherNext 활용 계획이 함께 언급됩니다.

같은 날 [청와대 브리핑](https://www.president.go.kr/briefings/wdDpcXDE)은 데미스 하사비스 대표와 대통령 면담에서 K-문샷 중심 협력, AI Campus의 서울 개소, AI 안전 가드레일, 글로벌 AI 허브 구상이 논의되었다고 설명했습니다. 이 부분은 리뷰에서 국가 정책과 글로벌 모델 제공자의 이해관계가 만나는 장면으로 다룰 수 있습니다.

### Co-Scientist와 Gemini for Science

[Google Korea의 2026년 5월 19일 Co-Scientist 발표](https://blog.google/intl/ko-kr/company-news/technology/coscientist-io-2026-kr/)는 Co-Scientist를 Gemini 기반 멀티 에이전트 시스템으로 설명합니다. 생성, 탐색, 리플렉션, 순위 평가, 이볼루션, 메타리뷰, 관리자 에이전트가 함께 가설을 만들고 비판하고 발전시키는 구조입니다. 발표는 항생제 내성, 식물 면역, 간 섬유화, ALS, 노화 연구 등 협력 사례와 함께 CBRN 오용 가능성 평가와 안전 분류기 개발도 언급합니다.

[Nature의 Co-Scientist 논문](https://www.nature.com/articles/s41586-026-10644-y)은 2026년 5월 19일 공개되었습니다. 논문 초록은 Co-Scientist가 연구 목표와 선행 근거를 바탕으로 검증 가능한 가설을 만들고, 테스트 타임 컴퓨트 확장을 통해 가설 품질을 개선하며, 급성 골수성 백혈병 약물 재창출 후보와 조합 치료 후보를 in vitro 실험으로 검증했다고 설명합니다.

### AlphaEvolve와 자동 평가 가능한 발견

[AlphaEvolve 발표](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)는 LLM의 창의적 제안과 자동 평가자를 결합한 진화형 코딩 에이전트를 소개합니다. Google은 이 시스템이 데이터센터, 칩 설계, AI 훈련, 행렬곱 알고리즘, 수학 문제 등에서 효율 개선이나 새로운 해법 탐색에 쓰였다고 설명합니다. 리뷰에서는 AlphaEvolve를 `검증 가능한 평가 함수가 있는 과학/공학 문제`의 대표 사례로 놓는 편이 좋습니다.

### Nature의 세 논문 클러스터

2026년 5월 19일 Nature에는 세 방향의 AI for Science 사례가 거의 동시에 등장했습니다.

- [Co-Scientist](https://www.nature.com/articles/s41586-026-10644-y): Google 계열의 가설 생성·비판·순위화 멀티 에이전트 시스템
- [Robin](https://www.nature.com/articles/s41586-026-10652-y): FutureHouse의 다중 에이전트 과학 자동화 시스템으로, 건성 노인성 황반변성 약물 후보 탐색과 후속 실험 설계에 연결
- [ERA](https://www.nature.com/articles/s41586-026-10658-6): 과학자가 쓰는 경험적 소프트웨어를 전문가 수준으로 작성하도록 돕는 AI 시스템

[Nature Portfolio 보도자료](https://www.natureasia.com/en/info/press-releases/detail/9330)는 Co-Scientist와 Robin을 가설 생성, 실험 설계, 데이터 분석을 돕는 협업 시스템으로 설명합니다. 이 지점은 리뷰의 균형추가 됩니다.

## 발굴된 리뷰 후보

### 후보 1: AI 과학자는 연구자를 대체하는가, 연구실의 협업 구조를 바꾸는가

가장 추천하는 방향입니다. Google Co-Scientist, FutureHouse Robin, ERA, AlphaEvolve, 한국 K-문샷을 한 흐름으로 묶되, 중심 메시지는 `책임 있는 협업 구조`에 둡니다. 독자가 얻어갈 질문은 명확합니다. AI가 가설을 낼 수 있을 때, 연구자는 무엇을 더 잘해야 하는가.

### 후보 2: K-문샷과 Google DeepMind 파트너십

한국 정책 중심 리뷰입니다. 국가 AI 컴퓨팅, 연구데이터, AI Campus, 서울대·KAIST·AI 바이오 거점, AI 안전연구소 협력, 출연연·기업 참여 구조를 중심으로 볼 수 있습니다. 다만 기술적 흥미를 살리려면 Co-Scientist와 AlphaEvolve를 충분히 설명해야 합니다.

### 후보 3: AI for Science의 네 가지 에이전트 유형

도구 비교형 리뷰입니다. Co-Scientist는 가설 에이전트, Robin은 실험 워크플로 에이전트, ERA는 연구 코드 에이전트, AlphaEvolve는 알고리즘 발견 에이전트로 놓고 비교합니다. 엔지니어 독자에게 실용적이지만, 국가 협력 맥락은 별도 섹션으로 압축해야 합니다.

### 후보 4: 우려에서 출발하는 AI for Science 리뷰

Nature의 비판 논문과 사설을 중심으로, AI가 과학 훈련, 문헌 품질, 불확실성 표현, 안전, 데이터 주권에 어떤 문제를 만들 수 있는지 다룹니다. 중요한 주제이지만, 단독으로 가면 이번 Google-한국 협력과 AlphaEvolve의 기술적 진전이 배경으로 밀릴 수 있습니다.

## 추천 리뷰 전략

이번 리뷰는 후보 1을 중심축으로 삼는 편이 좋겠습니다.

추천 제목은 다음과 같습니다.

> **AI 과학자는 어디까지 동료가 될 수 있을까: Co-Scientist, AlphaEvolve, K-문샷이 바꾸는 연구 협업 구조**

본문의 질문은 이렇게 잡을 수 있습니다.

> 과학 AI의 다음 단계에서는 더 똑똑한 답변 생성만큼이나 연구자의 질문, 문헌, 코드, 실험, 국가 인프라가 연결되는 협업 체계를 어떻게 설계할 것인가가 중요해집니다.

이 제목은 Google 발표, Nature 논문, 한국 정책을 모두 담을 수 있고, 사용자가 요청한 우려 섹션도 자연스럽게 들어갑니다.

## 본문 구성안

1. **AI for Science의 새 장면**  
   2026년 5월 Nature 논문 클러스터와 Google I/O 2026 Co-Scientist/Gemini for Science 발표를 배경으로, AI가 연구 과정의 어느 지점까지 들어왔는지 설명합니다.

2. **가설을 만드는 에이전트**  
   Co-Scientist와 Robin을 비교합니다. 문헌 검색, 가설 생성, 아이디어 토너먼트, 실험 후보 선정, 인간 검토의 역할을 분리합니다.

3. **코드와 알고리즘을 고치는 에이전트**  
   AlphaEvolve와 ERA를 다룹니다. 자동 평가자가 있는 문제에서 AI가 어떻게 연구 생산물을 개선하는지 설명합니다.

4. **한국 K-문샷과 국가 협업 인프라**  
   Google DeepMind-과기정통부 파트너십, AI Campus, K-문샷, AI 과학자 프로젝트, 국가 AI 컴퓨팅 센터, 연구데이터/출연연/기업 협력을 연결합니다.

5. **실험실로 들어갈 때 달라지는 조건**  
   문헌과 코드에서는 실패 비용이 낮지만, 실제 실험에서는 비용, 안전, 재현성, 장비·시료·프로토콜 제약이 커집니다. 이 장에서 LinkedIn 신호의 핵심 문제의식을 회수합니다.

6. **우려 사항: 연구 속도와 과학의 품질은 따로 검증해야 한다**  
   이 섹션은 크게 잡아야 합니다. Nature 사설과 Messeri/Crockett의 비판을 바탕으로, 인간 검토, 연구 훈련, 문헌 오염, 불확실성 표현, 안전, 데이터/IP/주권, 벤더 종속을 다룹니다.

7. **도입 원칙과 체크리스트**  
   연구기관이나 기업 연구소가 AI for Science를 도입할 때 필요한 운영 원칙을 정리합니다. 예: AI 가설의 실험 전 검토 절차, 데이터 출처 기록, 안전 분류, 연구자 훈련 보존, 재현성 로그, IP/보안 검토.

## 우려 사항 섹션 초안

우려 섹션의 핵심 문장은 이렇게 잡을 수 있습니다.

> AI가 연구 속도를 높일수록, 과학자의 역할은 더 명시적으로 설계되어야 합니다. 어떤 가설을 실험할지, 어떤 데이터가 충분한지, 어떤 실패를 배워야 하는지 판단하는 능력은 자동화의 뒤편에 숨겨두면 안 됩니다.

다룰 항목은 다음과 같습니다.

- **Hallucination과 근거 품질**: AI가 그럴듯한 가설을 낼수록, 근거의 출처와 실험 가능성을 별도로 검증해야 합니다.
- **연구 훈련의 약화**: 실험실의 기초 작업과 실패 경험은 연구자의 판단을 만드는 훈련 과정이기도 합니다.
- **문헌 생태계 오염**: 생성형 AI가 논문·제안서 생산량을 높이면, 좋은 문장과 좋은 과학을 구분하기 어려워질 수 있습니다.
- **불확실성 표현의 손실**: 과학 문장은 단정 외에도 조건, 한계, 애매함을 표현해야 합니다. AI가 이를 평평하게 만들 위험이 있습니다.
- **CBRN과 이중용도 위험**: 생명과학에서 AI는 치료 후보 탐색과 위험한 지식 조합 모두에 쓰일 수 있습니다.
- **데이터 주권과 IP**: 국가 연구데이터, 기업 실험데이터, 모델 제공자 인프라가 만날 때 권리와 책임을 명확히 해야 합니다.
- **벤더 종속과 평가 독립성**: 특정 글로벌 모델 제공자가 연구 인프라의 중심이 될 때, 성능 검증과 데이터 거버넌스는 독립적으로 설계되어야 합니다.

## 슬라이드 전략

Skywork 슬라이드는 10~12장 구성이 적절합니다.

1. 제목: AI 과학자는 어디까지 동료가 될 수 있을까
2. 2026년 5월 AI for Science 타임라인
3. Co-Scientist 구조: 가설 생성-토론-진화
4. Robin과 실험 생물학 워크플로
5. AlphaEvolve와 ERA: 자동 평가 가능한 연구 산출물
6. 문헌/코드/시뮬레이션과 실험실의 차이
7. Google DeepMind-대한민국 파트너십
8. K-문샷과 국가 과학 AI 인프라
9. 우려 사항 매트릭스
10. 연구기관 도입 체크리스트
11. 기업/공공 R&D 적용 시나리오
12. 결론: AI가 빠르게 만드는 것과 사람이 책임져야 하는 것

## 다음 실행 제안

이 전략을 본 리뷰로 승격한다면, root topic package는 다음 이름이 좋습니다.

`2026-05-23_ai-for-science-national-collaboration`

그 안에서 `memo`, `deepresearch`, `final_review`, `Skywork prompt`를 작성하고, 최종 리뷰의 시각자료는 세 가지를 우선 만들면 좋겠습니다.

- `AI for Science 워크플로 맵`: 문헌, 가설, 코드, 실험, 데이터, 정책 인프라의 연결
- `인간-에이전트 책임 경계도`: AI가 제안하고 사람이 판단해야 하는 지점
- `우려/가드레일 매트릭스`: 위험 유형과 대응 장치

## 참고자료

- Google Korea, `구글 딥마인드와 과학기술정보통신부, 국가 AI 파트너십 발표`, 2026-04-27: <https://blog.google/intl/ko-kr/company-news/inside-google/announcing-our-partnership-with-the-republic-of-korea/>
- Google DeepMind, `AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms`, 2025-05-14: <https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/>
- Google Research, `Accelerating scientific breakthroughs with an AI co-scientist`, 2025-02-19: <https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/>
- Google Korea, `[I/O 2026] 연구를 가속화하는 멀티 에이전트 AI 파트너, '코사이언티스트(Co-Scientist)'`, 2026-05-19: <https://blog.google/intl/ko-kr/company-news/technology/coscientist-io-2026-kr/>
- Nature, `Accelerating scientific discovery with Co-Scientist`, 2026-05-19: <https://www.nature.com/articles/s41586-026-10644-y>
- Nature, `A multi-agent system for automating scientific discovery`, 2026-05-19: <https://www.nature.com/articles/s41586-026-10652-y>
- Nature, `An AI system to help scientists write expert-level empirical software`, 2026-05-19: <https://www.nature.com/articles/s41586-026-10658-6>
- Nature Editorial, `Why AI cannot do good science without humans`, 2026-05-19: <https://www.nature.com/articles/d41586-026-01551-3>
- Messeri & Crockett, `The uncritical adoption of AI in science is alarming - we urgently need guard rails`, 2026-05-19: <https://www.nature.com/articles/d41586-026-01557-x>
- 대한민국 청와대, `데미스 하사비스 구글 딥마인드 대표 접견 관련 김용범 정책실장 브리핑`, 2026-04-27: <https://www.president.go.kr/briefings/wdDpcXDE>
