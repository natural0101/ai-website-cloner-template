from __future__ import annotations

import json
from pathlib import Path
import sys
from datetime import datetime

import bpy
import importlib


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
WORKBENCH = REPO / "blender-workbench"
SHAPE_UPGRADE = WORKBENCH / "shape-reconstruction-upgrade"
SHAPE_TOOLS = SHAPE_UPGRADE / "04_blender_tools"
if str(SHAPE_TOOLS) not in sys.path:
    sys.path.insert(0, str(SHAPE_TOOLS))

import shape_tools as st
st = importlib.reload(st)


ASSET = "hands_sphere_icon_v3_hybrid"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LAYER_STACK = WORKBENCH / "artifacts" / "reference_masks" / "v3" / "hands_sphere_v3_layer_stack.json"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
for directory in (RENDER_DIR, REPORT_DIR, EXPORT_DIR, BLEND_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def set_engine() -> None:
    scene = bpy.context.scene
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            break
        except Exception:
            continue
    if scene.render.engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 96
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 3
            scene.eevee.gtao_factor = 1.2


def set_material_finish() -> None:
    for material in bpy.data.materials:
        if not material.name.startswith("MAT_HS_V3_") or not material.use_nodes:
            continue
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        for socket_name, value in (
            ("Metallic", 0.0),
            ("Roughness", 0.44),
            ("Coat Weight", 0.22),
            ("Coat Roughness", 0.36),
            ("Alpha", 1.0),
        ):
            socket = bsdf.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value


def create_light(name: str, location: tuple[float, float, float], power: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    st.tag_object(obj, role="preview_light", export=False)
    return obj


def setup_scene() -> None:
    bpy.ops.scene.new(type="EMPTY")
    scene = bpy.context.scene
    scene.name = "HandsSphereV3HybridScene"
    set_engine()
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    world = scene.world or bpy.data.worlds.new("HS_V3_World")
    scene.world = world
    world.color = (1.0, 1.0, 1.0)


def add_preview_card() -> None:
    material = st.create_principled_material(
        "MAT_HS_V3_PreviewCard",
        base_color=(1.0, 1.0, 1.0, 1.0),
        roughness=0.62,
    )
    card = st.create_rounded_box(
        name="HS_V3_PreviewWhiteCard_not_exported",
        location=(0.0, 0.72, 0.0),
        dimensions=(5.15, 0.06, 4.15),
        radius=0.28,
        segments=10,
        material=material,
        export=False,
    )
    card.hide_select = True


def render_beauty(path: Path) -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = 927
    scene.render.resolution_y = 750
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def collect_imported_object_names(imported: dict) -> list[str]:
    names: list[str] = []
    for layer in imported.get("layers", []):
        for name in layer.get("objects", []):
            if bpy.data.objects.get(name) is not None:
                names.append(name)
    return names


def create_runtime_layer_stack() -> Path:
    config = json.loads(LAYER_STACK.read_text(encoding="utf-8"))
    config["collection"] = f"ABT_HS_V3_HYBRID_{RUN_ID}"
    runtime_path = LAYER_STACK.parent / f"{ASSET}_runtime_layer_stack.json"
    runtime_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return runtime_path


def main() -> None:
    setup_scene()

    runtime_layer_stack = create_runtime_layer_stack()
    imported = st.import_layer_stack(runtime_layer_stack)
    export_names = collect_imported_object_names(imported)
    set_material_finish()
    add_preview_card()
    create_light("HS_V3_KeyLight_not_exported", (-2.4, -5.2, 4.4), 620, 5.0)
    create_light("HS_V3_FillLight_not_exported", (3.2, -4.8, 2.5), 260, 6.0)
    create_light("HS_V3_RimLight_not_exported", (0.5, 1.8, 3.5), 90, 4.0)

    camera = st.setup_reference_camera(width=309, height=250, world_height=4.2, distance=9.5)
    silhouette = st.render_silhouette_mask(
        filepath=RENDER_DIR / f"{ASSET}_silhouette.png",
        object_names=export_names,
        width=309,
        height=250,
    )

    validation = st.validate_shape_asset(
        object_names=export_names,
        max_triangles=90_000,
        require_closed=False,
    )
    closed_diagnostic = st.validate_shape_asset(
        object_names=export_names,
        max_triangles=90_000,
        require_closed=True,
    )
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    for obj in bpy.data.objects:
        try:
            obj.select_set(False)
        except RuntimeError:
            pass
    export = st.export_glb(
        filepath=EXPORT_DIR / f"{ASSET}.glb",
        object_names=export_names,
    )
    beauty_path = RENDER_DIR / f"{ASSET}_preview.png"
    render_beauty(beauty_path)
    blend_path = BLEND_DIR / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "camera_range": "front, -15deg, +15deg only; not a true 360 reconstruction",
        "layer_stack": str(LAYER_STACK),
        "runtime_layer_stack": str(runtime_layer_stack),
        "imported": imported,
        "camera": camera,
        "silhouette": silhouette,
        "render": str(beauty_path),
        "validation": validation,
        "closed_mesh_diagnostic": closed_diagnostic,
        "export": export,
        "blend": str(blend_path),
        "scene": st.scene_report(),
        "notes": [
            "Single-image reconstruction preserves observed front silhouette only.",
            "Contour guide is converted to editable beveled mesh layers; no raster screenshot is exported.",
            "Preview card, lights and camera are tagged non-export.",
        ],
    }
    report_path = REPORT_DIR / f"{ASSET}_scene_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


main()
