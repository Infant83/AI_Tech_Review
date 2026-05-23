# 심층 리서치 프롬프트: AI for Science와 국가 과학 협업 체계

## 목적

2026년 5월 기준 공개 자료를 바탕으로, Google DeepMind와 대한민국 과학기술정보통신부의 국가 AI 파트너십, Google Co-Scientist, AlphaEvolve, Gemini for Science, FutureHouse Robin, Google ERA, 한국 K-문샷 정책을 함께 분석한다. 리뷰의 목표는 `AI for Science`가 단순 연구 보조 도구에서 과학자의 협업 인프라와 국가 R&D 운영 체계로 이동하고 있는지 검토하는 데 그치지 않는다. 회사가 가진 실제 문제를 AI 과학자형 실행 루프로 바꾸기 위해 어떤 도구, 보안 경계, 평가 함수, 하네스 구조가 필요한지까지 제안한다.

## 독자

- AI/기술 전략을 검토하는 엔지니어, 연구기획 담당자, R&D 리더
- AI 도입을 고민하는 연구 조직, 기업 연구소, 공공 R&D 관계자
- 생명과학, 소재, 에너지, 기상·기후, 반도체 등 분야별 과학 AI 활용을 이해해야 하는 의사결정자
- 이미 AI를 적극적으로 활용하고 싶지만, 도구 선택, 보안, 데이터 준비, 검증 절차 때문에 실행이 느린 회사 내부 실무자

## 반드시 확인할 1차 출처

1. Google Korea, `구글 딥마인드와 과학기술정보통신부, 국가 AI 파트너십 발표`, 2026-04-27
2. Google DeepMind, `AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms`, 2025-05-14
3. Google Research, `Accelerating scientific breakthroughs with an AI co-scientist`, 2025-02-19
4. Google Korea/Google I/O 2026, Co-Scientist/Gemini for Science 발표, 2026-05-19
5. Nature, `Accelerating scientific discovery with Co-Scientist`, 2026-05-19
6. Nature, `A multi-agent system for automating scientific discovery`, FutureHouse Robin, 2026-05-19
7. Nature, `An AI system to help scientists write expert-level empirical software`, Google ERA, 2026-05-19
8. Nature Editorial, `Why AI cannot do good science without humans`, 2026-05-19
9. Nature Comment, `The uncritical adoption of AI in science is alarming - we urgently need guard rails`, 2026-05-19
10. 한국 K-문샷 추진전략, 국가인공지능전략위원회, 청와대/과기정통부 발표, IRIS 연구기획 공고
11. Cline 공식 문서: 로컬 모델, MCP, checkpoints
12. Qwen 공식 문서/블로그: Qwen3-Coder, Qwen Code, agentic coding
13. OpenAI 공식 문서/블로그: Codex, Codex agent loop, Skills/AGENTS 기반 작업 맥락
14. Google 공식 문서: Gemini CLI, Gemini Code Assist, headless mode
15. Anthropic 공식 문서: Claude Code CLI, MCP
16. Quanta Magazine, `The AI Revolution in Math Has Arrived`, 2026-04-13
17. 뉴스스페이스, GPT-5.4 Pro와 에르되시 문제 #1196 풀이 주장 관련 기사, 2026-04-16
18. Nature News Feature / 한겨레, Bixonimania 가짜 질병 사례, 2026-04-07 / 2026-04-11

## 연구 질문

1. 2026년 5월 Nature 클러스터는 `AI Scientist` 논의에서 어떤 변화를 만들었는가?
2. Co-Scientist, FutureHouse Robin, Google ERA, AlphaEvolve는 각각 과학 워크플로의 어느 단계에 개입하는가?
3. `문헌 검색/가설 생성`, `실험 설계`, `데이터 해석`, `코드와 알고리즘 생성`, `실험실 자동화` 사이에는 어떤 기술적 간극이 남아 있는가?
4. Google DeepMind-대한민국 파트너십은 K-문샷, AI Campus, AI 과학자 프로젝트, 국가 AI 컴퓨팅 인프라와 어떻게 연결되는가?
5. 한국의 AI for Science 전략은 미국 Genesis Mission, Google Gemini for Science, FutureHouse 같은 민간/비영리 AI Scientist 흐름과 비교해 어떤 강점과 취약점을 갖는가?
6. 실제 연구 현장 도입에서 우려해야 할 위험은 무엇인가? 최소한 다음 항목을 별도 섹션으로 다룬다.
   - Hallucination과 근거 없는 가설
   - 연구 훈련과 암묵지의 약화
   - 논문/제안서 생산량 증가와 품질 저하
   - 과학적 불확실성 표현의 단순화
   - 바이오보안, CBRN, 이중용도 연구
   - 연구데이터 주권, IP, 보안, 벤더 종속
   - 자동화된 실험이 실패했을 때의 비용과 책임
