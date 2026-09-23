# Session 018 - Animation / Grease Pencil / Asset Library / GLB Handoff

Date: 2026-06-26

## Scope

- Expanded Shorts queue from `901` to `950`.
- Main topic: Grease Pencil and Line Art, Graph Editor polish, loop discipline, motion blur/camera cuts, Asset Browser reuse, GLB/texture export and physics scatter cleanup.
- Added production lifehacks `BH-320` ... `BH-339`.
- Applied all new lifehacks in Blender checkpoint asset `blender_shorts_lifehack_lab_v17`.

## Representative Sources

- [901 Line art to life](https://www.youtube.com/shorts/tT9u9DLmsOs)
- [903 Line Art modifier](https://www.youtube.com/shorts/h8q6NrFZS_M)
- [907 Boiling lines](https://www.youtube.com/shorts/K_epbDC_qOg)
- [920 Graph Editor smoothing](https://www.youtube.com/shorts/ySHzAL_ZYwA)
- [927 Perfect looping animations](https://www.youtube.com/shorts/Vv87FIkQU9I)
- [933 Motion blur](https://www.youtube.com/shorts/qbehV-YyQMc)
- [940 Asset Browser](https://www.youtube.com/shorts/Wn57c20CMFw)
- [944 Asset switching](https://www.youtube.com/shorts/UIRQCz0KNLk)
- [947 GLB Optimizer](https://www.youtube.com/shorts/cAWVpe-jg5Q)

## New Lifehacks

- `BH-320`: Line Art needs layer ownership.
- `BH-321`: comic outlines need thickness budgets.
- `BH-322`: Grease Pencil cleanup needs frame-range proof.
- `BH-323`: boiling lines need loop discipline.
- `BH-324`: imported sketches need source and scale notes.
- `BH-325`: glow outlines need separate emission controls.
- `BH-326`: Graph Editor polish needs F-curve evidence.
- `BH-327`: extrapolation needs endpoint policy.
- `BH-328`: procedural sway needs phase controls.
- `BH-329`: seamless loops need frame proof.
- `BH-330`: motion blur needs object policy.
- `BH-331`: camera cuts need timeline notes.
- `BH-332`: animation add-ons need manual proof.
- `BH-333`: Asset Browser needs catalog discipline.
- `BH-334`: cross-file reuse needs dependency checks.
- `BH-335`: asset switching needs realization gates.
- `BH-336`: material reuse needs duplicate cleanup.
- `BH-337`: GLB optimization needs visual regression checks.
- `BH-338`: texture export needs re-link QA.
- `BH-339`: physics scatter needs bake and cleanup policy.

## Blender Checkpoint

Asset: `blender_shorts_lifehack_lab_v17`

- Script: `blender-workbench/scripts/blender_create_shorts_lifehack_lab_v17.py`
- Preview: `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v17_preview_frame_024.png`
- Frames:
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v17_frame_001.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v17_frame_048.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v17_frame_096.png`
- GLB: `blender-workbench/artifacts/exports/blender_shorts_lifehack_lab_v17.glb`
- Site copy: `public/models/blender_shorts_lifehack_lab_v17.glb`
- Blend: `blender-workbench/artifacts/blend/blender_shorts_lifehack_lab_v17.blend`
- Reports:
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v17_validation.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v17_scene_report.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v17_scene_graph.json`

## Validation

- Status: `pass`
- Errors: `0`
- Warnings: `0`
- Triangles: `18,408`
- Exportable objects: `106`
- Exportable meshes: `105`
- Animated roots:
  - `LAB17_AssetSwitch_IndexSlider_Animated`
  - `LAB17_LoopProof_EndpointSlider`
  - `LAB17_Root_TurntableAnimated`
  - `LAB17_SwayPhase_AnimatedControl`
- Exact helper leaks: `0`

## Visual Review

The v17 scene reads as an animation and asset-reuse QA board. The left panel shows Line Art and Grease Pencil ownership/cleanup; the center panel shows Graph Editor curves, endpoint policy, sway and loop proof; the right panel shows motion blur/camera cut policy; the lower lane shows Asset Browser cataloging, cross-file dependencies, asset switching, material reuse, GLB optimization, texture re-link and scatter cleanup. Frame `048` has expected turntable overlap, while frames `001` and `096` show the full board.

## Next Target

Expand queue to `1000` sources. Good final categories: cloth/hair/particles, simulation cleanup, compositing passes, final web/GLB delivery and production hygiene.
