# New Agent Runbook: Blender Workbench

Use this file when another agent enters the repo and needs to continue Blender work without reading the whole chat.

## Start Here

1. Read `blender-workbench/AGENT_MEMORY_PACKET/START_HERE_RU.md`.
2. Read `blender-workbench/AGENT_MEMORY_PACKET/CURRENT_WORK_RU.md`.
3. Read `blender-workbench/AGENT_MEMORY_PACKET/BLENDER_RULES_RU.md`.
4. Read `blender-workbench/AGENT_MEMORY_PACKET/NEXT_STEPS_RU.md`.
5. Read `blender-workbench/AGENT_START_HERE.md`.
6. Read `blender-workbench/HANDOFF.md`.
7. Read `blender-workbench/CURRENT_STATE.md`.
8. For reference-matching tasks, read `blender-workbench/REFERENCE_MATCHING.md` and `blender-workbench/QUALITY_GATE.md`.

Do not start by writing random `bpy` code. Pick a mode first:

- `text/design`
- `shape reconstruction`
- `organic object`
- `icon/hero object`
- `GLB export`

## What Is Packaged

- Primary reference: `blender-workbench/references/hands-sphere-primary.png`
- New-agent memory packet: `blender-workbench/AGENT_MEMORY_PACKET/`
- Blender scripts: `blender-workbench/scripts/`
- Skills and workflow snapshots:
  - `blender-workbench/skill-snapshot/`
  - `blender-workbench/shape-reconstruction-upgrade/`
  - `blender-workbench/research-feedback-upgrade/`
- Blender outputs:
  - `.blend`: `blender-workbench/artifacts/blend/`
  - GLB: `blender-workbench/artifacts/exports/`
  - PNG renders: `blender-workbench/artifacts/renders/`
  - JSON reports: `blender-workbench/artifacts/reports/`
- Site GLB copies: `public/models/`

## Requirements On The Machine

Expected local Blender:

```powershell
C:\Program Files\Blender Foundation\Blender 5.1\blender.exe
```

Expected MCP port when Blender is open and the Blender MCP panel is connected:

```text
127.0.0.1:9876
```

If MCP is not responding, scripts can still run through background Blender:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --python 'blender-workbench\scripts\<script>.py'
```

## MCP Check

```powershell
py -3.11 blender-workbench/scripts/blender_socket_call.py --type get_scene_info --params-json "{}"
```

If this fails, classify it as transport unavailable. Do not keep retrying. Use background Blender for deterministic rebuilds.

## Current Critical Truth

The lower/supporting hand is not accepted as final by the user.

Hand Patch v5 is installed in:

```text
blender-workbench/AI_Blender_Agent_Hand_Patch_v5/
```

Before any further hand work, read:

```text
blender-workbench/AI_Blender_Agent_Hand_Patch_v5/00_start/START_HERE_RU.md
blender-workbench/AI_Blender_Agent_Hand_Patch_v5/01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md
```

Current page:

```text
http://127.0.0.1:3000/bottom-hand-part
```

Current asset:

```text
bottom_hand_result_v5
```

Latest validation:

- triangles: `28324`
- errors: `0`
- warnings: `0`

Important: `bottom_hand_part_v1` technical validation passed, but visual quality was rejected. `bottom_hand_result_v3` was cleaner, `bottom_hand_result_v4` became too fan-like, and the current page now uses `bottom_hand_result_v5`. V5 is the best current candidate, but it is still not accepted as final.

Current v5 files:

```text
blender-workbench/scripts/blender_create_bottom_hand_result_v5.py
blender-workbench/artifacts/exports/bottom_hand_result_v5.glb
public/models/bottom_hand_result_v5.glb
blender-workbench/artifacts/blend/bottom_hand_result_v5.blend
blender-workbench/artifacts/renders/bottom_hand_result_v5_01_clay_front_with_guide.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_02_clay_front_hand_only.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_03_clay_front_3q.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_04_clay_side.png
blender-workbench/artifacts/renders/bottom_hand_result_v5_05_opaque_front_fixed.png
blender-workbench/artifacts/reports/bottom_hand_result_v5_scene_report.json
blender-workbench/artifacts/reports/bottom_hand_result_v5_scene_graph.json
blender-workbench/artifacts/reports/bottom_hand_result_v5_qa.json
```

Latest v5 validation:

- triangles: `28324`
- errors: `0`
- warnings: `0`

## Correct Next Step For The Rejected Hand

Do not continue endlessly moving tubes in 3D.

Current 2D target proposal:

```text
blender-workbench/artifacts/reference_masks/bottom_hand_target_v1/hand_target.json
blender-workbench/artifacts/reference_masks/bottom_hand_target_v1/hand_target_board.png
blender-workbench/artifacts/reference_masks/bottom_hand_target_v1/hand_target_overlay.png
blender-workbench/artifacts/reference_masks/bottom_hand_target_v1/hand_target_validation.json
blender-workbench/artifacts/reference_masks/bottom_hand_target_v1/landmarks.md
```

Validation:

- status: `pass`
- landmarks: `16`
- centerlines: `7`
- layers: `5`
- negative spaces: `3`
- note: full JSON Schema validation now passes after installing `jsonschema` in Python 3.11.

This target is a proposal and evidence. The user later said they do not understand technical boards and need a result. Do not force board approval unless the user explicitly asks to inspect the target; use the board internally and show visual Blender/web results.

If the next hand result is rejected, do not ask the user to debug landmarks. Use the target board internally:

1. Load `references/hands-sphere-primary.png`.
2. Re-check the lower hand landmarks:
   - outer palm cup curve;
   - four fingertip positions;
   - valleys between fingers;
   - wrist/cuff axis;
   - sphere occlusion boundary.
3. Save the target/overlay under `artifacts/renders/` or `artifacts/reference_masks/` as internal evidence.
4. Produce a visual Blender/web candidate before asking for a verdict.
5. If rebuilding, continue from `bottom_hand_result_v5` unless there is a specific reason to restart. The next useful change is fingertip readability while preserving compact palm cup, not another generic primitive hand.

## Security / Preflight

Before executing local Blender Python, run:

```powershell
$env:PYTHONIOENCODING='utf-8'
py -3.11 -c "import sys, json; from pathlib import Path; sys.path.insert(0, r'blender-workbench/research-feedback-upgrade/04_python'); import security_guard; code=Path(sys.argv[1]).read_text(encoding='utf-8'); print(json.dumps(security_guard.preflight(code), ensure_ascii=False, indent=2))" "blender-workbench/scripts/<script>.py"
```

Warnings for `pathlib` and `bpy.ops.wm.save_as_mainfile` are expected when writing inside this project. Blocks are not expected.

## Site Check

Run the app:

```powershell
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Then open the relevant route:

- sphere: `http://127.0.0.1:3000/sphere-part`
- bottom hand: `http://127.0.0.1:3000/bottom-hand-part`
- full organic icon: `http://127.0.0.1:3000/organic-icon`

Run typecheck before handing off:

```powershell
npm run typecheck
```

## Do Not Claim

Do not claim:

- "95% match";
- "production quality";
- "accepted lower hand";
- "real source from Bite site";
- "true 360 reconstruction from one image".

The current workbench is a reproducible Blender workspace, not proof that the current visual result is good.
