# 하네스 엔지니어링 원문·서지 감사

대상: `2026-05-09_ai-updates-weekly`. 원 발행일 2026-05-09, 원 수정·근거 범위 2026-05-13을 보존하는 순차 개편의 독립 대조다. 확인일은 2026-10-27이며 과거 확인일을 새로 만들어 쓰지 않는다. 원 논문 실험·벤치마크와 제품 기능을 직접 실행하거나 재현하지 않았다. 역할: `legacy_harness_sources`.

## 우선 반영할 판단

1. **논문 판본:** Natural-Language Agent Harnesses는 v1(2026-03-26)을 사용한다. v2는 5월 18일이어서 원 근거 범위 밖이다. Meta-Harness는 v1(3월 30일), 절차형 오케스트레이션 논문은 v2(5월 5일)를 확인했다.
2. **절차형 작업의 결과:** 여행 예약·Zoom 지원·보험 청구는 합성 절차와 모의 사용자 환경이고, 같은 Claude Sonnet 4.5를 두 실행 방식에 사용했다. 조건·영역별 200개 대화를 LLM 심사로 평가했다. 원문 v2는 GPT-4.1 재채점도 포함하며 자연스러움의 우위는 심사 모델에 따라 달랐다. 본문의 높은 점수·낮은 실패율은 이 실험 조건의 보고다. 실제 조직의 생산성이나 사람 평가 결과로 확대하지 않는다.
3. **금융 발표:** [Anthropic 원 발표](https://www.anthropic.com/news/finance-agents)는 2026-05-05자다. 10개 템플릿·KYC·월말 마감·pitchbook·Microsoft 문서 도구·Moody's MCP app과 사람 검토를 실제로 설명한다. 다만 도입 요약에서 Outlook을 `coming soon`으로 명시한다. Outlook도 이미 제공된 것처럼 한데 묶지 않고 발표·예고로 구분한다.
4. **보안 발표:** [원 발표](https://www.anthropic.com/news/claude-code-security)는 2026-02-20자 limited research preview다. 코드 흐름 추론·다단계 자체 검증·사람 승인 후 패치 적용을 설명한다. 정식 일반 제공으로 쓰지 않는다.
5. **Managed Agents 날짜 충돌:** 현재 [공식 원문](https://claude.com/resources/articles/new-in-claude-managed-agents)은 2026-05-19로 표시하고 Dreaming을 research preview로 소개한다. 반면 보존된 5월 8일 영상 전사와 슬라이드는 Dreaming·Outcomes와 같은 URL을 실제로 언급한다. 보존 슬라이드의 파일 바이트는 5월 11일 Git 커밋의 공개 PPTX와 같다. 따라서 현재 페이지를 근거로 기능이 5월 13일까지 공식 제공됐다고 단정할 수 없고, 원글이 확실히 미래 발표를 잘못 썼다고 단정할 수도 없다. 날짜가 충돌하는 제품 예시를 역사적 제공 사실로 쓰지 않고, 기억 선별·평가 루프의 일반 설명을 보존하는 편집이 안전하다. 이름을 남기려면 당시 탐색 자료의 소개라는 귀속과 확인 한계를 분명히 한다. 현재 공식 발표일을 과거의 사실처럼 소급하지 않는다.
6. **SpaceX:** [2026-05-06 발표](https://www.anthropic.com/news/higher-limits-spacex)는 Colossus 1 계산 자원 계약, Claude Code 5시간 한도 확대와 Pro·Max의 피크시간 감축 제거를 설명한다. 모든 계정의 동일한 제한 제거로 확대하지 않는다.
7. **xAI:** 현재 [Connectors](https://docs.x.ai/grok/connectors)는 2026-10-10 최종 갱신으로 표시되며 회사 표기도 변경됐다. Gmail·Calendar·Drive·OneDrive·Outlook·SharePoint 및 OAuth 설명은 현재 문서에서 확인되지만 이 페이지 자체는 5월 판본이 아니다. 보존된 5월 탐색 슬라이드는 Gmail·Drive·Calendar·SharePoint·OneDrive와 OAuth를 명시한다. 당시 범위에서 필요한 사례만 유지하고 현재 Teams·Salesforce·MCP tunneling 등의 새 목록을 보태지 않는다. Outlook의 당시 제공 상태는 별도 과거 캡처를 확보하지 못했다.
8. **의료 사례:** [Google DeepMind 원문](https://deepmind.google/blog/ai-co-clinician/)의 일자 2026-04-30과 저자 Alan Karthikesalingam, Vivek Natarajan, Pushmeet Kohli를 확인했다. Planner/Talker와 임상 대화 모의평가, 근거·인용 확인을 실제 설명한다. 실제 환자 진단·치료·예방·의학적 조언의 제공 성과로 서술하지 않는다.

## 논문 크레딧과 대조 범위

| 원문 | 판본·저자 | 본문과의 대응 |
|---|---|---|
| [Natural-Language Agent Harnesses](https://arxiv.org/html/2603.25723v1) | Linyue Pan, Lexiao Zou, Shuo Guo, Jingchen Ni, Hai-Tao Zheng; v1 | §§2.2–2.4는 계약·권한 범위·출력·단계·검증·재시도·지속 상태를 명시한다. 본문의 테스트 재실행·승인 예시는 리뷰의 설명 예시로 쓰고 논문의 실제 지시문을 직접 인용한 것처럼 쓰지 않는다. |
| [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/html/2603.28052v1) | Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn; v1 | §3은 이전 후보 코드·점수·실행 trace를 파일시스템에서 읽는 proposer와 하네스 코드 탐색을 설명한다. 본문의 운영상 권고는 이 원리에 대한 리뷰 해석이다. |
| [In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks](https://arxiv.org/html/2604.27891v2) | Simon Dennis, Michael Diamond, Rivaan Patil, Kevin Shabahang, Hao Guo; v2 | §2.2–2.3, §3, §5.2를 대조했다. 외부 상태 추적과 전체 절차 프롬프트의 비교이며, 단일 대 다중 에이전트 일반 우열과 같은 실험이 아니다. |

## 테스트·평가 하네스의 근거

- 기존 TechTarget 글의 저자는 **Alexander S. Gillis**, 원제는 **test harness**, 일자 2019-02-07이다. 현재 URL은 IT Infrastructure 경로로 이동한다. 기존 크레딧을 보존할 수 있다.
- 1차 용어 근거로 [ISTQB test harness](https://glossary.istqb.org/en_US/term/test-harness)를 함께 쓰거나 대체할 수 있다. 공식 용어는 test suite 실행에 필요한 driver와 test double의 모음이다. 2020년 용어 개정 기록은 하네스가 테스트 환경 전체의 동의어가 아니라 그 일부라는 점을 분명히 한다. 새 글에서 운영 하네스 전체의 정의로 그대로 옮기지 않는다.
- EleutherAI 저장소의 `CITATION.bib`를 역사적 커밋에서도 대조했다. 권장 인용은 **L. Gao et al., A framework for few-shot language model evaluation, v0.4.0, Zenodo (2023), DOI 10.5281/zenodo.10256836**이다. 저자 24명이므로 APS·저장소 기준상 첫 저자와 et al.을 쓴다. 사용한 README 판본과 권장 소프트웨어 인용의 버전은 다르므로 함께 식별하되 동일 버전으로 혼동하지 않는다.

## 5월에 존재한 저장소 문서

아래 SHA는 GitHub commits API에서 2026-05-13 UTC 말까지의 커밋으로 조회하고 그 커밋의 원문 README를 읽은 결과다. 실제 당시 이 글이 사용한 커밋이 보존돼 있다는 뜻은 아니다. 새 검수에서 선택한 역사적 대조 판본이며 기능 실행·성능 재현도 아니다. 날짜를 시각까지 복원한 원 출판 기록이 없으므로 원고에서는 이들의 기능 목록을 그 시기 문서 사례로 제한한다.

| 저장소 | 대조한 커밋 | 확인한 내용 |
|---|---|---|
| Hmbown/DeepSeek-TUI | `6b5011a7228371543456d11c7f217ff0d28f4ce4` (5/13) | 파일·셸·Git·웹·MCP·하위 에이전트·승인 모드·세션 재개. |
| nousresearch/hermes-agent | `9d42c2c2869e5be531b6302bdc8ea6c6269a9604` (5/13) | CLI·messaging gateway. `website/docs/user-guide/features/curator.md`는 agent-created skills의 active→stale→archived 관리와 주기적 검토를 명시한다. 현재 기본 보관 기간 등 후대 변경을 보태지 않는다. |
| VRSEN/OpenSwarm | `d20c60e1212301ed9b4f11702f51e8a06c86413b` (5/12) | 슬라이드·보고서·시각화·문서·이미지·영상 생성 지향. 실제 모든 산출물의 품질을 검증한 것은 아니다. |
| InsForge/InsForge | `c91ae4352f258b6a83d1adb90c361d842396a21a` (5/13) | 데이터베이스·인증·저장소·계산·호스팅·AI gateway와 MCP 실행 통로. |
| zed-industries/zed | `3a8d012d1a846272c2ba019176352bbd1befa6cf` (5/13) | `docs/src/ai/overview.md`: Rust·GPU native 앱, agentic editing·inline transformations·completion·모델 대화. |
| jj-vcs/jj | `2144f50a5836822f4b1b5a5b3bae1c280e4ef3f3` (5/13) | Git 저장 계층과 별도의 버전관리 모델. |
| ataraxy-labs/weave | `a278d32138f94ecdb6c2313883c8fbeeb2d31fb1` (5/12) | entity-level merge·tree-sitter와 Git/Jujutsu 연결. MCP/coordination은 당시 슬라이드와 현재 공식 소개에서 표방하지만 이번 역사적 README의 구체 구현까지 검증하지 않았다. 본문을 entity-level merge 중심으로 한정하면 근거가 분명하다. |
| EleutherAI/lm-evaluation-harness | `95d580638385578c1c07fa554cf16ad7f5b5f460` (5/11) | 평가 실행 환경과 권장 `CITATION.bib`. |
| lselector/seminar | `3999fa63ba430df0e5cda476e31734bff707fc1d` (5/11) | `2026/2026-05-08-AI-Updates.pptx`가 저장된 원 PPTX와 바이트 동일. SHA-256 `82d3c12d1f178a8320845ce657df0b13c9d28abcd51edb754c3401e68e0571d3`. |

[Mergiraf 공식 소개](https://mergiraf.org/)는 syntax/tree-aware merge와 해결 결과의 사람 검토를 설명한다. 이번에는 역사적 코드 판본까지 확보하지 않았으므로 수치 우위나 모든 semantic conflict 해결을 주장하지 않는다. 원 슬라이드에 이미 해당 도구와 기능이 제시된 점은 확인했다.

## 참고문헌 정리 방법

`proposed-bibliography.md`의 번호는 **기존 본문의 첫 등장순** 제안이다. 수정 본문에서 사례가 빠지거나 순서가 바뀌면 다시 번호를 매긴다. 본문·표의 제품 이름 링크는 설명 위치에서 번호 인용으로 연결하고, 아래 서지는 원제·저자·판본만 쓴다. 글쓰기·그림 제작에 참고한 HORIZON·Quanta·Science Note와 내부 빌더·하네스는 작성·제작 정보에서 필요한 크레딧으로 남기고, 과학적 주장 근거의 서지 목록과 섞지 않는다.

Lev Selector의 원 영상·슬라이드는 주제 탐색의 기여로 함께 크레딧을 준다. 영상명은 **Exciting AI Updates Weekly - May 8, 2026**, 업로드 기록은 2026-05-08이다. 영상의 현재 온라인 열람은 throttling으로 제한됐으며 보존된 공개 메타데이터·전사·바이트가 일치한 역사적 슬라이드를 대조했다. 영상의 소개를 모든 제품의 공식 제공 검증으로 대신하지 않는다.

## 통합 원고의 최종 서지 점검

2026-10-27 통합 원고에서 현행 Managed Agents 발표를 독립 서지에서 제외하고, 당시 주제 탐색 영상·슬라이드를 기억·평가 설명과 Grok 소개의 근거로 귀속한 것을 확인했다. 실제 목록은 19개 번호 그룹이며 본문·표·작성 정보의 번호 인용 링크 39개를 가진다. 최초 등장순이 정확히 1–19이고, 모든 인용의 표시 번호·대상 anchor·`reference-manifest.json`의 개수가 일치한다. 세 논문의 원저자·원제·v1/v1/v2, 역사적 저장소 판본과 실제 원 작성 사용 버전의 구분, 금융 Outlook의 예고, Pro·Max 피크 제한의 범위가 반영됐다.

서지와 근거 대응은 통과했다. 본문 주제 안내 표의 절차형 작업 설명에서 ‘여러 에이전트 대 한 모델’로 축약한 문구는 외부 오케스트레이터의 단계별 제어와 전체 절차 문맥을 비교하는 문구로 맞추도록 총괄에 전달했다. Grok 문단의 끝에 독립적으로 남은 ‘발표자료 [17]’도 앞 문장의 끝으로 연결하도록 제안했다. 실제 HTML·모바일·배포 확인은 총괄의 별도 출력 검수 범위다.
