import json
import sys

KIT_PYTHON = r"C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\python"
OUTPUT_ROOT = r"C:\Users\se-20\Documents\Codex\blender-agent-output"

if KIT_PYTHON not in sys.path:
    sys.path.insert(0, KIT_PYTHON)

import bpy
import ai_blender_toolkit as abt
from ai_blender_toolkit.scene import save_blend_copy

abt.configure(output_root=OUTPUT_ROOT)

silver_names = [
    "bite_site_silver_word",
    "bite_site_silver_take_a",
    "bite_site_silver_registered",
    "bite_site_silver_logo_Root",
]
old_prefixes = (
    "bite_3d_logo",
    "bite_site_silver_take_a_Root",
    "bite_site_silver_registered_Root",
)

result = {"status": "ok", "steps": {}}
result["steps"]["checkpoint"] = abt.dispatch(
    "scene.checkpoint", {"name": "before_clean_bite_scene_visibility"}
)

hidden = []
for obj in bpy.context.scene.objects:
    if obj.name in silver_names:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj["abt_export"] = True
        continue

    if obj.name.startswith(old_prefixes):
        obj.hide_set(True)
        obj.hide_viewport = True
        obj.hide_render = True
        obj["abt_export"] = False
        hidden.append(obj.name)

for obj in bpy.context.scene.objects:
    obj.select_set(False)

active = bpy.data.objects.get("bite_site_silver_word")
if active is not None:
    active.select_set(True)
    bpy.context.view_layer.objects.active = active

target_names = [
    "bite_site_silver_word",
    "bite_site_silver_take_a",
    "bite_site_silver_registered",
]
result["steps"]["hidden"] = hidden
result["steps"]["inspect"] = abt.dispatch(
    "scene.inspect",
    {
        "object_names": target_names,
        "object_limit": 50,
        "include_mesh_stats": True,
    },
)
result["steps"]["studio"] = abt.dispatch(
    "scene.setup_studio",
    {
        "object_names": target_names,
        "clear_generated_lights": True,
        "key_energy": 900,
        "world_color": [0.88, 0.84, 0.77],
        "world_strength": 0.55,
        "add_floor": False,
    },
)
result["steps"]["camera"] = abt.dispatch(
    "camera.frame",
    {
        "object_names": target_names,
        "view": "FRONT_3Q",
        "margin": 1.18,
        "lens": 64,
        "resolution": [1024, 640],
    },
)
result["steps"]["render"] = abt.dispatch(
    "render.preview",
    {
        "filepath": "renders/bite_site_silver_logo_clean.png",
        "object_names": target_names,
        "resolution": [1024, 640],
        "transparent": True,
        "samples": 96,
        "engine": "BLENDER_EEVEE",
        "isolate": True,
    },
)
result["steps"]["validation"] = abt.dispatch(
    "asset.validate",
    {
        "object_names": target_names,
        "max_triangles": 100000,
        "require_materials": True,
        "strict": False,
    },
)
if result["steps"]["validation"]["status"] == "pass":
    result["steps"]["export"] = abt.dispatch(
        "asset.export_glb",
        {
            "filepath": "exports/bite_3d_logo.glb",
            "name": "bite_3d_logo",
            "object_names": silver_names,
            "validate": True,
            "max_triangles": 100000,
            "export_animations": False,
            "export_cameras": False,
            "export_lights": False,
        },
    )
    result["steps"]["blend"] = save_blend_copy(
        name="bite_site_silver_logo_clean",
        filepath="blend/bite_site_silver_logo_clean.blend",
    )
else:
    result["status"] = "fail"
    result["reason"] = "validation failed"

print(json.dumps(result, ensure_ascii=False, indent=2))
