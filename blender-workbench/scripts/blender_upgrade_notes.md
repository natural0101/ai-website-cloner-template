# Blender Agent Upgrade

## Installed Paths

- Toolkit: `C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit`
- Codex skill: `C:\Users\se-20\.codex\skills\blender-web-3d`
- Blender output root: `C:\Users\se-20\Documents\Codex\blender-agent-output`
- First MCP bootstrap: `C:\Users\se-20\Documents\Codex\2026-06-21\new-chat\outputs\blender_mcp_bootstrap.py`

## What The Kit Adds

- Semantic Blender actions instead of improvised raw `bpy` scripts.
- Inspect/checkpoint/render/validate/export workflow.
- Plastic/clay text workflow.
- Soft shapes: rounded boxes, blobs, tubes, spheres.
- Studio lighting, camera framing, PNG previews, GLB export and `.blend` saves.

## First Connection Test

After Blender MCP is connected, run the bootstrap code through the MCP tool that executes Python inside Blender.

Expected result:

- `ai_blender_toolkit` imports successfully.
- `output_root` is configured.
- `scene.inspect` returns JSON with `status`.

Actual status on 2026-06-22:

- Blender MCP socket answered on `127.0.0.1:9876`.
- `ai_blender_toolkit` imported inside Blender.
- `scene.inspect` returned Blender `5.1.1`.
- The initial default scene was checkpointed before asset creation.

## Created Bite 3D Asset

- PNG preview: `C:\Users\se-20\Documents\Codex\blender-agent-output\renders\bite_3d_logo.png`
- GLB export: `C:\Users\se-20\Documents\Codex\blender-agent-output\exports\bite_3d_logo.glb`
- Blend copy: `C:\Users\se-20\Documents\Codex\blender-agent-output\blend\bite_3d_logo.blend`
- Checkpoint: `C:\Users\se-20\Documents\Codex\blender-agent-output\checkpoints\20260622T043456Z_before_bite_3d_logo.blend`
- Web copy: `C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\public\models\bite_3d_logo.glb`
- Validation: pass, 5176 triangles, 0 errors, 0 warnings.

## Site Integration

- Installed `three` and `@types/three`.
- Added `src/components/BiteModelViewer.tsx`.
- Inserted the GLB canvas into the Bite hero.
- Desktop and mobile browser checks passed with visible nonblank model pixels and no console errors.

## Design Upgrade V2

- Installed from: `C:\Users\se-20\Downloads\AI_Blender_Agent_Kit_v2_design_upgrade.zip`
- Installed folder: `C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\design_upgrade`
- Skill copy: `C:\Users\se-20\.codex\skills\blender-web-3d\design_upgrade`
- Key API: `design_upgrade\03_blender_tools\design_tools.py`
- Key rule: chrome/silver requires reflection cards or web environment/reflections; gray material is not silver.
- Codex skill now routes chrome/silver, brushed silver, liquid metal, website hero and reference tasks through Design Upgrade recipes and visual checklist.
- Validation: `tests\validate_package.py` pass; design examples syntax parse pass; Blender MCP probe pass.

## Next Project Step

For the Bite site, build a new editable Blender hero instead of relying on the downloaded JPG:

- beige studio background;
- glossy snack bars and package-like rounded boxes;
- soft colored spheres, blobs and ribbon/tube accents;
- rocket/globe/microscope-inspired decorative shapes;
- large rounded 3D wordmark;
- render desktop/mobile WEBP/PNG;
- export GLB if interactive Three.js hero is wanted.
