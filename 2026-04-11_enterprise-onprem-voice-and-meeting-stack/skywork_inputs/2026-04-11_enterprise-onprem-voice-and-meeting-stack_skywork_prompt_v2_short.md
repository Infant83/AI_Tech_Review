# Skywork Prompt V2

업로드된 `LGD_Template.pptx`, `deepresearch.md`, `memo.md`, `sources.md`를 사용해 한국어 기술 브리핑용 PowerPoint deck을 생성하라.

핵심 요구:
- LG Display 템플릿의 corporate white-grid rhythm을 유지하라.
- sparse marketing deck이 아니라 information-dense technical briefing 스타일로 구성하라.
- 청중은 AI 플랫폼 리드, 음성/ML 엔지니어, 인프라/보안 담당자다.
- 목적은 Picovoice를 중심으로 기업 on-prem STT/TTS/회의록 스택의 실용성과 한계를 평가하고, 실전 권고 아키텍처와 PoC 방향을 제시하는 것이다.
- 새로운 수치나 확인되지 않은 벤더 비교를 임의로 추가하지 말라.
- 업로드된 자료 안의 사실만 사용하라.

반드시 반영할 사실:
- `Leopard`는 Korean batch STT를 지원한다.
- `Orca`는 on-device / on-prem / streaming TTS 용도다.
- `Falcon`은 diarization component다.
- `Cheetah`의 Korean streaming STT self-serve availability는 문서상 모호하다.
- Picovoice pricing 문서에는 AccessKey validation / plan limit 확인을 위한 call-home behavior가 있다.
- 회의록 품질의 핵심 병목은 STT/TTS만이 아니라 diarization, segmentation, summarization, action-item extraction, workflow integration이다.
- 실전 기본 대안은 `whisper.cpp 또는 faster-whisper + pyannote + llama.cpp`다.
- GPU-backed enterprise 대안은 `NVIDIA Riva`다.

권장 장표:
1. 제목 + 한 줄 결론
2. 왜 기업 on-prem speech stack이 중요한가
3. `speech I/O`와 `meeting notes system`의 차이
4. Picovoice component map
5. Picovoice가 잘하는 것
6. Picovoice 단독 접근의 한계
7. Korean streaming STT ambiguity + strict air-gap / AccessKey risk
8. Picovoice vs Whisper stack vs Riva 비교표
9. Reference architecture A: local voice assistant
10. Reference architecture B: private meeting-note pipeline
11. Reference architecture C: enterprise-supported GPU speech platform
12. 90-day PoC plan + go/no-go criteria
13. 기술 리더용 최종 권고

레이아웃 요구:
- 표, 비교 보드, architecture block diagram, workflow strip, risk matrix를 적극 사용하라.
- 각 장표는 하나의 상위 메시지를 유지하되, 실무 판단에 필요한 세부 비교는 숨기지 말라.
- 하단에는 필요한 경우 작은 회색 출처 텍스트를 넣어라.
- 운영 제약, 한국어 지원 모호성, air-gap caveat는 작은 짙은 녹색 annotation으로 표시하라.

금지:
- Picovoice를 완성형 enterprise meeting-note platform처럼 과장하지 말라.
- 미확인 benchmark를 넣지 말라.
- 빈 공간 위주 미려한 deck로 약화시키지 말라.

분량은 12~14장, 비율은 16:9로 유지하라.
