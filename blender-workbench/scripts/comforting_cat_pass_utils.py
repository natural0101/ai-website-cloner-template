"""Shared reversible output, render, export, and QA utilities for cat passes."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


def preserve_copy(
    obj: bpy.types.Object,
    collection_name: str,
    suffix: str,
    reason: str,
) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections[collection_name].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_{suffix}"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = reason
    return copy.name


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def finalize_pass(
    *,
    asset: str,
    root: bpy.types.Object,
    scene: bpy.types.Scene,
    final_blend: Path,
    glb_path: Path,
    render_dir: Path,
    report_dir: Path,
    scene_qa_path: Path,
    report: dict[str, object],
) -> dict[str, object]:
    camera = bpy.data.objects["CAT_RenderCamera"]
    views = [
        ("02_material_front", (0.0, -8.6, 3.08), (0.0, 0.0, 1.88), 4.20),
        ("03_front_3q", (4.0, -7.4, 3.35), (0.0, 0.02, 1.84), 4.30),
        ("04_side", (8.4, -0.35, 3.08), (0.0, 0.08, 1.82), 4.30),
        ("05_back", (0.0, 8.4, 3.08), (0.0, 0.12, 1.82), 4.30),
    ]
    for suffix, location, target, scale in views:
        camera.location = location
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = scale
        look_at(camera, target)
        scene.camera = camera
        scene.render.filepath = str(render_dir / f"{asset}_{suffix}.png")
        bpy.ops.render.render(write_still=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(final_blend))
    export_objects = descendants(root)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    qa = runpy.run_path(str(scene_qa_path))["audit_scene"](
        object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
        contact_tolerance=0.004,
        floating_tolerance=0.03,
    )
    report["outputs"] = {
        "blend": str(final_blend),
        "glb": str(glb_path),
        "front": str(render_dir / f"{asset}_02_material_front.png"),
        "three_quarter": str(render_dir / f"{asset}_03_front_3q.png"),
        "side": str(render_dir / f"{asset}_04_side.png"),
        "back": str(render_dir / f"{asset}_05_back.png"),
    }
    report["validation"] = {
        "errors": sorted(set(qa["errors"])),
        "warnings": sorted(set(qa["warnings"])),
    }
    (report_dir / f"{asset}_scene_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (report_dir / f"{asset}_structural_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(final_blend))
    print(json.dumps(report, ensure_ascii=False))
    return report
