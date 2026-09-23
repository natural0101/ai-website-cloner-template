"""Static validation for the lookdev patch.

This does not replace a Blender 5.1 runtime test. It validates package structure,
Python syntax, JSON, safety invariants and the supplied image audit.
"""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09_review" / "STATIC_VALIDATION.json"

REQUIRED = [
    "README_RU.md",
    "00_start/START_HERE_RU.md",
    "01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md",
    "02_diagnosis/CURRENT_SCENE_REVIEW_RU.md",
    "03_workflow/PRODUCTION_LOOKDEV_PIPELINE_RU.md",
    "03_workflow/WEB_GLTF_PARITY_RU.md",
    "04_recipes/GAS_STATION_SCENE_RECIPE_RU.md",
    "05_tools/production_lookdev_tools.py",
    "05_tools/scene_quality_audit.py",
    "05_tools/image_quality_audit.py",
    "06_skill/blender-production-lookdev/SKILL.md",
    "07_examples/01_upgrade_current_scene.py",
    "07_examples/02_threejs_viewer_setup.js",
    "08_sources/SOURCES_RU.md",
    "09_review/QUALITY_REVIEW_RU.md",
    "reference/current_scene.png",
    "reference/current_scene_clipping_map.png",
]


def check(condition: bool, name: str, detail: str = "") -> dict:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    results: list[dict] = []

    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    results.append(check(not missing, "required_files", ", ".join(missing)))

    empty = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and p.stat().st_size == 0]
    results.append(check(not empty, "no_empty_files", ", ".join(empty)))

    py_errors: list[str] = []
    for path in ROOT.rglob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            py_errors.append(f"{path.relative_to(ROOT)}: {exc}")
    results.append(check(not py_errors, "python_ast", " | ".join(py_errors)))

    json_errors: list[str] = []
    for path in ROOT.rglob("*.json"):
        if path == OUT:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append(f"{path.relative_to(ROOT)}: {exc}")
    results.append(check(not json_errors, "json_parse", " | ".join(json_errors)))

    prompt = (ROOT / "01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md").read_text(encoding="utf-8")
    required_prompt_terms = ["checkpoint", "neutral clay", "GLB/web parity", "Не меняй более одного"]
    absent = [term for term in required_prompt_terms if term not in prompt]
    results.append(check(not absent, "agent_prompt_guards", ", ".join(absent)))

    helper = (ROOT / "05_tools/production_lookdev_tools.py").read_text(encoding="utf-8")
    safety_ok = (
        "bpy.ops.object.delete" not in helper
        and "TAG = \"lookdev_v6_generated\"" in helper
        and "if bool(obj.get(TAG, False))" in helper
        and "save_checkpoint" in helper
    )
    results.append(check(safety_ok, "non_destructive_helper_guards"))

    recipes = json.loads((ROOT / "04_recipes/MATERIAL_RECIPES.json").read_text(encoding="utf-8"))
    normalized_range_keys = {"roughness_range", "coat_weight_range"}
    ranges_ok = all(
        0.0 <= value <= 1.0
        for recipe in recipes.values()
        for key, values in recipe.items()
        if key in normalized_range_keys and isinstance(values, list)
        for value in values
    )
    results.append(check(ranges_ok, "material_ranges_normalized"))

    # Load the external image auditor without importing bpy-dependent modules.
    auditor_path = ROOT / "05_tools/image_quality_audit.py"
    spec = importlib.util.spec_from_file_location("image_quality_audit", auditor_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load image_quality_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.audit_image(ROOT / "reference/current_scene.png")
    metrics_ok = (
        report["width"] == 1234
        and report["height"] == 712
        and 8.5 < report["all_channels_exactly_clipped_pct"] < 10.0
        and 15.0 < report["any_channel_exactly_clipped_pct"] < 16.0
        and report["status"] == "REVIEW_REQUIRED"
    )
    results.append(check(metrics_ok, "reference_image_audit", json.dumps(report, ensure_ascii=False)))

    sources = (ROOT / "08_sources/SOURCES_RU.md").read_text(encoding="utf-8")
    source_domains = ["docs.blender.org", "KhronosGroup/glTF", "threejs.org", "google/filament", "arxiv.org"]
    missing_sources = [domain for domain in source_domains if domain not in sources]
    results.append(check(not missing_sources, "primary_sources_present", ", ".join(missing_sources)))

    failed = [item for item in results if item["status"] != "PASS"]
    payload = {
        "package": ROOT.name,
        "static_tests": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "status": "PASS" if not failed else "FAIL",
        "runtime_blender_test": "NOT_RUN: Blender 5.1 unavailable in this environment",
        "results": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
