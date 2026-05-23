# Skywork Prompt V1

업로드된 자료와 `LGD_Template.pptx`를 기반으로 새로운 Korean PowerPoint deck을 생성하라.

기본 템플릿 규칙:
- 사용자가 다른 템플릿을 명시하지 않았다면 `LGD_Template.pptx`를 기본 템플릿으로 사용하라.
- 템플릿은 source pack과 함께 기본 업로드 대상으로 간주하라.

프로젝트명: Display Week와 블루 OLED 관련 업데이트 종합 리뷰
청중: 디스플레이 소재/소자 연구자, OLED 제품전략 담당자, 기술전략 리더, 사업개발/투자 검토 인력
목적: Display Week 전후 blue OLED 관련 공개 신호를 `commercialization signal`, `research signal`, `uncertainty`, `diligence checklist` 관점에서 정리하는 기술 브리핑 deck
권장 분량: 12~14 slides
비율: 16:9

소스 우선순위:
1. 업로드된 `deepresearch.md`, `memo.md`, `sources.md`
2. 필요한 경우에만 문서 안에 이미 인용된 공식 source 범위

리서치 정책:
- 업로드된 문서는 이미 공식 source와 peer-reviewed paper 중심으로 정리되어 있으므로 외부 리서치는 최소화하고 구조화와 표현 정교화에 집중하라.
- 문서에 없는 새로운 수치나 기업 비교를 임의로 추가하지 말라.
- `2025`와 `2026` 시점을 반드시 구분하라.
- `commercialized pure-blue PHOLED`라고 과장하지 말고 `hybrid commercialization path`와 `PSF/PEP research progress`를 구분하라.

템플릿 원칙:
- LG Display 템플릿의 white-grid corporate rhythm은 유지하라.
- 브랜드형 sparse marketing deck이 아니라 정보 밀집형 technical briefing 스타일로 전개하라.
- 표, timeline, annotated diagram, evidence ladder, risk matrix를 적극 사용하라.

전체 서사:
- 왜 지금 `Display Week + blue OLED`를 함께 봐야 하는지 제시하라.
- Pulse가 묶은 이 주제가 사실은 `2025 commercialization signal + 2026 agreement signal + 2025-2026 literature signal`의 결합이라는 점을 먼저 보여라.
- LG Display의 `hybrid two-stack commercialization verification`이 의미하는 바와 한계를 분리하라.
- UDC-LGD 장기 계약 연장이 왜 roadmap confidence signal인지 설명하라.
- 최근 PSF / PEP / tandem PEP-PHOLED 논문이 남은 장벽을 어떻게 낮추는지 요약하라.
- 마지막은 `Display Week 현장 질문 리스트`와 `기술전략팀 next step`으로 닫아라.

섹션 정책:
- CH00: briefing, density=medium, evidence=explicit
- CH01: analysis, density=high, evidence=explicit
- CH02: internal_report, density=high, evidence=explicit
- CH03: analysis, density=high, evidence=explicit
- CH04: internal_report, density=high, evidence=explicit

반영해야 할 현재 사실:
- `2025-04-30` LG Display announced commercialization-level verification of blue phosphorescent OLED panels on a mass production line.
- The disclosed structure was a `hybrid two-stack Tandem OLED` with blue fluorescence in one stack and blue phosphorescence in the other.
- LG Display said the panel consumed about `15% less power` while maintaining a similar stability level to existing OLED panels.
- `2026-02-26` UDC and LG Display announced an extension of long-term OLED material supply and license agreements.
- The 2026 RSC paper reported `stable pure-blue phosphor-sensitized OLEDs utilizing a hypsochromic-shifting non-TADF fluorescent emitter`.
- Use the reported device anchors from the uploaded report, including `EQE = 18.7%`, `LT95 = 104.3 h`, `461 nm`, `CIE-y = 0.150`.
- The 2025 Advanced Materials paper reported about `3.1x` lifetime improvement for deep-blue PSF OLEDs in a `PEP` cavity at `10 mA cm^-2`.
- The 2025 Nature Photonics paper reported tandem deep-blue PEP-PHOLED lifetime and EQE metrics that are materially stronger than conventional single-junction comparators.
- The most accurate synthesis is not `blue OLED solved`, but `hybrid commercialization path emerging while PSF/PEP literature reduces the remaining lifetime barrier`.

권장 장표 구성:
- Slide 1: title + one-line thesis
- Slide 2: why this topic matters now, with explicit date anchors
- Slide 3: evidence ladder timeline (`2025-04-30`, `2025 literature`, `2026-02-26`, `Display Week 2026`)
- Slide 4: what LG Display actually proved
- Slide 5: what LG Display did not yet publicly prove
- Slide 6: why the UDC-LGD extension matters
- Slide 7: 2026 RSC pure-blue PSF OLED update
- Slide 8: 2025 PEP / tandem PEP-PHOLED research update
- Slide 9: commercialization path vs research path comparison table
- Slide 10: Display Week diligence checklist
- Slide 11: implications for panel strategy, supply chain, and technology scouting
- Slide 12: recommended next actions for a technical strategy team
- Slide 13: closing recommendation

시각/레이아웃 정책:
- base template rhythm은 유지하라.
- 같은 카드형을 반복하지 말고 장표 목적에 따라 서브템플릿을 바꿔라.
- compound slide를 허용하되 하나의 상위 인사이트로 수렴시켜라.
- sparse marketing layout보다 구조화된 정보 밀집형 구성을 우선하라.
- timeline strip, evidence matrix, risk/uncertainty board, annotated architecture-like diagrams를 적극 사용하라.
- 기술 용어, caveat, metric condition, interpretation note는 작은 짙은 녹색 inline annotation text로 옆이나 아래에 붙일 수 있다.
- references가 필요한 slide에는 하단 또는 관련 블록 근처에 작은 짙은 회색 text로 공식 출처를 넣어라.

좋은 장표가 되기 위한 규칙:
- `fact`, `interpretation`, `uncertainty`를 섞지 말라.
- 한 슬라이드마다 하나의 상위 메시지를 유지하되, 실무 판단에 필요한 세부 비교는 숨기지 말라.
- 기술 리더가 바로 질문 리스트와 판단 포인트를 가져갈 수 있을 정도로 information-dense 하게 만들어라.

피해야 할 것:
- `blue PHOLED solved` 같은 과장된 headline
- `hybrid commercialization verification`과 `pure-blue direct commercialization`의 혼동
- 확인되지 않은 yield, lifetime, market-share 수치 추가
- 큰 빈 공간 위주의 미려한 deck

이 기준으로 전체 deck을 생성하라.
