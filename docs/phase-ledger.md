# Phase Ledger

All timestamps use Asia/Kolkata (IST, UTC+05:30).

| Phase | Planned window | Launch code | State | Actual record |
|---|---|---|---|---|
| TL-00 Scope | 22 Aug 09:00-13:00 | `START TL-00 SCOPE` | Approved/complete | User launched early on 21 Aug; checkpoint recorded and subsequently approved |
| TL-01 Data | 22 Aug 14:00-23 Aug 20:00 | `START TL-01 DATA` | Approved/complete | User launched early on 21 Aug; implementation completed 21 Aug 22:10 IST and approved 22 Aug |
| TL-02 Model | 24-25 Aug | `START TL-02 MODEL` | Approved/complete | User launched and approved early on 22 Aug; implementation completed 22 Aug 05:57 IST |
| TL-03 Queue | 26 Aug | `START TL-03 QUEUE` | Approved/complete | User launched early on 22 Aug; implementation and verification completed 22 Aug 06:55 IST; approved 22 Aug |
| TL-04 Product | 27-29 Aug | `START TL-04 PRODUCT` | Amended/checkpoint ready | User launched early on 22 Aug; research, implementation and product QA completed 22 Aug 08:29 IST; TL-04.5 amendments verified |
| TL-04.5 Critique | 22 Aug | independent-review request | Complete/checkpoint ready | Review audited against the current product; accepted scientific, workload, claim and failure-state fixes implemented and verified before TL-05 |
| TL-05 Verify | 30-31 Aug | `START TL-05 VERIFY` | Complete/checkpoint ready | User launched early on 22 Aug; scientific, end-to-end, safety, security, accessibility and reproducibility evidence completed 22 Aug |
| TL-06 Package | 1-2 Sep | `START TL-06 PACKAGE` | Complete/checkpoint ready | User launched early on 22 Aug; proposal, pitch, storyboard, visuals, README and release package completed and verified 22 Aug |
| TL-06.5 Final review | 22 Aug | external Claude review request | Complete / conditional GO | Claude findings F01-F09 independently dispositioned; accepted corrections implemented; 73 tests, product visual appendix, link audit and response-interval sensitivity verified. Clean-machine Docker execution remains the first external TL-07 gate. |
| TL-07 Final | 3-4 Sep | `START TL-07 FINAL` | Public repository released / portal gates | User approved launch on 22 Aug; isolated rehearsal, 2:05 MP4, repository scrub, 73 tests, production build, Vercel deployment, public browser journey and Docker Compose build/browser/restart/persistence/reset gate pass. Public repository released at `Hermes-25/TriageLoop-AI`; identity fields, portal-preferred video link and portal submission remain external. |

Rule: a later phase does not begin from an ambiguous message. It begins when its exact launch code is received or Abhishek explicitly authorizes an equivalent instruction.
