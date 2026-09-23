# YouTube Character Lesson Notes: J-nbY8B2oa4

Source: https://www.youtube.com/watch?v=J-nbY8B2oa4

Title found via search/thumbnail context: "Blender Character - Step-by-Step Guide" / "Персонаж за 10 минут. Пошаговый рецепт".

YouTube transcript/video download status: `yt-dlp` failed repeatedly with connection reset, so this pass uses the available YouTube thumbnail as the primary visual reference:

- `docs/research/youtube-lessons/character-J-nbY8B2oa4/maxresdefault.jpg`
- `blender-workbench/references/low_poly_character_youtube_J-nbY8B2oa4.jpg`

## Target

Create a low-poly faceted humanoid mannequin, not a smooth organic sculpt.

## Visual Breakdown

- Pose: crouching/squatting character with wide legs and bent arms.
- Style: low-poly grey mannequin, visible polygon facets, no facial features.
- Body: simplified head, chest, abdomen/pelvis, shoulders, arms, hands, thighs, shins, feet.
- Proportions: large faceted head, angular torso, long bent limbs, wide stance.
- Materials: light/mid/dark grey clay-plastic material with flat shading and hard polygon faces.
- Camera: hero 3/4 view plus front and side QA renders.
- Export goal: editable `.blend`, web-safe GLB, PNG preview, scene graph, structural QA, validation report.

## Modeling Recipe For Agent

1. Use semantic primitives, not one fused blob.
2. Use faceted ellipsoids for head, torso, pelvis, joints and hands.
3. Use tapered low-poly frustums for upper/lower arms and legs.
4. Keep elbows, knees, wrists, ankles and shoulders visibly connected.
5. Preserve flat shading; do not smooth the silhouette into a realistic human.
6. Add non-export lights/camera/floor/reference background only for preview.
7. Validate exportable objects only; exclude floor, lights, camera and reference.

Target mode: `HYBRID_HERO`, because the thumbnail gives a front/3-quarter character reference, while hidden/back details are inferred.
