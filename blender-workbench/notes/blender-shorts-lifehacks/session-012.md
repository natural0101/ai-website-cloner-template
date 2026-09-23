# Session 012 - 2026-06-26

Goal continuation: move from 600 to 650 Blender Shorts, keep the queue/lifehack log current, and create an eleventh checkpoint test asset focused on compositing, camera tracking, VFX integration, Grease Pencil and toon/line-art QA.

## What Changed

- Added sources `601-650` to `shorts-queue.md`.
- Added lifehacks `BH-204` through `BH-220`.
- Expanded the base into viewport/final compositor parity, glow threshold control, camera-shake limits, tracking solve QA, tracking shortcut assumptions, keying matte/spill cleanup, shadow-catcher contact proof, camera-follow framing QA, Grease Pencil layer discipline, line-art scope/thickness QA, line-boil noise limits, mixed 2D/3D shared space, Grease Pencil rig pose tests, toon pass contracts, fake-reflection link logic, 2D-to-3D cleanup and VFX pass accounting.

## Source Method

The batch used public YouTube Shorts search results and snippets. Strong tutorial snippets are marked `reviewed`; vague, unavailable, addon-specific or broad inspiration/VFX breakdown sources stay `metadata-reviewed` or `queued`.

## Current Counters

| Counter | Value |
|---|---:|
| Target sources | ~1000 |
| Sources queued | 650 |
| Sources applied in Blender scenes/test assets | 169 |
| Lifehacks distilled | 220 |
| Next checkpoint | 700 queued sources |

## Test Asset Result

Built `blender_shorts_lifehack_lab_v11` as the 650-source checkpoint scene.

| Artifact | Path |
|---|---|
| Script | `blender-workbench/scripts/blender_create_shorts_lifehack_lab_v11.py` |
| Preview | `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v11_preview_frame_024.png` |
| Frames | `blender-workbench/artifacts/renders/blender_shorts_lifehack_lab_v11_frame_001.png`, `..._frame_048.png`, `..._frame_096.png` |
| GLB | `blender-workbench/artifacts/exports/blender_shorts_lifehack_lab_v11.glb` |
| Site copy | `public/models/blender_shorts_lifehack_lab_v11.glb` |
| Blend | `blender-workbench/artifacts/blend/blender_shorts_lifehack_lab_v11.blend` |
| Validation | `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v11_validation.json` |
| Scene report | `blender-workbench/artifacts/reports/blender_shorts_lifehack_lab_v11_scene_report.json` |

## Applied In V11

- viewport/final compositor parity board (`BH-204`);
- glow threshold and clipping control board (`BH-205`);
- camera-shake amplitude/frequency guard (`BH-206`);
- tracking solve QA board with markers, solve error and ground plane (`BH-207`);
- shortcut/external-tracking assumptions board (`BH-208`);
- keying matte/spill cleanup board (`BH-209`);
- shadow catcher contact/alpha board (`BH-210`);
- camera-follow framing/focal-length board (`BH-211`);
- Grease Pencil layer/material/timing discipline board (`BH-212`);
- Line Art scope/thickness/depth board (`BH-213`);
- line-boil noise limits board (`BH-214`);
- mixed 2D/3D shared-space board (`BH-215`);
- Grease Pencil rig pose-test board (`BH-216`);
- toon material/outline/color-grade pass contract board (`BH-217`);
- fake reflection link/offset/opacity board (`BH-218`);
- mesh-to-GP / 2D-to-3D cleanup board (`BH-219`);
- VFX shot pass-accounting board (`BH-220`).

## Validation

| Check | Result |
|---|---:|
| Status | pass |
| Errors | 0 |
| Warnings | 0 |
| Triangles | 8,520 |
| Exportable objects | 84 |
| Exportable meshes | 72 |
| Animated roots | 5 |
| Exact GLB helper leaks | 0 |

Visual review: the preview separates comp/tracking/key/shadow controls, Grease Pencil/line art/toon controls, and VFX pass accounting. Studio lights, camera, labels and floor are render helpers and are excluded from GLB export.
