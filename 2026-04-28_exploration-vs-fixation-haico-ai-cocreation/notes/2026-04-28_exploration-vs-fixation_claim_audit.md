# Claim audit

date: 2026-04-28
paper: arXiv:2512.18388v2

## 확인됨

| 주장 | 근거 | 상태 |
|---|---|---|
| HAICo는 창작 과정을 Divergent mode와 Convergent mode로 분리한다. | 논문 abstract, section 4 | 확인됨 |
| 연구는 poster image creation task에서 ChatGPT와 HAICo를 within-subjects로 비교했다. | 논문 section 5, `N = 24` | 확인됨 |
| HAICo는 CSI, UMUX-Lite, novelty, diversity에서 ChatGPT보다 높았다. | 논문 Fig. 5 및 section 6.1 | 확인됨 |
| Fluency와 usefulness는 유의미한 차이가 없었다. | 논문 Fig. 5 caption | 확인됨 |
| associative-thinking prompting은 non-associative prompt보다 idea diversity가 높았다. | 논문 Fig. 7, `W = 24.0`, `p < 0.001` | 확인됨 |
| HAICo 사용자는 ChatGPT 사용자보다 self-reported learning이 높았다. | 논문 Fig. 9, `M = 5.29 vs. 3.12`, `p < 0.001` | 확인됨 |
| ChatGPT 경험은 주로 tool/prompt learning으로, HAICo 경험은 task/workflow learning으로 보고되었다. | 논문 section 6.4, 7.4 | 확인됨 |

## 주의 필요

| 주장 | 이유 | 처리 |
|---|---|---|
| 이 결과가 모든 창의 작업에 적용된다. | 연구 도메인은 이미지 포스터 생성이고 세션은 단회성이다. | `확장 가능성`으로만 표현 |
| HAICo가 공개 도구로 바로 쓰일 수 있다. | 연구 시스템이며 일반 공개 서비스가 아니다. | 실무 적용은 워크플로 원리 중심으로 제시 |
| 학습 효과가 장기적으로 유지된다. | self-reported learning이고 장기 추적이 없다. | 장기 효과는 미검증으로 표시 |
| 스캐폴딩은 항상 좋다. | 목표가 명확한 경우 ChatGPT식 직접 실행도 유용하다는 참가자 의견이 있다. | 작업 유형별 사용 기준 제시 |
| AI가 개인 창의성을 높이면 조직 창의성도 자동으로 높아진다. | Doshi/Hauser와 Anderson/Shah/Kreminski는 집단 다양성 저하 가능성을 보고했다. | 개인 생산성과 조직 다양성을 분리 |

## 확장 해석

| 해석 | 근거 | 슬라이드 반영 |
|---|---|---|
| 사용자에게 중요한 것은 프롬프트 문장 하나보다 작업 순서다. | HAICo의 성과는 두 모드 분리, idea grid, semantic parameters에서 나온다. | workflow 전환 슬라이드 |
| 업무용 AI는 "대답 생성기"보다 "탐색판 + 선택판 + 실행판"으로 설계해야 한다. | divergent/convergent 분리와 non-linear context preservation | 실무 적용 슬라이드 |
| 조직에서는 같은 모델을 같은 방식으로 쓰면 아이디어가 비슷해질 수 있다. | Doshi/Hauser, Anderson/Shah/Kreminski | 다양성 거버넌스 슬라이드 |
| 프롬프트 교육은 도구 조작 교육에 그치기 쉽다. | ChatGPT condition의 system learning 우세 | 사용자 교육 슬라이드 |
| 코딩·기획·데이터 시각화에도 "초기 산출물 고착" 위험이 있다. | 논문 conclusion의 소프트웨어·시각화·발표 설계 예시, Parsons et al. 데이터 시각화 fixation | 적용 도메인 슬라이드 |
