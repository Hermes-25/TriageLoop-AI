# TL-07 Final Release Report

Date: 22 August 2026  
State: **Public repository released — final portal gates remain**

## Release-candidate result

- Isolated production API and web services were launched from the current source on ports 8100 and 3200.
- The deterministic reset → deterioration → negative Slack → NBO boundary → 3× surge → reasoned override → audit → evidence → capacity journey passed without browser-console or page errors.
- The regression assertion confirmed that the P-0009 explanation contains observed oxygen-saturation evidence and contains neither `mental confused` nor `reduced estimated urgency`.
- Python verification passes **73/73** tests.
- TypeScript verification and the optimized Next.js production build pass.
- The production Vercel jury preview is `READY` at <https://triageloop-ai.vercel.app/board>; its public reset-to-capacity browser journey passes with eight screenshots and zero console/page errors.
- Docker Desktop 4.87.0 / Engine 29.7.2 / Compose 5.4.0 passed the reference container gate: both services built and started, API health and `/board` passed, the full eight-screen browser journey passed with zero errors, five audit events plus the newest hash persisted across restart, and reset returned one intact baseline event.
- The public repository release contains 209 curated files, approximately 21.7 MB, with no file above GitHub's standard per-file limit.
- Generated dependencies, caches, raw external data, local databases, agent instruction files, build outputs and temporary release tooling are excluded.
- A staged-content secret-signature scan found no private-key, GitHub-token, OpenAI-token or AWS-key signature.

## Demo video

`submission/video/TriageLoop_Prototype_Demo.mp4` is a **2:05**, **1440 × 900**, **25 fps**, H.264 release candidate. It is captured from the working product and contains burned-in explanatory captions. A matching transcript is included.

The complete sequence was reviewed through a nine-frame contact sheet plus dedicated title and NBO frames. Text and clinical boundaries are readable; no real patient information, credentials, notifications or unrelated applications are visible.

## Submission artifacts

The approved 11-slide business proposal, 36-page technical monograph, product screenshots, MP4, transcript and evidence artifacts are staged. They supersede the earlier proposal/pitch/paper exports; SHA-256 values for the authoritative outputs are recorded in `submission/release-manifest.sha256`.

## External gates

The following are deliberately not marked complete:

1. **Optional alternate video host:** The captioned MP4 is publicly downloadable from the `v1.0.0` GitHub release; use a public or unlisted streaming host only if the portal specifically requires or prefers one.
2. **Identity fields:** Team name, campus name, member details and any portal-prescribed file naming must be supplied by Abhishek.
3. **Portal submission:** The active Round-2 form, deadline, required fields and final link playback must be checked immediately before submission.

The public repository is <https://github.com/Hermes-25/TriageLoop-AI>. No portal submission is claimed in this report. The public Vercel artifact is a synthetic presentation adapter, not a clinical deployment; the passed Docker path remains the technical reference implementation.
