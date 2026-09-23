# TeamON Teddy Bear V1 — Reference Research

Date: 2026-07-20

## Scope

Create an original seated plush teddy for the TeamON Master home hero. References define general teddy anatomy, seated balance, soft-material cues and studio lighting only. No third-party mesh or texture is used.

## Stored References

- `references/teamon-teddy-reference-light-sitting.jpg` — topology/part transition reference from [TurboSquid 1925401](https://www.turbosquid.com/pt_br/3d-models/3d-teddy-bear-light-color-sitting-1925401).
- `references/teamon-teddy-reference-classic-plush.jpg` — front silhouette and fur-volume reference from [TurboSquid 1342980](https://www.turbosquid.com/3d-models/3d-model-teddy-bear-plush-1342980).
- `references/teamon-teddy-reference-studio-pbr.jpg` — 3/4 pose, fabric and contact-shadow reference from [TurboSquid 2378236](https://www.turbosquid.com/3d-models/3d-model-teddy-bear-toy-brown-2378236).
- `references/teamon-home-teddy-placement-reference.png` — user-provided current page and target placement.

## Breakdown

- Silhouette: large round head, two clear ears, short pear torso, two short arms, broad thighs and large forward paw pads.
- Proportions: head about 38% of full seated height; total silhouette slightly wider than tall; feet create a stable triangular base.
- Occlusion: feet in front of thighs; arms in front of torso; muzzle, nose, eyes and inner ears in front of head.
- Face: small glossy button eyes with separate pupils/highlights; broad pale muzzle; compact dark nose; stitched smile.
- Material: export-safe PBR with high roughness, subtle woven bump and soft studio lighting; no hair-particle dependency.
- Camera: near-front 3/4 product view, weak perspective, full ears and feet visible.
- TeamON adaptation: porcelain base, mint inner ears/paw pads, deep green face details, chartreuse chest badge and one coral stitch.

## Acceptance Criteria

- Recognizable as a seated plush teddy at 180 px tall.
- Reads as one coherent character, not assembled primitives.
- Head is a separate transform node and pupils are separately named.
- Cursor response remains attentive rather than uncanny: yaw ±14°, pitch ±8°, pupil shift subtle.
- Under 60k triangles preferred; GLB under 3 MB preferred.
- Front, 3/4 and side evidence plus a transparent fallback render are required.
