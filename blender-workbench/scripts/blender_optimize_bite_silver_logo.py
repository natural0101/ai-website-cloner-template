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

target_names = [
    "bite_site_silver_word",
    "bite_site_silver_take_a",
    "bite_site_silver_registered",
]
root_name = "bite_site_silver_logo_Root"

result = {"status": "ok", "steps": {}}
result["steps"]["checkpoint"] = abt.dispatch(
    "scene.checkpoint", {"name": "before_bite_site_silver_decimate"}
)

ratios = {
    "bite_site_silver_word": 0.42,
    "bite_site_silver_take_a": 0.32,
    "bite_site_silver_registered": 0.28,
}
decimated = []

for name in target_names:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing object: {name}")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("ABT_Web_Decimate", "DECIMATE")
    modifier.ratio = ratios[name]
    modifier.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.object.shade_smooth()
    decimated.append({"object": name, "ratio": ratios[name]})

result["steps"]["decimate"] = decimated
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
        "key_energy": 1250,
        "world_color": [0.93, 0.87, 0.78],
        "world_strength": 0.82,
        "add_floor": False,
    },
)
result["steps"]["camera"] = abt.dispatch(
    "camera.frame",
    {
        "object_names": target_names,
        "view": "FRONT_3Q",
        "margin": 1.2,
        "lens": 64,
        "resolution": [1024, 640],
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
            "object_names": target_names + [root_name],
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