7. 기업 연구소나 공공 연구기관이 지금 준비해야 할 운영 원칙은 무엇인가?
8. 회사가 가진 문제를 `문제 카드 -> 데이터 패키지 -> 에이전트 워크벤치 -> 평가 함수 -> 인간 검토 -> 반복 검증` 구조로 바꾸려면 어떤 절차가 필요한가?
9. Cline+Qwen/Ollama/LM Studio 같은 온프레미스 환경과 Codex/Gemini/Claude 같은 서비스 환경은 보안 등급, 작업 유형, 검증 수준에 따라 어떻게 나눠 써야 하는가?
10. 이미 AI 활용 의지가 있는 조직에서 도입 마찰을 줄이기 위한 실제 사용 시나리오, 프롬프트, 하네스 폴더, 데이터 스키마, 결과 저장 구조는 무엇인가?
11. 최종 리뷰의 도입부는 수학에서 AI가 연구 도구로 받아들여지는 기대와 Bixonimania처럼 가짜 지식이 학술 인용망에 들어가는 위험을 어떻게 함께 보여줄 수 있는가?

## 비교 프레임

| 축 | 비교 대상 | 확인할 내용 |
|---|---|---|
| 가설 생성 | Co-Scientist, Robin | 문헌 기반 가설, 토론/순위화, 인간 검토 구조 |
| 실험 연결 | Robin, Co-Scientist 사례 | 실제 wet-lab 검증, 비용, 반복 주기 |
| 코드/알고리즘 | AlphaEvolve, ERA | 자동 평가자, 벤치마크, 재현 가능한 산출물 |
| 국가 인프라 | K-문샷, AI Campus, NAIS | 데이터, GPU, 인재, 출연연/대학/기업 연결 |
| 거버넌스 | Nature 비판 논문, AI 안전연구소 | 연구 신뢰성, 안전, 책임, 교육 |
| 실행 환경 | Cline, Qwen, Codex, Gemini CLI, Claude Code | 온프레미스/서비스 분리, MCP, 스킬, 자동화, 검증 로그 |
| 회사형 하네스 | 문제 카드, 데이터 패키지, 평가 함수 | 실제 문제를 AI 과학자형 작업 단위로 변환 |

## 산출물 요구

1. 한국어 기술동향 리포트 초안
2. 주요 사건 연표
3. 소스별 주장-근거-확신도 표
4. Co-Scientist / Robin / ERA / AlphaEvolve 비교표
5. 한국 K-문샷과 Google 협력의 정책·산업 함의
6. `우려 사항`을 독립된 장으로 구성한 심층 분석
7. 리뷰 후보 제목 3개와 추천 제목 1개
8. Skywork 슬라이드용 10~12장 구성안
9. 시각자료 제안: AI for Science 워크플로 맵, 인간-에이전트 책임 경계도, 우려/가드레일 매트릭스
10. 온프레미스/서비스 실행환경 비교표
11. 회사형 하네스 폴더 구조와 파일시스템 예시
12. `문제 카드`, `평가 함수`, `검토 게이트` 템플릿
13. 독자가 바로 따라할 수 있는 실제 사용 시나리오 3개
14. 프롬프트 예시, 데이터 스키마, 결과 저장 구조

## 작성 원칙

- 한국어로 작성한다.
- 사실, 해석, 미확인 주장을 구분한다.
- LinkedIn 메일 공유는 주제 발굴 신호로만 취급하고, 결론 근거로 쓰지 않는다.
- 뉴스스페이스의 GPT-5.4/에르되시 문제 보도는 독자 흥미를 여는 사례로 쓰되, 수학계 검증이 끝난 사실처럼 단정하지 않는다.
- Quanta의 수학 AI 기사와 Nature/Hani의 Bixonimania 사례를 도입부 양쪽 축으로 사용한다.
- 기술 주장에는 가능하면 논문, 공식 발표, 정부 문서 등 1차 출처를 우선 연결한다.
- 과장된 `AI 과학자 대체` 프레임을 피하고, 어떤 단계에서 어떤 도구가 어떤 검증을 거쳤는지 구체적으로 설명한다.
- 우려 섹션은 형식적 면피가 아니라 리뷰의 핵심 축으로 다룬다.
- 독자가 이미 AI 활용 의지가 있다는 전제에서 쓴다. 동기부여보다 실행 마찰을 줄이는 전략과 도구 선택 기준을 강조한다.
- 회사 내부 문제를 적극적으로 표면화하고, 사내 자원과 도메인 지식을 활용해 해결하려는 태도를 중심에 둔다.
- AI 과학자를 `충실한 조수`, `조언자`, `실무 수행자`로 쓰기 위한 역할·권한·검증 경계를 구체적으로 제안한다.
