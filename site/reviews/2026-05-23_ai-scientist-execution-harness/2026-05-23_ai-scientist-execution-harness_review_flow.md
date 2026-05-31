# 리뷰 흐름 정리

## 제목

**AI 과학자는 어떻게 우리 곁에 오는가**

부제:

**에르되시 문제 #1196에서 AI Co-Scientist까지, 발견의 속도와 검증 가능한 실행 환경을 읽는 Tech Review**

## 한 문장 메시지

AI 과학자는 인간 연구자의 자리를 단번에 대체하는 존재라기보다, 사람이 고른 문제를 더 많은 후보 경로와 더 빠른 반복으로 넓혀주는 실행 파트너입니다. 그 힘은 문제, 자료, 도구, 평가, 기록이 한 작업대 위에 놓일 때 가장 잘 드러납니다.

## 개정 흐름

1. **수학 칠판의 장면**
   - Quanta의 AI 수학 전환과 뉴스스페이스의 에르되시 #1196 보도를 흥미의 출발점으로 둡니다.
   - 에르되시가 어떤 수학자였는지, 에르되시 문제란 무엇인지, #1196이 왜 긴 기다림을 가졌는지 먼저 풉니다.
   - `primitive set`, `Erdős sum`, 기존 `1.399 + o(1)` 상한, GPT-5.4 Pro와 Liam Price의 프롬프트, Markov chain과 von Mangoldt weights, 인간 수학자의 정리와 Lean 검증까지 연결합니다.

2. **수학에서 과학으로**
   - 수학의 검증 가능한 증명 흐름을 생명과학·소프트웨어·알고리즘 탐색으로 확장합니다.
   - Co-Scientist, Robin, ERA, AlphaEvolve를 나열하지 않고, 연구 업무의 작은 단위가 빨리 반복되는 변화로 묶습니다.

3. **국가와 기업의 속도**
   - Google DeepMind-과기정통부 파트너십, K-문샷, AI Campus, AI 과학자 프로젝트를 다룹니다.
   - 회사가 가진 실패 기록, 품질 이슈, 실험 데이터, 장비/recipe 이력을 AI 과학자형 작업으로 옮길 수 있는 자원으로 배치합니다.

4. **기대가 커질수록 생기는 물음**
   - 독자가 스스로 “이렇게 빨라져도 괜찮을까?”라고 느끼는 지점에서 Bixonimania를 꺼냅니다.
   - Nature 사설/Comment와 Quanta의 수학 교육·지식 오염 우려를 함께 놓습니다.

5. **회사 문제를 작업대에 올리기**
   - 하네스라는 용어를 과하게 밀지 않고, 작업대·작업 폴더·실행 루프 중심으로 풀어냅니다.
   - 문제 카드, 자료와 데이터, 에이전트 워크벤치, 평가 함수, 검토 로그를 제시합니다.

6. **지금 쓸 수 있는 세 가지 장면**
   - 공개 자료 기반 가설 탐색: Codex, Gemini CLI, Claude Code
   - 온프레미스 민감 자료 분석: Cline + Qwen/Ollama/LM Studio + MCP
   - 반복 평가와 보고 자동화: Gemini CLI headless, Claude print mode, Codex/Qwen Code

7. **작은 작업 폴더**
   - 파일 구조, `problem_card.yaml`, `.cline/mcp.json`, prompt, JSON 결과, Python evaluator를 보여줍니다.

8. **우려를 작업 안에 넣는 방법**
   - 지식 오염, 데이터 반출, 훈련 약화, 벤더 종속을 설교처럼 분리하지 않고 산출물 안의 항목으로 넣습니다.

9. **조수라는 말의 무게**
   - AI 과학자를 무궁한 가능성을 가진 조수로 두되, 사람이 문제를 고르고 다음 실험과 다음 질문으로 옮기는 장면으로 마무리합니다.

## 시각 자료

- `imagegen/ai_scientist_erdos_blackboard.png`: 도입 hero
- `ai_scientist_erdos_1196_explainer.svg`: 에르되시 #1196 설명 도해
- `imagegen/ai_scientist_coscientist_lab.png`: Co-Scientist 연구실 장면
- `imagegen/ai_scientist_guarded_library.png`: 지식 오염과 검증 장면
- `ai_scientist_validation_loop.svg`: 실행 루프
- `ai_scientist_harness_example.svg`: 작업 폴더 구조
- `ai_scientist_guardrail_matrix.svg`: 위험과 대응 매트릭스

## 문체 원칙

- 독자에게 해석을 명령하지 않습니다.
- `사례로 읽는 편이 안전합니다`, `짚었습니다`, `보여줍니다`, `하자는 뜻은 아닙니다` 계열의 판정/교정 문장을 피합니다.
- `하네스`, `감사`, `암묵지`, `인간의 판단` 같은 지난 리뷰의 반복 표현은 꼭 필요한 곳에만 둡니다.
- 호기심, 가능성, 작동 방식, 실전 장면이 먼저 오고 우려는 자연스러운 질문의 자리에서 꺼냅니다.
