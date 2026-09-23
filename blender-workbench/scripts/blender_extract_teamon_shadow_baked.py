from __future__ import annotations

from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_shadow_hand_baked_world.blend"

source_meshes = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH"
    and obj.name.startswith("TEAMON_SH_")
    and not obj.hide_render
]
if len(source_meshes) != 24:
    raise RuntimeError(f"Expected 24 visible Shadow Hand meshes, received {len(source_meshes)}")

baked_collection = bpy.data.collections.new("TEAMON_ShadowBaked")
bpy.context.scene.collection.children.link(baked_collection)
baked_root = bpy.data.objects.new("TEAMON_ShadowBakedRoot", None)
baked_collection.objects.link(baked_root)

baked_objects = []
for source in source_meshes:
    baked = source.copy()
    baked.data = source.data.copy()
    baked.animation_data_clear()
    baked.name = f"TEAMON_V21_{source.name.removeprefix('TEAMON_SH_')}"
    baked_collection.objects.link(baked)
    baked.parent = baked_root
    baked.matrix_world = source.matrix_world.copy()
    baked["mjcf_body"] = source.get("mjcf_body", "")
    baked["shadow_index_distal"] = source.get("mjcf_body") == "rh_ffdistal"
    baked_objects.append(baked)

for obj in list(bpy.data.objects):
    if obj not in baked_objects and obj != baked_root:
        bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection != baked_collection:
        bpy.data.collections.remove(collection)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_PATH))
print(f"Saved {len(baked_objects)} baked Shadow Hand meshes to {OUTPUT_PATH}")
