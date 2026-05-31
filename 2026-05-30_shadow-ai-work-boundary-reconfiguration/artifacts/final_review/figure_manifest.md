# Figure Manifest

## 생성 정보

- Review: `2026-05-30_shadow-ai-work-boundary-reconfiguration`
- Report: `reports/2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.md`
- 작성일: 2026-05-30
- Figure count: 7
- Bitmap illustration: `imagegen` 3개
- Deterministic diagram: SVG 4개
- 역할 분리: `imagegen`은 Quanta/KIAS Horizon식 기사형 진입 장면과 섹션 opener를 담당하고, SVG는 정확한 한국어 라벨과 구조 설명을 담당했습니다.

## 채택 Figure

| Figure | 파일 | 형식 | 본문 위치 | 목적 | 검토 기록 |
|---|---|---|---|---|---|
| 그림 1 | `figures/imagegen/shadow_ai_calm_silo_night_v11_clean.png` | imagegen PNG | 도입부 hero | 밤의 집에서 개인 AI 산출물이 은은한 흐름으로 회사에 닿지만, DX가 된 회사 내부에서는 분리된 팀·승인·검증 silo와 일부 AX 구간이 hidden effort에 기대어 연결되는 장면 | 채택. v10은 메시지는 맞았지만 빛과 속도감이 과해 기존 AI Tech Review Letters의 차분한 수채화 톤과 어긋났습니다. v11 clean은 사외 AI의 빠른 실행, 야간 개인 작업, 회사 내부 silo, 부분적 AX 성공, shadow effort와 burnout을 더 절제된 톤으로 보여줍니다. |
| 그림 2 | `figures/shadow_ai_absorption_gap_hero.svg` | SVG | 핵심 문제의식 뒤 | 외부 AI 역량과 내부 운영체계의 속도 차이를 구조적으로 설명 | 채택. 정확한 한국어 라벨과 관계 표시가 중요해 SVG로 유지. 2026-05-31 재점검에서 카드 내부 곡선 화살표를 제거하고, 카드 간 진행 화살표와 하단 누적 단계 화살표만 남겨 방향성을 명확히 정리. |
| 그림 3 | `figures/shadow_ai_mechanism_flow.svg` | SVG | Shadow AI 발생 과정 설명 뒤 | Shadow AI가 개인 일탈이 아니라 단계적 운영 실패로 생기는 과정을 설명 | 채택. 발생 순서를 독자가 따라가도록 7단계 흐름으로 구성. 2026-05-31 배포 전 점검에서 하단 결론 문장이 박스 폭을 넘을 수 있어 2줄 구성으로 수정. |
| 그림 4 | `figures/imagegen/shadow_ai_hidden_work_cascade.png` | imagegen PNG | AI FOMO Cascade와 숨은 노동 사이 | 경영진 기대, 승인 지연, 보안 점검, 개인 학습 시간이 실무자의 숨은 노동으로 겹치는 장면 제시 | 채택. 감정 과잉 없이 야간의 업무 압박과 보이지 않는 비용을 보여줌. |
| 그림 5 | `figures/imagegen/shadow_ai_governed_paths_room.png` | imagegen PNG | 공식 사용 경로 섹션 | 공개자료 실험, 사내 일반자료 처리, 민감자료 분석이 검토와 기록으로 연결되는 운영 공간 제시 | 채택. 1차 후보에는 `AI Gateway`라는 읽을 수 있는 영어 라벨이 있어 기각했고, 텍스트 없는 버전으로 재생성. |
| 그림 6 | `figures/shadow_ai_governance_model.svg` | SVG | 데이터 등급 기반 운영 모델 | 데이터 등급, 사용 경로, 검증, 로그, 실제 AI 업무시간 기록 구조를 설명 | 채택. 도구명 허용/금지가 아니라 데이터 등급과 운영 기록을 함께 배치. 2026-05-31 배포 전 점검에서 제목과 하단 성공 조건 문구를 줄여 모바일 축소 가독성을 개선. |
| 그림 7 | `figures/shadow_ai_reference_map.svg` | SVG | 결론 및 참고자료 앞 | 주요 참고자료가 업무 변화, 성과, 보안, 노동 부하, 한국 제도 맥락을 어떻게 나누어 뒷받침하는지 설명 | 채택. 출처 목록을 단순 나열하지 않고 근거의 역할을 빠르게 볼 수 있도록 구성. 2026-05-31 배포 전 점검에서 References 구조와 맞게 제목 문구를 정리. |

## Imagegen Prompt Summary

| 파일 | Prompt Summary | Review Notes |
|---|---|---|
| `figures/imagegen/shadow_ai_calm_silo_night_v11_clean.png` | 밤의 집에서 만들어진 개인 AI 산출물이 차분한 흐름으로 회사 내부 silo에 닿고, 일부 AX 성공이 hidden effort에 기대는 hero | 기사형 진입점으로 사용. 회사가 이미 DX를 이뤘더라도 AX-native 운영은 silo와 handoff 문제를 남기며, 이 간극이 개인의 야간 shadow effort와 burnout으로 이어진다는 점을 기존 리뷰 스타일에 맞는 절제된 수채화 톤으로 표현. |
| `figures/imagegen/shadow_ai_hidden_work_cascade.png` | 야간 사무실, 실무자, 경영진 기대, 승인 대기, 보안 체크가 겹치는 hidden work 장면 | 숨은 노동을 개인 실패가 아니라 구조적 비용으로 읽게 함. |
| `figures/imagegen/shadow_ai_governed_paths_room.png` | 세 가지 안전한 AI 사용 경로가 검토 테이블로 모이는 기업 AI 운영실 | 생성 이미지 안 텍스트를 제거한 버전을 채택. 정확한 라벨은 다음 SVG가 담당. |

## 추가 그림 가능성 점검

- 현재 본문은 imagegen hero 1개, section opener 2개, 정확한 SVG 도식 4개로 구성되어 있습니다.
- 배포용 웹진에서는 `그림 1`, `그림 4`, `그림 5`가 스크롤 리듬을 열고, `그림 2`, `그림 3`, `그림 6`, `그림 7`이 개념과 근거를 정리합니다.
- 한국어 장문 라벨은 이미지 모델에 맡기지 않고 SVG와 캡션으로 처리했습니다.
- 2026-05-31 배포 전 브라우저 점검에서 그림 2, 3, 6, 7의 SVG viewBox 밖 텍스트 overflow는 0개, 데스크톱/모바일 페이지 overflow는 0개로 확인했습니다. 확인 스크린샷은 `artifacts/final_review/verification/shadow_ai_figure_*_after_fix_nocache.png`에 저장했습니다.
- 2026-05-31 추가 재점검에서 그림 2의 화살표 표현을 다시 수정했습니다. 확인 스크린샷은 `artifacts/final_review/verification/shadow_ai_figure_2_arrow_fix.png`에 저장했습니다.
