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
    "scene.checkpoint", {"name": "before_bite_site_silver_material_tune"}
)

material = abt.dispatch(
    "material.create_principled",
    {
        "name": "Bite_Site_Dark_Silver",
        "base_color": "#3F484C",
        "roughness": 0.11,
        "metallic": 0.92,
        "specular_ior_level": 0.94,
        "coat_weight": 0.35,
    },
)
result["steps"]["material"] = material

mat = bpy.data.materials["Bite_Site_Dark_Silver"]
node = next((item for item in mat.node_tree.nodes if item.type == "BSDF_PRINCIPLED"), None)
if node is not None:
    for socket_name, value in {
        "Coat Roughness": 0.08,
        "Alpha": 1.0,
    }.items():
        socket = node.inputs.get(socket_name)
        if socket is not None:
            socket.default_value = value

for name in target_names:
    obj = bpy.data.objects[name]
    obj.data.materials.clear()
    obj.data.materials.append(mat)

result["steps"]["studio"] = abt.dispatch(
    "scene.setup_studio",
    {
        "object_names": target_names,
        "clear_generated_lights": True,
        "key_energy": 850,
        "world_color": [0.88, 0.84, 0.77],
        "world_strength": 0.5,
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
