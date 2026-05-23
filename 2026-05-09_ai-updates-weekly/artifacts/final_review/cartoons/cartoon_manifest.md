# AI Tech Review Letters Week 19 Cartoon Cuts

생성일: 2026-05-13

생성 도구: `$imagegen` skill, `gpt-image-1.5`

공통 스타일: 텍스트 없는 프리미엄 과학기술 리뷰용 카툰 컷, 수채화 질감, 절제된 색감, 브랜드 로고와 읽을 수 있는 글자 없음.

## 권장 배치

| 컷 | 파일 | 권장 섹션 | 의도 |
|---|---|---|---|
| 1 | `01-agent-work-prep-cartoon-web.png` | `똑똑한 에이전트를 위한 업무 단도리: 하네스 구축` | 똑똑한 에이전트도 실제 업무에 들어가기 전 체크리스트, 권한, 검토 준비가 필요하다는 도입부 컷 |
| 2 | `02-harness-operating-layer-cartoon-web.png` | `하네스는 모델 주변의 운영 조건을 정합니다` | 모델 주변의 맥락, 도구, 기억, 권한, 검증, 승인, 되돌리기 장치를 하나의 운영층으로 보여주는 컷 |
| 3 | `03-enterprise-permission-approval-cartoon-web.png` | `회사 업무에는 권한 범위와 승인 기록이 따라옵니다` | 기업 업무에서 데이터 접근, 권한 게이트, 사람 검토, 승인, 감사 기록이 함께 작동하는 장면 |
| 4 | `04-memory-evaluation-loop-cartoon-web.png` | `장기 작업 에이전트에는 기억을 고르는 하네스가 필요합니다` | 장기 작업에서 기억 선별, 평가 기준, 재시도 루프가 필요하다는 메시지 |
| 5 | `05-connector-permission-door-cartoon-web.png` | `업무 도구를 열어주는 문: Connector와 권한 설계` | 메일, 일정, 문서 같은 업무 도구가 connector를 통해 열리지만 권한 게이트를 지나야 한다는 장면 |
| 6 | `06-developer-file-exec-delegation-cartoon-web.png` | `개발자 에이전트의 하네스는 파일/실행 권한 위임 구조로 완성됩니다` | 파일 읽기/수정과 명령 실행 권한을 개발자가 에이전트에게 위임하는 개발자 에이전트 컷 |

## 파일 구성

- 원본: `*-cartoon.png`
- 웹 삽입용 축소본: `*-cartoon-web.png`
- 한눈에 보기: `cartoon_contact_sheet.png`

## 생성 실행

```powershell
python C:\Users\angpa\.codex\skills\imagegen\scripts\image_gen.py generate-batch `
  --input .\tmp\imagegen\ai_harness_cartoon_prompts.jsonl `
  --out-dir .\2026-05-09_ai-updates-weekly\artifacts\final_review\cartoons `
  --concurrency 3 `
  --max-attempts 3 `
  --downscale-max-dim 1200
```

비고: 이미지 내부에는 한국어 라벨을 넣지 않았습니다. 본문 삽입 시 캡션과 필요하면 HTML/SVG 라벨을 별도로 얹는 방식이 안전합니다.
