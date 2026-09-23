"""Read-only inspection of the current comforting-cat face hierarchy."""

from __future__ import annotations

import json

import bpy


PREFIXES = (
    "Cat_Eye_",
    "Cat_Iris_",
    "Cat_Pupil_",
    "Cat_EyeHighlight_",
    "Cat_Eyebrow_",
    "Cat_Muzzle_",
    "Cat_Whisker_",
)
EXACT = {
    "Cat_Head",
    "Cat_Head_Mesh",
    "Cat_Nose",
    "Cat_MouthStem",
    "Cat_Mouth_L",
    "Cat_Mouth_R",
}


def vec(values: object) -> list[float]:
    return [round(float(value), 6) for value in values]


objects = []
for obj in sorted(bpy.data.objects, key=lambda item: item.name):
    if obj.name not in EXACT and not obj.name.startswith(PREFIXES):
        continue
    objects.append(
        {
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "location_local": vec(obj.location),
            "location_world": vec(obj.matrix_world.translation),
            "scale_local": vec(obj.scale),
            "dimensions_world": vec(obj.dimensions),
            "rotation_local": vec(obj.rotation_euler),
        }
    )

report = {
    "blend": bpy.data.filepath,
    "scene": bpy.context.scene.name,
    "objects": objects,
}
print("COMFORTING_CAT_V5_FACE_INSPECTION=" + json.dumps(report, ensure_ascii=False))
