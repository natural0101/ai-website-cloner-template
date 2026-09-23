# Sonar Fidelity Benchmark — 2026-07-16

## Current quality level

Desktop macro-composition: 4.8/5. The nine heading landmarks align within 0–190px across a ~9.7k page, section order matches, and every reference landmark has a Sonar-owned equivalent.

Mobile macro-composition after this pass: 4.8/5. The measured oversized sections match the reference closely, the workflow now uses the same narrow-screen card-reading model, and the final CTA delta fell from +1387px to -142px.

## Top visual gaps

1. Fixed: mobile security section changed from 1188px to 673px versus 649px in the reference.
2. Fixed: mobile FAQ shelf changed from 1472px to 733px versus the 730px horizontal customer-story shelf.
3. Fixed: workflow desktop state now expands with its explanation; at 390/768 it becomes the reference-matched 313px horizontal card rail.
4. Fixed: mobile final CTA moved from Y=10335 to Y=8806 versus Y=8948.
5. Russian Unbounded headings are intentionally taller than the reference's neutral grotesk; this is protected by the user-supplied Orbitron-like type direction.
6. The reference is currently dark, while Sonar is intentionally light because the user explicitly prohibited dark colors.

## Section-specific action

- Security: keep the evidence trace but compress it to a 300px mobile instrument; remove duplicate proof chips from mobile only.
- FAQ: preserve factual disclosure content but switch mobile presentation to a one-card horizontal snap shelf.
- Workflow: keep the accepted light arched review instrument; expose active explanatory copy on desktop and use the observed fixed-width native card shelf at `<=980px`.
- Hero, product/proof/use-case/security/decision/FAQ/CTA and footer: do not structurally recompose; their measured landmarks already match.

## Mobile risks

- Fixed-height open FAQ content could clip; verify the longest answer live.
- Horizontal card shelf must not create document-level overflow.
- Compact trace cards must remain legible at 360px.

## Presentation-readiness verdict

`PASS WITH USER ACCEPTANCE PENDING`: desktop structure is strong and the two measured mobile rhythm gaps are fixed. The active goal remains open because the user has not explicitly accepted the full result.
