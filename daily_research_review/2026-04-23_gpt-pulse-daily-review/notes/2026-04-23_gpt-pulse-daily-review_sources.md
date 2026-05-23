# 2026-04-23 GPT Pulse Sources

## Intake Context
- Intake type: ChatGPT Pulse daily check.
- Pulse interface: `https://chatgpt.com/pulse`
- Latest visible Pulse issue label: `4월 23일`.
- Capture window: `2026-04-23 23:53` to `2026-04-24 00:00` KST.
- Workspace package: `daily_research_review/2026-04-23_gpt-pulse-daily-review/`

## Browser Capture Path
- Initial Playwright default browser access reached a Cloudflare-style waiting page and did not expose Pulse content.
- Chrome Stable `Default`, Chrome SxS `Default`, and Edge `Default` profile copies did not expose an authenticated ChatGPT session.
- Chrome Stable `Profile 1` contained an authenticated ChatGPT session.
- The successful capture path was:
  - clone `C:\Users\angpa\AppData\Local\Google\Chrome\User Data\Profile 1` into the OS temp area
  - launch Chrome with a remote debugging port using that temp profile
  - connect via Playwright CDP
  - open `https://chatgpt.com/pulse`
  - capture overview text, all visible card detail text, screenshots, and JSON metadata
- Temporary profile copies were kept under the OS temp `AI_Tech_Review` runtime area during capture and should be treated as disposable runtime artifacts.

## Captured Overview Artifacts
- Overview JSON: `sources/2026-04-23_gpt-pulse-daily-review_overview_capture.json`
- Overview text: `sources/2026-04-23_gpt-pulse-daily-review_overview_text.txt`
- Overview screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_overview.png`
- ChatGPT home/session probe JSON: `sources/2026-04-23_gpt-pulse-daily-review_access_probe.json`
- ChatGPT home/session probe text: `sources/2026-04-23_gpt-pulse-daily-review_access_probe.txt`
- ChatGPT home/session probe screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_chatgpt_home_probe.png`

## Captured Pulse Detail Cards
- `2026년 4-5월 포용교육 마이크로 그랜트 모집`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_inclusive_micro_grants.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_inclusive_micro_grants.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_inclusive_micro_grants.png`
- `포용교육 단편 영상 콘티 제안`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_inclusive_video_storyboard.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_inclusive_video_storyboard.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_inclusive_video_storyboard.png`
- `OIDC ID 토큰과 CI Job 토큰 수명 관리`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_gitlab_oidc_ci_job_token.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_gitlab_oidc_ci_job_token.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_gitlab_oidc_ci_job_token.png`
- `OTel 기반 에이전트 추적성 청사진`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_otel_agent_traceability.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_otel_agent_traceability.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_otel_agent_traceability.png`
- `미군, 오만만서 이란 화물선 'Touska' 나포`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_touska_seizure.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_touska_seizure.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_touska_seizure.png`
- `미국, 이라크 달러 현금 수송 중단`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_iraq_dollar_cash_shipments.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_iraq_dollar_cash_shipments.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_iraq_dollar_cash_shipments.png`
- `온디바이스 STT/TTS 10분 미니 벤치마크`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_ondevice_stt_tts_benchmark.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_ondevice_stt_tts_benchmark.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_ondevice_stt_tts_benchmark.png`
- `SID 전 10일 주목 신호 - LGD/Fraunhofer`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_sid_lgd_fraunhofer_signals.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_sid_lgd_fraunhofer_signals.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_sid_lgd_fraunhofer_signals.png`
- `LG디스플레이 OLED 투자, 연구개발에 미칠 영향`
  - Text: `sources/2026-04-23_gpt-pulse-daily-review_detail_lg_display_oled_investment.txt`
  - JSON: `sources/2026-04-23_gpt-pulse-daily-review_detail_lg_display_oled_investment.json`
  - Screenshot: `artifacts/2026-04-23_gpt-pulse-daily-review_detail_lg_display_oled_investment.png`
- Detail capture summary: `sources/2026-04-23_gpt-pulse-daily-review_detail_capture_summary.json`

## Source Extraction Note
- Pulse detail views displayed source names such as `GitLab Docs`, `Reuters`, `Fraunhofer IPMS`, and `Seoul Economic Daily`, but the captured DOM did not expose clickable external source URLs for those source labels.
- Therefore, this package treats Pulse card text as an intake signal, not as verified evidence.
- External links in the overview report are verification paths added by Codex after the Pulse capture, not direct Pulse-exported links.

## Raw Pulse Topic Set
- Education and inclusion:
  - `2026년 4-5월 포용교육 마이크로 그랜트 모집`
  - `포용교육 단편 영상 콘티 제안`
- MLOps / agent governance:
  - `OIDC ID 토큰과 CI Job 토큰 수명 관리`
  - `OTel 기반 에이전트 추적성 청사진`
- Geopolitical risk:
  - `미군, 오만만서 이란 화물선 'Touska' 나포`
  - `미국, 이라크 달러 현금 수송 중단`
- Hands-on technical experiments and display/OLED signals:
  - `온디바이스 STT/TTS 10분 미니 벤치마크`
  - `SID 전 10일 주목 신호 - LGD/Fraunhofer`
  - `LG디스플레이 OLED 투자, 연구개발에 미칠 영향`
