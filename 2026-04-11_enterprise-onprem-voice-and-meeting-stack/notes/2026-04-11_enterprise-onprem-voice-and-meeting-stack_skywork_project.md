# Skywork Project Log

- Topic: `enterprise-onprem-voice-and-meeting-stack`
- Created at: `2026-04-11 23:05:21 +09:00`
- Tool: `Skywork PPT`
- Mode: `PowerPoint / Pro Mode`
- Project title: `Picovoice 기반 기업 온프레미스 음성 스택 평가`
- Project URL: `https://skywork.ai/project/2042966834316664832?from=home_query&is_new_project=false`
- Current status: `completed and exported`

## Inputs

- Template: `skywork_inputs/LGD_Template.pptx`
- Prompt: `skywork_inputs/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_prompt_v1.md`
- Uploaded report: `reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_deepresearch.md`
- Uploaded memo: `reports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_memo.md`
- Uploaded source note: `notes/2026-04-11_enterprise-onprem-voice-and-meeting-stack_sources.md`

## Notes

- NotebookLM is not part of the default flow for this run.
- The deck was submitted directly through Skywork using the LGD template.
- `PPTX` and `PDF` were downloaded after generation completed.

## Outputs

- Artifact output id: `2042970790112858112`
- Artifact id: `2042970790138912769`
- Exported PPTX:
  - `skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pptx`
- Exported PDF:
  - `skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v1.pdf`
- PPTX export task id: `2042972313603522560`
- PDF export task id: `2042972319238230016`

## Fallback Attempt

- A second lightweight retry project was also started while the first job appeared stalled:
  - `https://skywork.ai/project/2042970396484526080?from=home_query&is_new_project=false`
- This retry was not used because the first project completed successfully and produced the final export set.

## Quality Review

- Structural result:
  - export succeeded as `13` slides in both `PPTX` and `PDF`
- Strong pages:
  - slides `1`, `2`, `3`, `5`, `6`, `7`, `8`, `13` contain the intended argument structure and core claims
- Material issues found in exported deck:
  - slide `4` is effectively incomplete and only retains the section title without the expected component map content
  - slides `9` and `10` are near-empty and preserve only architecture section headings
  - slide `11` still contains template placeholder text such as `페이지 제목 / Page title`
  - slide `12` still contains template placeholder text and wording artifacts such as `오폰소스 기존선 유지`
  - several slides contain template carry-over labels like `PUBLIC`, duplicate footer tokens, or mixed Korean/English placeholder fragments
- Conclusion:
  - this export is usable as a reference draft, but it is not final-quality for distribution without a second correction pass

## Second Correction Pass (V2)

- Correction packet:
  - `skywork_inputs/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_correction_v1.md`
- Goal:
  - preserve the working narrative and LGD template
  - specifically repair slides `4`, `9`, `10`, `11`, `12`
  - remove template placeholders and wording artifacts
- Revised Skywork output:
  - output id: `2043147384591060992`
  - version: `2`
- Export task ids:
  - PDF: `2043147566686642176`
  - PPTX: `2043147877618659328`
- Exported V2 files:
  - `skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pptx`
  - `skywork_exports/2026-04-11_enterprise-onprem-voice-and-meeting-stack_skywork_v2.pdf`

## V2 Review

- Structural result:
  - export succeeded as `13` slides in both `PPTX` and `PDF`
- Corrected pages confirmed:
  - slide `4`: Picovoice component map restored as a full comparison table with Korean support and meeting-stack implications
  - slide `9`: local voice assistant architecture rendered as an actual pipeline diagram
  - slide `10`: private meeting-note pipeline rendered as a full processing flow with bottleneck ordering
  - slide `11`: NVIDIA Riva enterprise platform slide restored with scenario, constraint, and component blocks
  - slide `12`: `90-day PoC` execution board restored and prior wording artifact removed
- Placeholder check:
  - `페이지 제목`, `Page title`, `Headline`, `헤드라인`, `오폰소스` were not found in slides `4`, `9`, `10`, `11`, `12`
- Visual quality assessment:
  - the previously broken slides are now presentation-ready
  - slide `9` and slide `10` are no longer near-empty and now contain readable architecture structures
- Conclusion:
  - `v2` is the current distribution candidate
  - keep `v1` only as an audit/reference draft
