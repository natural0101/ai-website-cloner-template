# Session 006 - 2026-06-25

Goal continuation: move from 300 to 350 Blender Shorts, keep the queue/lifehack log current, and create a fifth checkpoint test asset at the 350-source mark.

## What Changed

- Added sources `301-350` to `shorts-queue.md`.
- Added lifehacks `BH-101` through `BH-115`.
- Expanded the base into rigid-body roles, simulation baking, force fields, particles, smoke/fire/fluid domains, resolution comparison, shield FX and helper/export hygiene.

## Source Method

The batch used public YouTube Shorts search results and snippets. Strong tutorial snippets are marked `reviewed`; unavailable, teaser-like, addon-specific or weak sources stay `queued` or `metadata-reviewed`.

## Current Counters

| Counter | Value |
|---|---:|
| Target sources | ~1000 |
| Sources queued | 350 |
| Sources applied in Blender scenes/test assets | 64 |
| Lifehacks distilled | 115 |
| Next checkpoint | 400 queued sources |

## Test Asset Result

Built `blender_shorts_lifehack_lab_v5` as the 350-source checkpoint scene.

| Artifact | Path |
|---|---|
| Script | `scripts/blender_create_shorts_lifehack_lab_v5.py` |
| Preview | `artifacts/renders/blender_shorts_lifehack_lab_v5_preview_frame_024.png` |
| GLB | `artifacts/exports/blender_shorts_lifehack_lab_v5.glb` |
| Site copy | `public/models/blender_shorts_lifehack_lab_v5.glb` |
| Blend | `artifacts/blend/blender_shorts_lifehack_lab_v5.blend` |
| Scene graph | `artifacts/reports/blender_shorts_lifehack_lab_v5_scene_graph.json` |
| Validation | `artifacts/reports/blender_shorts_lifehack_lab_v5_validation.json` |
| Scene report | `artifacts/reports/blender_shorts_lifehack_lab_v5_scene_report.json` |

## Applied In V5

- rigid-body role board with active/passive/collision pieces (`BH-101`, `BH-103`);
- baked/cache frame rail (`BH-102`);
- force-field influence rings and wind/vector arrows (`BH-104`, `BH-107`);
- particle density mask field, visibility checklist and subtle dust (`BH-105`, `BH-106`, `BH-114`);
- smoke/fire/fluid domain boxes with resolution/cache indicators (`BH-108`, `BH-109`, `BH-110`, `BH-111`);
- explosion/shield effect layers separated as editable rings/debris/smoke cards (`BH-112`, `BH-113`);
- helper/export hygiene visibly excluding domains/fields/floor from GLB (`BH-115`).

## Validation

| Check | Result |
|---|---:|
| Errors | 0 |
| Warnings | 0 |
| Triangles | 18,826 |
| Exportable objects | 77 |
| Exportable meshes | 76 |
| Animated roots | 3 |
| GLB helper-name leaks | 0 |

Visual review: preview frame 024 is centered after a camera pass; the scene reads left-to-right as rigid bodies, masked particles/fields, layered shield/explosion FX, and non-export simulation domains.
