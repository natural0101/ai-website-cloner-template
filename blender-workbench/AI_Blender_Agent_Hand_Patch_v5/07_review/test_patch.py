from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class HandPatchTests(unittest.TestCase):
    def test_json_syntax_and_schema(self):
        for path in ROOT.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "02_spec/hand_target.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "02_spec/hand_target.example.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(example)

    def test_manifest_entry_points(self):
        manifest = json.loads((ROOT / "PACKAGE_MANIFEST_HAND_PATCH.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["activation"], "hands_only")
        self.assertEqual(manifest["new_mcp_tools"], 0)
        for relative in manifest["entry_points"].values():
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_skill_frontmatter(self):
        path = ROOT / "05_skill/blender-stylized-hand-reconstruction/SKILL.md"
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        for field in ("name:", "description:", "license:", "compatibility:"):
            self.assertIn(field, frontmatter)

    def test_validator_and_board_generator(self):
        spec = ROOT / "02_spec/hand_target.example.json"
        validator = ROOT / "04_tools/validate_hand_target.py"
        board = ROOT / "04_tools/make_hand_target_board.py"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            report = tmp / "report.json"
            result = subprocess.run(
                [sys.executable, str(validator), str(spec), "--check-files", "--output", str(report)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["status"], "pass")

            output = tmp / "board.png"
            result = subprocess.run(
                [sys.executable, str(board), str(spec), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue(output.is_file())
            with Image.open(output) as image:
                self.assertGreater(image.width, 800)
                self.assertEqual(image.height, 600)

    def test_no_build_machine_paths(self):
        offenders = []
        for path in ROOT.rglob("*"):
            if path.resolve() == Path(__file__).resolve():
                continue
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8")
            if "/mnt/data/" in text or "hand_patch_work" in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
