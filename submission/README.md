# Submission Assets

This folder holds jury-facing outputs generated from the verified TL-05 baseline and TL-06.5 review corrections. Drafts and render-QA intermediates belong under `tmp/`, not here.

Prepared TL-06 artifacts:

- `TriageLoop_Detailed_Business_Proposal.docx`
- `TriageLoop_Detailed_Business_Proposal.pdf`
- `TriageLoop_Accenture_Round2_Pitch.pptx`
- `TriageLoop_Accenture_Round2_Pitch.pdf`
- `demo-storyboard.md`
- `video/TriageLoop_Prototype_Demo.mp4` - 2:05 captioned working-prototype walkthrough.
- `video/TriageLoop_Prototype_Demo_transcript.md` - accessible transcript matching the burned-in captions.
- `pitch-speaker-notes.md`
- `architecture-and-evidence-visuals.md`
- `visuals/` - export-ready operating-loop, safety, uniqueness, evidence and six working-product surface captures.
- `submission-checklist.md`
- `release-manifest.sha256` - SHA-256 integrity values for the decisive release outputs.

The proposal is 18 pages, including a six-screen working-product evidence appendix. The pitch contains 16 core slides and three appendices, with source-bearing speaker notes. Both PDFs have been fully rendered and reviewed page-by-page. The proposal accessibility audit reports zero findings.

The code and product verification baseline is 73 passing tests plus a successful TypeScript check and optimized production build. The TL-07 isolated, Vercel and Docker deployments pass the complete reset-to-evidence workflow without browser or page errors. The Docker restart check also preserves the five-event audit stream and newest hash exactly before deterministic reset. Repository publication remains gated only by explicit GitHub identity/visibility approval and authentication.

Repository and video URLs remain explicit placeholders until Abhishek authorizes external publication/upload. Do not publish from this folder without that approval.
