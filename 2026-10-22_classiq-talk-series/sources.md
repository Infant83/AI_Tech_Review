# 출처와 작성 검증 공개

## 원영상과 행사 안내

1. [Classiq 새 플랫폼 다시보기](https://www.youtube.com/watch?v=QtKbkvWgncQ), 행사 2026-10-21. [공식 행사 안내](https://get.classiq.io/office-hour-webinars/the-new-classiq-platform/).
2. [Classiq와 NVIDIA CUDA-Q 금융 웨비나 다시보기](https://www.youtube.com/watch?v=E4Uko49fBaU), 행사 2026-10-15. [공식 행사 안내](https://get.classiq.io/events-and-webinars/building-practical-quantum-finance-applications-with-nvidia/).
3. [AI 에이전트 다시보기](https://www.youtube.com/watch?v=gaLZNQkcsp8), 행사 2026-07-08. [공식 행사 안내](https://get.classiq.io/office-hour-webinars/from-idea-to-quantum-circuit-with-ai-agents/).
4. [금융 문제의 양자 응용 다시보기](https://www.youtube.com/watch?v=diJa_JRJ2F8), 행사 2026-08-27. [공식 행사 안내](https://get.classiq.io/office-hour-webinars/quantum-computing-for-finance/).

공식 시리즈명은 Quantum Office Hours이며 NVIDIA 공동 웨비나는 별도 행사다. 두 종류를 최근 제품·응용 세션이라는 범위로 함께 정리했다. 공식 채널에는 별도의 [Classiq Talks 재생목록](https://www.youtube.com/playlist?list=PLdt5EdfrcDgU)도 있다. 이 노트의 네 회차와 동일한 재생목록은 아니다.

## 보충 학습 자료

- [Classiq 문서](https://docs.classiq.io/latest/): Qmod, 합성, 실행, 응용 예제. 움직이는 latest 문서이므로 재현에는 SDK 버전 고정이 필요하다.
- [Classiq 공식 응용 저장소](https://github.com/Classiq/classiq-library): 세션의 수학과 구현을 더 읽는 출발점. 현재 파일이 영상 촬영 시점의 파일과 같다고 가정하지 않는다.
- [Classiq within_apply와 Grover 연산자 예제](https://docs.classiq.io/qmod-reference/language-reference/statements/within-apply): 준비·적용·역준비 구조.
- [NVIDIA CUDA-Q 실행 문서](https://nvidia.github.io/cuda-quantum/latest/using/basics/run_kernel.html): sample·observe와 실행 타깃을 구별할 자료.
- [Brassard 등 진폭 증폭과 추정](https://arxiv.org/abs/quant-ph/0005055), 2000: 진폭 증폭과 QAE의 원 논문.
- [Grinko 등 IQAE](https://arxiv.org/abs/1912.05559), 최초 공개 2019, npj Quantum Information 7, 52 (2021): 위상추정 없이 반복하는 진폭 추정.
- [Farhi 등 QAOA](https://arxiv.org/abs/1411.4028), 2014: 근사 조합최적화 알고리즘의 원 제안.

## 확인 범위

각 회차는 실제 영상의 시간정보가 있는 전사 내용을 읽고 발표의 순서와 질문·답변을 재구성했다. 자동자막의 전문용어 오인은 공식 명칭과 문맥으로 바로잡았다. 최신 회차는 로컬 음성인식을 사용했다. 화면으로 직접 확인한 기능 명칭이나 실행 타깃은 본문에 그 범위를 적었다. 발표자가 보고한 외부 성능 수치를 이 작업에서 재현한 측정값으로 표시하지 않는다.

손계산 예제의 목적함수·성공확률·표본오차·메모리·총시간은 독립 계산으로 대조했다. 실제 Classiq 클라우드 합성이나 QPU 작업을 새로 제출하지 않았다. 작은 전수열거는 해당 유한 입력의 해를 확인하며 일반 알고리즘 성능을 평가하지 않는다.

## 발표 화면과 설명 도식

발표 화면의 원출처는 각 캡션에 연결한 Classiq Technologies 공식 다시보기다. Classiq·NVIDIA 발표자의 코드·화면·출력 중 설명에 필요한 부분을 발췌했다. 브라우저 도구막대와 계정·경로·관련 없는 화면은 제외하고, 원본의 수치·코드·곡선을 그대로 보존했다. 그래프의 축이나 출력값을 다시 그려 실제 화면처럼 표시하지 않았다. 코드와 비교표의 한국어 설명은 본문과 캡션에서 제공한다.

별도 설명 도식은 노트에서 정의한 작은 입력·가정·알고리즘 구조로 제작했다. Grover 반복의 이상적 확률, QAOA의 유효 상태 수, 기대 payoff와 진폭 인코딩은 계산 예이며 실제 QPU 측정값이 아니다. 자원 비교 그림은 전체 기간·하루 단위의 처리 범위와 방향 고정에 따른 자유도 변화를 함께 표시한다.

그림마다 종류·출처·영상 시각 또는 계산 조건을 캡션에 적었다. 최종 선택 목록과 파일 해시는 읽기용 폴더의 `figures/manifest.json`에 남겼다. SVG·PNG에 개인 환경의 경로와 계정 정보를 포함하지 않았는지 검사하고 HTML·PDF에서 가독성과 잘림을 확인했다. 원영상·전체 대본·음성 파일과 검수용 화면 모음은 읽기용 파일에 수록하지 않는다.

## 작성과 검토

책임 편집자는 김현중이며 AI 지원 시스템은 OpenAI Codex다. 작업자 **root**는 범위 확인, 통합 편집, 보충 수학·용어집·문제, HTML·PDF와 출력 검사를 맡았다. **find_talk_series**는 공식 영상·행사 조사와 1회 전사를, **finance_replay**는 2회의 전사·영상 화면·계산 대조를, **earlier_office_hours**는 3·4회와 질의응답 검토를 맡았다. 정확한 실행 모델 식별자는 별도 실행 기록에 보존하지 않아 추정하지 않는다.

1.1판에서는 **concept_figures**가 계산·개념 도식, **platform_screens**가 새 플랫폼 발표 화면, **finance_screens**가 금융 발표 화면의 선별·출처 기록을 맡았다. root는 본문과 캡션을 연결하고, 원자료와 도식의 의미·수치를 대조하며 읽기용 파일에 통합했다.

적용 편집 원칙은 [AI Tech Review Editorial Harness 2026.08](https://infant83.github.io/AI_Tech_Review/methods/)이다. 용어·실행 수준·발표와 보충 설명의 경계를 검토하고, 브라우저와 PDF에서 글꼴·수식·표·페이지를 확인했다. 사람의 문장별 감수나 강사의 승인을 마쳤다고 주장하지 않는다. 후속 자막·공식 코드·정정이 나오면 행사일과 판본을 유지하면서 해당 근거를 갱신할 수 있다.
