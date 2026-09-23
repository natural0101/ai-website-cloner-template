# Research Log: Stylized Hand Recovery

Date: 2026-06-23

## Goal

Improve the lower/supporting hand workflow for the hands-holding-sphere icon.
The user does not want technical landmark approval; the agent must own the
visual critique and show only concrete results plus evidence.

## External Learning Attempts

YouTube direct search through `yt-dlp` timed out during this run. Transcript
fetching through `youtube_transcript_api` was attempted later, but the request
was interrupted when the environment switched sandbox mode. Useful learning was
therefore extracted from available web/source references and sub-agent review.

Useful sources to revisit:

- Blender Artists, "Modeling Hands": https://blenderartists.org/t/modeling-hands/573937
- Reddit r/blenderhelp, sculpting hands tips: https://www.reddit.com/r/blenderhelp/comments/142ngwo/does_anyone_have_tips_on_sculping_hands_that/
- YouTube, "Sculpting a Stylized Hand - 1 Minute Guide": https://www.youtube.com/watch?v=irqZ0YSc4-8
- YouTube, "Blender 2.9 Tutorial - How to Sculpt a Stylized Hand!": https://www.youtube.com/watch?v=FQlh08yjfAE
- YouTube, "Sculpting Hands Is SOO EASY | Blender Tutorial": https://www.youtube.com/watch?v=5RFhA0PG0XE
- YouTube, "How to 3D Model a Stylized Hand": https://www.youtube.com/watch?v=zVybsydplxU

## Extracted Rules

1. Start from a wide cupped palm mass. Fingers are secondary and must grow from
   that mass, not float as separate tubes.
2. Use four unequal fingers with different root heights, curvature and radii.
   Keep valleys readable, but avoid anatomical noise.
3. Thumb is a separate thenar/web mass plus a shorter curved tube. It is not a
   fifth parallel finger.
4. Finger roots must overlap the palm/root pad before any smoothing or union.
5. Wrist should taper from cuff to palm and enter under the palm mass.
6. Cuff remains a separate soft volume; wrist must visibly enter it.
7. Check front, 3/4 and side. A good front silhouette is not enough if the side
   view is flat or reads as disconnected parts.
8. Materials and lighting must not be used to hide a bad silhouette.

## Applied During This Run

### `bottom_hand_result_v4`

Changed the lower hand from hardcoded v3 coordinates to target-driven
centerlines/radii from:

`artifacts/reference_masks/bottom_hand_target_v1/hand_target.json`

Result:

- Technical validation passed.
- Schema validation for the target now passes after installing `jsonschema`.
- Visual result over-followed the target centerlines and became too fan-like.
- Structural QA showed wrist/cuff contact was only `NEAR`, not `OVERLAP`.

### `bottom_hand_result_v5`

Kept target fingertip landmarks but tucked hidden roots into a compact palm cup.
Also widened palm/root masses and fixed wrist/cuff contact.

Result:

- GLB: `public/models/bottom_hand_result_v5.glb`
- Blend: `artifacts/blend/bottom_hand_result_v5.blend`
- Main preview: `artifacts/renders/bottom_hand_result_v5_05_opaque_front_fixed.png`
- Technical validation: 28,324 triangles, 0 errors, 0 warnings.
- Structural QA: wrist/cuff now `OVERLAP`.
- `/bottom-hand-part` now loads v5.

## Honest Current Assessment

v5 is the best current candidate from this run, but it is still not a final
95% reference match. The palm cup is more cohesive and structurally cleaner than
v3/v4, but several fingertips are partially swallowed by the palm mass and the
lower hand does not yet fully match the compact reference pose.

## Next Local Fix

Do not restart. Continue from `bottom_hand_result_v5`.

One dominant defect to fix next:

- improve fingertip readability while preserving compact palm cup.

Suggested change:

- keep palm/wrist/cuff from v5;
- move the visible finger midpoints slightly forward/down in front view;
- reduce palm root-pad coverage over the index/middle/ring tips;
- render front, 3/4, side and opaque-front again;
- only then run mask/landmark comparison.

