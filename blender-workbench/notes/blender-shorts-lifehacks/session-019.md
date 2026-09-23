# Session 019 - Cloth / Hair / Simulation / Compositing / GLTF Handoff

Date: 2026-06-26

## Scope

- Expanded Shorts queue from `951` to `1000`.
- Main topic: cloth pinning/collision/freeze policy, hair grooming and dynamics cache, smoke/fluid/particle production gates, render passes/compositing, final GLTF/game/texture/deform handoff.
- Added production lifehacks `BH-340` ... `BH-359`.
- Applied all new lifehacks in Blender checkpoint asset `blender_shorts_lifehack_lab_v18`.
- Target `1000` sources reached. `metadata-reviewed` entries stay flagged for future full visual revisit when deeper review is needed.

## Representative Sources

- [951 Pin Cloth FAST & EASY](https://www.youtube.com/shorts/EsIdAdj-sXw)
- [953 Cloth flag wind setup](https://www.youtube.com/shorts/Hmfa2J0Y6Wg)
- [961 Smooth Blender hair](https://www.youtube.com/shorts/B0erUgje7VQ)
- [965 Hair dynamics](https://www.youtube.com/shorts/0nw7W2AcUXQ)
- [971 Smoke simulation stability](https://www.youtube.com/shorts/o099XQW9p34)
- [974 Fluid setup](https://www.youtube.com/shorts/MHWQe9YdshM)
- [979 Render pass lighting](https://www.youtube.com/shorts/hcE389sUg2U)
- [982 Multiple view layers](https://www.youtube.com/shorts/0qGqEyaYK3I)
- [989 GLTF export](https://www.youtube.com/shorts/FJHVhRpOm1k)
- [1000 Testing Blender hair dynamics branch](https://www.youtube.com/shorts/YssKo8aQHjc)

## New Lifehacks

- `BH-340`: cloth pinning needs vertex-group proof.
- `BH-341`: cloth collision needs pose sweeps.
- `BH-342`: soft furnishing sims need final freeze policy.
- `BH-343`: hair needs strand budget discipline.
- `BH-344`: hair grooming needs fallbacks.
- `BH-345`: hair dynamics need versioned cache proof.
- `BH-346`: smoke sims need memory budgets.
- `BH-347`: fluid sims need domain/flow naming.
- `BH-348`: particles need seed and density gates.
- `BH-349`: render passes need pass accounting.
- `BH-350`: view layers need collection contracts.
- `BH-351`: depth/position passes need space notes.
- `BH-352`: compositor blur needs vector proof.
- `BH-353`: shadow catchers need destination proof.
- `BH-354`: cinematic composites need before/after reviews.
- `BH-355`: GLTF export needs transform and material checks.
- `BH-356`: vertex animation export needs viewer tests.
- `BH-357`: game collision exports need naming discipline.
- `BH-358`: texture bake/export needs relink QA.
- `BH-359`: destructive cleanup needs deform proof.

## Blender Checkpoint

Asset: `blender_shorts_lifehack_lab_v18`

- Script: `blender-workbench/scripts/blender_create_shorts_lifehack_lab_v18.py`
- Preview: `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v18_preview_frame_024.png`
- Frames:
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v18_frame_001.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v18_frame_048.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v18_frame_096.png`
- GLB: `blender-workbench/artifacts/exports/blender_shorts_lifehack_lab_v18.glb`
- Site copy: `public/models/blender_shorts_lifehack_lab_v18.glb`
- Blend: `blender-workbench/artifacts/blend/blender_shorts_lifehack_lab_v18.blend`
- Reports:
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v18_validation.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v18_scene_report.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v18_scene_graph.json`

## Validation

- Status: `pass`
- Errors: `0`
- Warnings: `0`
- Triangles: `19,086`
- Exportable objects: `116`
- Exportable meshes: `115`
- Animated roots:
  - `LAB18_ClothCache_FrameSlider_Animated`
  - `LAB18_HairWind_Control_Animated`
  - `LAB18_ParticleSeed_Slider_Animated`
  - `LAB18_PassPreview_Toggle_Animated`
  - `LAB18_Root_TurntableAnimated`
  - `LAB18_VertexAnim_ViewerScrubber_Animated`
- Exact helper leaks: `0`

## Visual Review

The v18 scene reads as a final production-hygiene board. The left zone shows cloth pin groups, collision sweeps, frozen soft-furnishing frames, strand budgets, grooming fallbacks and versioned hair cache controls. The center zone shows smoke memory, fluid domain/flow naming and particle seed/density gates. The right zone shows render pass accounting, view-layer contracts, depth/position space notes, vector blur, shadow catcher and before/after composite proof. The lower export lane shows GLTF transform/material checks, vertex animation viewer testing, collision naming, texture relink QA and destructive cleanup/deform proof.

Frames `024`, `048` and `096` were visually checked. The final orthographic camera keeps the full board inside frame while preserving the turntable motion.

## Completion Note

The quantitative target is reached: `1000` sources in queue, `359` formulated lifehacks and `308` applied lifehacks across Blender scenes/test-assets. The honest-status rule remains active: sources marked `metadata-reviewed` are useful production hints but should be revisited for full visual review when exact technique reproduction matters.
