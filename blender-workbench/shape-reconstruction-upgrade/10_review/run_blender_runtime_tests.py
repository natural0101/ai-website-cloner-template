"""Runtime smoke tests for Blender/bpy 5.1.x.

Run either with Blender background Python or with the official PyPI bpy wheel:
    blender --background --python run_blender_runtime_tests.py
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import traceback

import bpy

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
TOOLS = UPGRADE / "04_blender_tools"
OUTPUT = UPGRADE / "demo" / "blender_runtime"
OUTPUT.mkdir(parents=True, exist_ok=True)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_dispatcher
import shape_tools as st


def reset_scene() -> None:
    st.ensure_object_mode()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def record(name, function, tests):
    try:
        result = function()
        tests.append({"name": name, "status": "pass", "result": result})
    except Exception as exc:
        tests.append({
            "name": name,
            "status": "fail",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc().splitlines()[-12:],
        })


tests = []


def test_hand_sphere():
    reset_scene()
    created = st.create_hand_sphere_icon(
        name="RuntimeTest", sphere_radius=1.0, merge_hands=True, voxel_size=0.065
    )
    camera = st.setup_reference_camera(
        width=309, height=250, world_height=4.2, distance=10.0
    )
    silhouette = st.render_silhouette_mask(
        filepath=OUTPUT / "hand_sphere_silhouette.png"
    )
    validation = st.validate_shape_asset(max_triangles=200_000, require_closed=True)
    if validation["status"] != "pass":
        raise RuntimeError(f"Hand-sphere validation failed: {validation}")
    exported = st.export_glb(filepath=OUTPUT / "hand_sphere_runtime_test.glb")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "hand_sphere_runtime_test.blend"))
    return {
        "create": created,
        "camera": camera,
        "silhouette": silhouette,
        "validation": validation,
        "glb": exported,
        "scene": st.scene_report(),
    }


def test_contour_import():
    reset_scene()
    material = st.create_principled_material("MAT_Runtime_Contour")
    created = st.import_contour_json(
        contour_json=UPGRADE / "demo" / "combined.contours.json",
        name="RuntimeContour",
        thickness=0.12,
        bevel=0.0,
        scale=4.0,
        material=material,
        export=True,
    )
    camera = st.setup_reference_camera(
        width=309, height=250, world_height=4.0, distance=10.0
    )
    render = st.render_silhouette_mask(
        filepath=OUTPUT / "contour_blender_mask.png"
    )
    return {"created": created, "camera": camera, "render": render}


def test_hole_import():
    reset_scene()
    created = st.import_contour_json(
        contour_json=UPGRADE / "demo" / "hole_test.contours.json",
        name="RuntimeHole",
        thickness=0.12,
        bevel=0.0,
        scale=4.0,
        export=True,
    )
    st.setup_reference_camera(width=309, height=250, world_height=4.0, distance=10.0)
    render = st.render_silhouette_mask(filepath=OUTPUT / "hole_blender_mask.png")
    return {"created": created, "render": render}


def test_layer_stack():
    reset_scene()
    created = st.import_layer_stack(UPGRADE / "demo" / "layer_stack.example.json")
    st.setup_reference_camera(width=309, height=250, world_height=4.0, distance=10.0)
    render = st.render_silhouette_mask(
        filepath=OUTPUT / "layer_stack_blender_mask.png"
    )
    return {"created": created, "render": render}


def test_dispatcher():
    reset_scene()
    response = shape_dispatcher.dispatch({
        "action": "shape.create_part",
        "arguments": {
            "kind": "ELLIPSOID",
            "name": "DispatcherPart",
            "location": [0, 0, 0],
            "scale": [0.8, 0.4, 1.0],
            "collection_name": "ABT_DISPATCH_TEST",
            "material": {"base_color": [0.4, 0.7, 1.0, 1.0]},
        },
    })
    if not response.get("ok"):
        raise RuntimeError(response)
    error_response = shape_dispatcher.dispatch({
        "action": "shape.not_allowed", "arguments": {}
    })
    if error_response.get("ok") or error_response.get("error_type") != "ShapeDispatchError":
        raise RuntimeError(f"Allow-list test failed: {error_response}")

    fit_root = st.create_root("DispatcherFitRoot")
    guarded_fit = shape_dispatcher.dispatch({
        "action": "shape.apply_reference_fit",
        "arguments": {
            "report_json": str(UPGRADE / "demo" / "silhouette_report.json"),
            "root_object": fit_root.name,
            "confirm": False,
        },
    })
    if guarded_fit.get("ok") or guarded_fit.get("error_type") != "ShapeToolError":
        raise RuntimeError(f"Confirmation guard failed: {guarded_fit}")
    applied_fit = shape_dispatcher.dispatch({
        "action": "shape.apply_reference_fit",
        "arguments": {
            "report_json": str(UPGRADE / "demo" / "silhouette_report.json"),
            "root_object": fit_root.name,
            "mode": "UNIFORM",
            "confirm": True,
        },
    })
    if not applied_fit.get("ok"):
        raise RuntimeError(f"Confirmed fit failed: {applied_fit}")
    return {
        "success": response,
        "allowlist_rejection": error_response,
        "fit_guard": guarded_fit,
        "fit_applied": applied_fit,
    }


record("hand_sphere_create_validate_export", test_hand_sphere, tests)
record("contour_import_and_render", test_contour_import, tests)
record("hole_preservation_render", test_hole_import, tests)
record("layer_stack_import_and_render", test_layer_stack, tests)
record("mcp_dispatcher_allowlist", test_dispatcher, tests)

report = {
    "schema": "ai-blender-shape-runtime-tests/v1",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "blender": bpy.app.version_string,
    "python": sys.version.split()[0],
    "background": bool(bpy.app.background),
    "status": "pass" if all(t["status"] == "pass" for t in tests) else "fail",
    "tests": tests,
}
(OUTPUT / "blender_runtime_tests.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
if report["status"] != "pass":
    raise SystemExit(1)
