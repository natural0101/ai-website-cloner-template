"""Example orchestration for the supplied gas-station scene.

Run in Blender after replacing paths and object groups. The example intentionally
stops between stages: inspect each render before continuing.
"""

from pathlib import Path

ROOT = Path(r"C:/REPLACE/AI_Blender_Agent_Lookdev_Lighting_Patch_v6")
OUT = Path(r"C:/REPLACE/lookdev_output")
OUT.mkdir(parents=True, exist_ok=True)

exec((ROOT / "05_tools/production_lookdev_tools.py").read_text(encoding="utf-8"))
exec((ROOT / "05_tools/scene_quality_audit.py").read_text(encoding="utf-8"))

# 1. Safety + audit
save_checkpoint(OUT / "station_lookdev_00_checkpoint.blend")
run_audit(OUT / "scene_quality_before.json")

# 2. Neutral clay. Inspect this render before touching materials.
set_neutral_clay_override(True)
configure_cycles_production(samples=128, resolution=(1280, 720), exposure=-0.5)
create_architecture_night_rig(clear_previous=True)
render_png(OUT / "01_clay_before.png", resolution=(1280, 720), samples=128, exposure=-0.5)
set_neutral_clay_override(False)

# 3. Geometry detail. Replace with reviewed hard-surface object names only.
HARD_SURFACE_OBJECTS = [
    # "Canopy",
    # "Columns",
    # "PumpBody",
    # "RoadSign",
]
if HARD_SURFACE_OBJECTS:
    print(apply_bevel_detail_pass(HARD_SURFACE_OBJECTS, width_ratio=0.003, segments=3))

# 4. Create physically distinct material families.
create_pbr_material("MAT_PaintedMetal", "painted_metal")
create_pbr_material("MAT_BareAluminium", "bare_aluminium")
create_pbr_material("MAT_Rubber", "rubber")
create_pbr_material("MAT_Plastic", "plastic")
create_pbr_material("MAT_Concrete", "concrete")
create_pbr_material("MAT_Glass", "glass")

# Assign explicitly after reviewing object names, for example:
# assign_material("Canopy", "MAT_PaintedMetal")
# assign_material("Hose", "MAT_Rubber")
# assign_material("Forecourt", "MAT_Concrete")

# 5. Visible emitters stay moderate. Add separate AREA/POINT/SPOT lights at fixtures.
# set_material_emission("MAT_SignDiffuser", color=(1.0, 0.32, 0.12, 1.0), strength=1.5)

# 6. Final Blender lookdev pass.
configure_cycles_production(samples=256, resolution=(1600, 900), exposure=-0.8)
render_png(OUT / "02_final_blender.png", resolution=(1600, 900), samples=256, exposure=-0.8)
run_audit(OUT / "scene_quality_after.json")
write_scene_summary(OUT / "scene_summary.json")

print("Next: run image_quality_audit.py externally, export GLB, then capture target web-viewer.")
