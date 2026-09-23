# Reference Matching 3D

Use this when the user asks to repeat, match, clone, or get close to a supplied image or a visual style. The goal is not an inspired approximation; it is a front-view match first, then a web-ready 3D asset.

## Required Inputs

- If the user supplies an image, use it as the primary reference.
- If the user does not supply an image but requests a recognizable style, search for 3-6 current visual references yourself and record the URLs or local paths used.
- Use references for shape, lighting, camera, and material analysis only. Do not copy protected textures or redistribute third-party assets.

## Matching Workflow

1. Create a reference board: primary image plus optional found examples.
2. Decompose the image into silhouette, occlusion order, proportions, palette, material, camera, and crop.
3. Put the primary image into Blender as camera background or a reference plane.
4. Use orthographic camera for icon/product matches unless perspective is clearly required.
5. Block the model as large editable masses first. Do not start with many equal-radius tubes.
6. Match the 2D silhouette before adding detail:
   - center and scale;
   - sphere/central object size;
   - hand/palm masses;
   - cuff positions;
   - finger count, curve, thickness, and overlap;
   - visible negative spaces.
7. Render preview from the same camera.
8. Compare render and reference with an overlay or edge-mask report.
9. Fix the largest 1-3 mismatch categories only, then render again.
10. Do not export/finalize until the silhouette and composition are visually close.

## Hand / Soft Icon Rules

- Build palms as flattened soft blobs/ellipsoids, not cylinders.
- Fingers are tapered curved forms with different lengths and radii.
- Fingers must visibly merge into the palm; avoid detached beads unless the reference shows them.
- Use occlusion order deliberately: in front of ball, behind ball, under ball.
- Cuffs are short rounded cylinders with visible front rim and soft inner face.
- Toy/clay materials: metallic 0, roughness 0.45-0.75, small clearcoat only if the reference is glossy.

## Quality Gate

Before final response, include:

- source references used;
- primary-reference overlay or a written mismatch report;
- preview PNG path, GLB path, `.blend` path;
- triangle count;
- confirmation that unrelated scene objects are not exported;
- remaining mismatch notes, if any.

If the asset is still not close, say so and continue iterating instead of presenting it as done.
