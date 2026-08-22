# Round 2 Submission Checklist

## Required by official materials

- [x] Detailed business proposal prepared and exported to PDF; executive review remains below.
- [x] Working prototype runs from the repository instructions.
- [x] Public GitHub repository contains source, dependencies and configuration: <https://github.com/Hermes-25/TriageLoop-AI>.
- [x] README explains approach, architecture, implementation, features and execution.
- [ ] Prototype demo video is uploaded and playable without access requests.
- [x] Pitch presentation opens correctly and uses verified results only.

## Claim-control gate

- [x] Every quantitative claim says synthetic/simulation and matches the source register.
- [x] Preferred headline is 20.5% versus fixed 15-minute periodic re-triage.
- [x] Static-comparator 36.0% result is labeled with its weaker comparator; periodic-comparator response-interval sensitivity is separately quantified.
- [x] NBO failure and full-reassessment fallback are visible.
- [x] External MIMIC-IV demo check is never called ED or clinical validation.
- [x] No claim of autonomous care, staffing adequacy, achieved savings, production readiness, regulatory approval or novelty primacy.

## Repository gate

- [x] Documented Docker Compose setup builds and runs on the target Windows/WSL 2 machine.
- [x] `.env.example` contains no secret and all required settings are documented.
- [x] Generated data, raw external data, local databases, render intermediates and secrets are ignored.
- [x] 73 automated tests, TypeScript check and production build pass.
- [x] Docker Compose builds both images, passes API/UI/browser checks, and preserves an intact audit chain across restart before deterministic reset.
- [x] Repository visibility is public and its release surface has been independently verified after publication.

## Demo gate

- [x] Reset -> deterioration -> negative Slack -> explanation -> override -> audit -> evidence is visible in the working prototype.
- [x] Video text is readable at normal playback size; representative frames and the complete sequence were inspected.
- [x] No real patient data, notifications, credentials or unrelated tabs appear.
- [x] Burned-in captions and a matching transcript are included.
- [ ] Final file/link naming follows the active portal instructions.

## Final human approval

- [x] Abhishek approved the narrative, claims and visual direction through the TL-06.5 → TL-07 gate.
- [ ] Team/campus names, member details and final portal video URL are filled; repository URL is <https://github.com/Hermes-25/TriageLoop-AI>.
- [ ] Final portal fields and deadline are rechecked on Unstop immediately before submission.
