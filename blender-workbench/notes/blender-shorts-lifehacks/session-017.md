# Session 017 - Topology / UV / Bake / Mesh Handoff

Date: 2026-06-26

## Scope

- Expanded Shorts queue from `851` to `900`.
- Main topic: topology cleanup, retopology, UV seams/packing, normals, high-to-low baking, bevel/weighted-normal shading and mesh export handoff.
- Added production lifehacks `BH-300` ... `BH-319`.
- Applied all new lifehacks in Blender checkpoint asset `blender_shorts_lifehack_lab_v16`.

## Representative Sources

- [851 Bad Topology Fix](https://www.youtube.com/shorts/a0KN6xr0Yq4)
- [853 Stop Making N-Gons](https://www.youtube.com/shorts/pOlWCFOBx6Q)
- [860 Voxel and Quad Remesh](https://www.youtube.com/shorts/DxcthXYiM6s)
- [863 High To Low Poly Normal Bake](https://www.youtube.com/shorts/cissl9LKiUY)
- [869 UV Seam Placement](https://www.youtube.com/shorts/UhJZ0fIg4KY)
- [877 Complex UV Unwrap](https://www.youtube.com/shorts/HREG5VWajVY)
- [881 Weighted Normals After Bevel](https://www.youtube.com/shorts/X3xj7BRJleY)
- [892 Fix Flipped Normals](https://www.youtube.com/shorts/lPoaeVu6g5Q)
- [900 Simplify for Better Performance](https://www.youtube.com/shorts/b-UQ6ye4jf0)

## New Lifehacks

- `BH-300`: topology cleanup needs before/after mesh proof.
- `BH-301`: n-gons and booleans need risk maps.
- `BH-302`: automated retopo is only draft topology until QA.
- `BH-303`: sculpt remesh needs resolution budgets.
- `BH-304`: high-low baking needs a cage contract.
- `BH-305`: normal details need seam-safe placement.
- `BH-306`: UV seams need intent.
- `BH-307`: UV transfer and mirror need orientation QA.
- `BH-308`: UV packing needs texel and margin proof.
- `BH-309`: UV add-ons need fallbacks.
- `BH-310`: bevel and weighted normals need a shading contract.
- `BH-311`: hard-surface topology needs edge policy.
- `BH-312`: blockouts need cleanup gates.
- `BH-313`: bevel tricks still need topology review.
- `BH-314`: normals need face-orientation proof.
- `BH-315`: edge flow is shape QA.
- `BH-316`: extrude and dissolve need manifold checks.
- `BH-317`: modifier stacks need export order.
- `BH-318`: simplification needs preservation metrics.
- `BH-319`: mesh handoff needs a full asset checklist.

## Blender Checkpoint

Asset: `blender_shorts_lifehack_lab_v16`

- Script: `blender-workbench/scripts/blender_create_shorts_lifehack_lab_v16.py`
- Preview: `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v16_preview_frame_024.png`
- Frames:
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v16_frame_001.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v16_frame_048.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v16_frame_096.png`
- GLB: `blender-workbench/artifacts/exports/blender_shorts_lifehack_lab_v16.glb`
- Site copy: `public/models/blender_shorts_lifehack_lab_v16.glb`
- Blend: `blender-workbench/artifacts/blend/blender_shorts_lifehack_lab_v16.blend`
- Reports:
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v16_validation.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v16_scene_report.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v16_scene_graph.json`

## Validation

- Status: `pass`
- Errors: `0`
- Warnings: `0`
- Triangles: `17,064`
- Exportable objects: `115`
- Exportable meshes: `114`
- Animated roots:
  - `LAB16_Bake_CageDistance_Ghost`
  - `LAB16_Root_TurntableAnimated`
  - `LAB16_Simplification_PreservationMetricSlider`
- Exact helper leaks: `0`

## Visual Review

The v16 scene reads as a topology/UV/bake QA board. The left side shows mesh cleanup, before/after topology and retopo draft checks; the center shows UV seams, checker distortion, islands, texel margin and bake cage; the right side shows bevel/weighted normals and face orientation; the lower lane shows modifier order, simplification metrics and final mesh handoff checklist. Frame `048` has expected turntable overlap, while frames `001` and `096` show the complete board.

## Next Target

Expand queue to `950` sources. Good next categories: animation polish, Grease Pencil, cloth/hair/particles, asset library workflow or web/GLB optimization.
