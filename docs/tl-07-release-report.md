# TL-07 Final Release Report

Date: 22 August 2026  
State: **Internal release candidate ready — external publication gates remain**

## Release-candidate result

- Isolated production API and web services were launched from the current source on ports 8100 and 3200.
- The deterministic reset → deterioration → negative Slack → NBO boundary → 3× surge → reasoned override → audit → evidence → capacity journey passed without browser-console or page errors.
- The regression assertion confirmed that the P-0009 explanation contains observed oxygen-saturation evidence and contains neither `mental confused` nor `reduced estimated urgency`.
- Python verification passes **73/73** tests.
- TypeScript verification and the optimized Next.js production build pass.
- The production Vercel jury preview is `READY` at <https://triageloop-ai.vercel.app/board>; its public reset-to-capacity browser journey passes with eight screenshots and zero console/page errors.
- Docker Desktop 4.87.0 / Engine 29.7.2 / Compose 5.4.0 passed the reference container gate: both services built and started, API health and `/board` passed, the full eight-screen browser journey passed with zero errors, five audit events plus the newest hash persisted across restart, and reset returned one intact baseline event.
- The staged public-repository surface contains 174 files, approximately 19.7 MB before compression, with no file above 9 MB.
- Generated dependencies, caches, raw external data, local databases, agent instruction files, build outputs and temporary release tooling are excluded.
- A staged-content secret-signature scan found no private-key, GitHub-token, OpenAI-token or AWS-key signature.

## Demo video

`submission/video/TriageLoop_Prototype_Demo.mp4` is a **2:05**, **1440 × 900**, **25 fps**, H.264 release candidate. It is captured from the working product and contains burned-in explanatory captions. A matching transcript is included.

The complete sequence was reviewed through a nine-frame contact sheet plus dedicated title and NBO frames. Text and clinical boundaries are readable; no real patient information, credentials, notifications or unrelated applications are visible.

## Submission artifacts

The 18-page proposal, 19-slide pitch, editable source formats, speaker notes, product screenshots, MP4, transcript and evidence artifacts are staged. SHA-256 values for the decisive outputs are recorded in `submission/release-manifest.sha256`.

## External gates

The following are deliberately not marked complete:

1. **GitHub publication:** GitHub CLI currently reports an invalid token for the configured `Hermes-25` account. Reauthentication and repository identity/visibility approval are required.
2. **Public video link:** The MP4 is prepared locally but has not been uploaded. The selected public or unlisted link must be tested without account access.
3. **Identity fields:** Team name, campus name, member details and any portal-prescribed file naming must be supplied by Abhishek.
4. **Portal submission:** The active Round-2 form, deadline, required fields and final link playback must be checked immediately before submission.

No public repository, external video upload or portal submission is claimed in this report. The public Vercel artifact is a synthetic presentation adapter, not a clinical deployment; the passed Docker path remains the technical reference implementation.
