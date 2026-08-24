# Submission Assets

This folder holds jury-facing outputs generated from the verified TL-05 baseline and TL-06.5 review corrections. Drafts and render-QA intermediates belong under `tmp/`, not here.

Final approved artifacts (24 August 2026):

- `Zeta_TriageloopAI.pdf` - final 11-slide business proposal and jury narrative.
- `TriageLoop_Technical_Working_Paper_Abhishek_Das.pdf` - final 36-page technical monograph.
- `demo-storyboard.md`
- `video/TriageLoop_Prototype_Demo.mp4` - 2:05 captioned working-prototype walkthrough.
- `video/TriageLoop_Prototype_Demo_transcript.md` - accessible transcript matching the burned-in captions.
- `architecture-and-evidence-visuals.md`
- `visuals/` - export-ready operating-loop, safety, uniqueness, evidence and six working-product surface captures.
- `submission-checklist.md`
- `release-manifest.sha256` - SHA-256 integrity values for the decisive release outputs.

The approved business proposal contains 11 widescreen slides and the approved technical monograph contains 36 A4 pages. Both PDFs have been fully rendered and reviewed page-by-page; their exact SHA-256 values are recorded in `release-manifest.sha256`. Earlier draft proposal, pitch and paper exports were removed so the folder exposes one authoritative version of each final document.

The code and product verification baseline is 73 passing tests plus a successful TypeScript check and optimized production build. The TL-07 isolated, Vercel and Docker deployments pass the complete reset-to-evidence workflow without browser or page errors. The Docker restart check also preserves the five-event audit stream and newest hash exactly before deterministic reset. The verified public repository is <https://github.com/Hermes-25/TriageLoop-AI>.

The repository and bundled captioned MP4 are public. Versioned jury downloads are available from <https://github.com/Hermes-25/TriageLoop-AI/releases/tag/v1.0.0>. Team/campus identity fields, any portal-preferred alternate video host and the portal submission remain human-controlled completion gates.
