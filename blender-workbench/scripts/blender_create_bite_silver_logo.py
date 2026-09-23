import json
import math
import sys

KIT_PYTHON = r"C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\python"
OUTPUT_ROOT = r"C:\Users\se-20\Documents\Codex\blender-agent-output"
SCRIPT_FONT = r"C:\Windows\Fonts\BRUSHSCI.TTF"

if KIT_PYTHON not in sys.path:
    sys.path.insert(0, KIT_PYTHON)

import bpy
import ai_blender_toolkit as abt
from ai_blender_toolkit.scene import save_blend_copy

abt.configure(output_root=OUTPUT_ROOT)

result = {
    "status": "ok",
    "steps": {},
}

target_names = []

result["steps"]["checkpoint"] = abt.dispatch(
    "scene.checkpoint", {"name": "before_bite_site_silver_logo"}
)

material = abt.dispatch(
    "material.create_principled",
    {
        "name": "Bite_Site_Dark_Silver",
        "base_color": "#657074",
        "roughness": 0.16,
        "metallic": 1.0,
        "specular_ior_level": 0.86,
        "coat_weight": 0.22,
    },
)
mat_name = material["material"]
result["steps"]["material"] = material

word = abt.dispatch(
    "typography.create_plastic_text",
    {
        "text": "Bite",
        "name": "bite_site_silver_word",
        "mode": "WORD",
        "font_path": SCRIPT_FONT,
        "size": 2.85,
        "depth": 0.24,
        "bevel": 0.055,
        "bevel_segments": 8,
        "material_names": [mat_name],
        "seed": 9,
        "upright": True,
        "convert_mesh": True,
    },
)
result["steps"]["word"] = word
target_names.extend(word["objects"])
root_name = word["root"]
root = bpy.data.objects[root_name]
root.name = "bite_site_silver_logo_Root"

accent = abt.dispatch(
    "typography.create_plastic_text",
    {
        "text": "take a",
        "name": "bite_site_silver_take_a",
        "mode": "WORD",
        "font_path": SCRIPT_FONT,
        "size": 0.45,
        "depth": 0.08,
        "bevel": 0.018,
        "bevel_segments": 5,
        "material_names": [mat_name],
        "seed": 4,
        "upright": True,
        "convert_mesh": True,
    },
)
result["steps"]["accent"] = accent
target_names.extend(accent["objects"])
for name in accent["objects"]:
    obj = bpy.data.objects[name]
    obj.parent = root
    obj.location.x -= 2.35
    obj.location.z += 0.48
    obj.rotation_euler.z = math.radians(-67)

registered = abt.dispatch(
    "typography.create_plastic_text",
    {
        "text": "®",
        "name": "bite_site_silver_registered",
        "mode": "WORD",
        "font_path": r"C:\Windows\Fonts\segoeui.ttf",
        "size": 0.22,
        "depth": 0.045,
        "bevel": 0.009,
        "bevel_segments": 4,
        "material_names": [mat_name],
        "seed": 5,
        "upright": True,
        "convert_mesh": True,
    },
)
result["steps"]["registered"] = registered
target_names.extend(registered["objects"])
for name in registered["objects"]:
    obj = bpy.data.objects[name]
    obj.parent = root
    obj.location.x += 2.28
    obj.location.z += 0.45

for obj_name in target_names:
    obj = bpy.data.objects[obj_name]
    obj["abt_role"] = "text_mesh"
    obj["abt_export"] = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.shade_smooth()
    finally:
        obj.select_set(False)

result["steps"]["studio"] = abt.dispatch(
    "scene.setup_studio",
    {
        "object_names": target_names,
        "clear_generated_lights": True,
        "key_energy": 1150,
        "world_color": [0.93, 0.87, 0.78],
        "world_strength": 0.72,
        "add_floor": False,
    },
)
result["steps"]["camera"] = abt.dispatch(
    "camera.frame",
    {
        "object_names": target_names,
        "view": "FRONT_3Q",
        "margin": 1.22,
        "lens": 64,
        "resolution": [1024, 640],
    },
)
result["steps"]["inspect"] = abt.dispatch(
    "scene.inspect",
    {
        "object_names": target_names,
        "object_limit": 50,
        "include_mesh_stats": True,
    },
)
result["steps"]["render"] = abt.dispatch(
    "render.preview",
    {
        "filepath": "renders/bite_site_silver_logo.png",
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
if result["steps"]["validation"]["status"] != "pass":
    result["status"] = "fail"
    result["reason"] = "validation failed"
else:
    result["steps"]["export"] = abt.dispatch(
        "asset.export_glb",
        {
            "filepath": "exports/bite_3d_logo.glb",
            "name": "bite_3d_logo",
            "object_names": target_names + [root.name],
            "validate": True,
            "max_triangles": 100000,
            "export_animations": False,
            "export_cameras": False,
            "export_lights": False,
        },
    )
    result["steps"]["blend"] = save_blend_copy(
        name="bite_site_silver_logo",
        filepath="blend/bite_site_silver_logo.blend",
    )

print(json.dumps(result, ensure_ascii=False, indent=2))
