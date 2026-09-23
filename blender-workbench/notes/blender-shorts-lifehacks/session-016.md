# Session 016 - Rigging / Constraints / Deformation QA

Date: 2026-06-26

## Scope

- Expanded Shorts queue from `801` to `850`.
- Main topic: rigging, IK, constraints, shape keys, weight painting, corrective shapes, NLA/root motion and rig export gates.
- Added production lifehacks `BH-280` ... `BH-299`.
- Applied all new lifehacks in Blender checkpoint asset `blender_shorts_lifehack_lab_v15`.

## Representative Sources

- [801 Easy IK Rigging](https://www.youtube.com/shorts/77RvfjaWvRQ)
- [802 Shape Key Drivers](https://www.youtube.com/shorts/SAX7T69OmxE)
- [803 Wrist-Twist Constraints](https://www.youtube.com/shorts/VxkWd2qEPi8)
- [817 Corrective Elbow Shape](https://www.youtube.com/shorts/45ZX6HcmIo4)
- [823 Bake Constraints to Keyframes](https://www.youtube.com/shorts/AU1C-l8D8ow)
- [832 NLA Animation Combining](https://www.youtube.com/shorts/uxPJbwXLqJs)
- [838 Reliable Weight-Paint Transfer](https://www.youtube.com/shorts/fYvXstKmo-c)
- [846 Root Motion](https://www.youtube.com/shorts/RgcR5W752kM)

## New Lifehacks

- `BH-280`: IK chains need named target, pole, chain length and proof poses.
- `BH-281`: constraints need owner, axis, space, influence and pose-range notes.
- `BH-282`: shape-key rigs need driver maps, clamps and debug override sliders.
- `BH-283`: corrective shapes need saved problem-pose snapshots.
- `BH-284`: weight transfer needs source/target assumptions and post-transfer pose checks.
- `BH-285`: auto weights need scale, normals, loose parts and mirror-name preflight.
- `BH-286`: armature deformation needs modifier order, parenting, scale and vertex-group QA.
- `BH-287`: mechanical rigs need explicit pivots, hinge axes and rigid parented parts.
- `BH-288`: Preserve Volume is only a checkpoint; joint silhouettes still need review.
- `BH-289`: face and eye rigs need independent controls plus follow-body policies.
- `BH-290`: rig cleanup needs action, NLA, fake-user and orphan-data accounting.
- `BH-291`: constraint baking needs frame-range and export/reload tests.
- `BH-292`: NLA and root motion need root owner, transitions and foot-slide checks.
- `BH-293`: motion paths are timing QA for arcs, spacing and follow-through.
- `BH-294`: controller organization prevents animator selection mistakes.
- `BH-295`: clothing deformation needs clipping sweeps across animated poses.
- `BH-296`: symmetry work depends on origin, mirror plane and L/R naming discipline.
- `BH-297`: joining rig parts needs UV/material/vertex-group/custom-normal preservation checks.
- `BH-298`: neck/head rigs need control/deform split and isolation switches.
- `BH-299`: rig exports need control/helper/constraint/baked-animation filtering.

## Blender Checkpoint

Asset: `blender_shorts_lifehack_lab_v15`

- Script: `blender-workbench/scripts/blender_create_shorts_lifehack_lab_v15.py`
- Preview: `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v15_preview_frame_024.png`
- Frames:
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v15_frame_001.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v15_frame_048.png`
  - `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v15_frame_096.png`
- GLB: `blender-workbench/artifacts/exports/blender_shorts_lifehack_lab_v15.glb`
- Site copy: `public/models/blender_shorts_lifehack_lab_v15.glb`
- Blend: `blender-workbench/artifacts/blend/blender_shorts_lifehack_lab_v15.blend`
- Reports:
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v15_validation.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v15_scene_report.json`
  - `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v15_scene_graph.json`

## Validation

- Status: `pass`
- Errors: `0`
- Warnings: `0`
- Triangles: `26,898`
- Exportable objects: `132`
- Exportable meshes: `131`
- Animated roots:
  - `LAB15_BakeGate_Animated`
  - `LAB15_IK_Target_Control_Animated`
  - `LAB15_Root_TurntableAnimated`
  - `LAB15_RootMotion_Owner_Animated`
  - `LAB15_ShapeKeyDriver_DebugSlider`
- Exact helper leaks: `0`

## Visual Review

The v15 scene reads as a single rigging QA board with separate zones for IK/constraints, shape keys/face follow, deformation/weights, mechanical pivots and NLA/bake/export gates. Frame `001` and `096` show the board clearly; frame `048` shows intended turntable overlap, confirming the panels move together as one animated checkpoint asset.

## Next Target

Expand queue to `900` sources. A good next category is sculpt/retopology/UV cleanup or more animation polish, so the next Blender checkpoint can focus on topology and asset handoff rather than another rigging pass.
