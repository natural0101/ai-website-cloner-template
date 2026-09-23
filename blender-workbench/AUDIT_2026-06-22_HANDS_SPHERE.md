# Audit 2026-06-22: hands holding sphere

## Verdict

Current full hands+sphere result is not production quality. It is a rough web demo, not a 95% reconstruction of the reference.

## What failed visually

1. Composition scale failed in the browser: the model is too large and cropped, so errors become more obvious.
2. Hand anatomy failed: fingers read as inflated tubes, not soft stylized hands.
3. Object hierarchy was rushed: sphere, hands, cuffs and camera were not accepted separately before assembly.
4. Reference matching failed: the reference has a compact icon with two clean hands holding a centered green sphere; the current output has oversized hands and weak negative spaces.
5. Material lookdev failed: the sphere became too pale in the web viewer and the hands are overlit.
6. Side view is weak: the object only works as a front-ish hero and should not be called true 360.

## Process failure

The previous workflow tried to solve the whole object at once. That made every stage ambiguous: geometry errors looked like lighting errors, material errors looked like scale errors, and the website framing hid Blender mistakes until too late.

## Missing inputs / missing gates

- A per-part acceptance loop: sphere -> top hand -> bottom hand -> cuffs -> assembly.
- Fixed browser viewport and camera crop targets before modeling.
- Side/front/3Q review after every geometry pass.
- A small reference board for soft 3D hand icons and green clay/plastic spheres.
- A simple material calibration scene before hand assembly.
- A hard stop when the isolated part fails.

## New plan

Work by parts:

1. `green_sphere_part_v1`: single green sphere only.
2. `left_top_hand_part_v1`: upper hand only, no ball.
3. `right_bottom_hand_part_v1`: lower/support hand only.
4. `pink_cuffs_part_v1`: cuffs only.
5. Assembly only after each part is accepted.

## Current part under test

`green_sphere_part_v1`

Acceptance criteria:

- single closed smooth sphere;
- saturated green material, not pale;
- soft highlight without blown-out white patch;
- GLB under 10k triangles;
- no cameras/lights/floor/hands/cuffs in GLB.
