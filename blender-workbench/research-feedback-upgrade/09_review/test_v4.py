from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
UP = HERE.parent


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, UP / rel)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stage = load('stage_orchestrator_v4', '04_python/stage_orchestrator.py')
retrieval = load('retrieval_index_v4', '04_python/retrieval_index.py')
security = load('security_guard_v4', '04_python/security_guard.py')


class V4Tests(unittest.TestCase):
    def test_stage_scope_and_memory(self):
        o = stage.StageOrchestrator.create('p1', 'goal', memory_limit=2)
        a = o.record_attempt('a1', 'accept spec', ['spec'])
        o.review_attempt(a.attempt_id, True)
        o.approve_stage(a.attempt_id, '/tmp/intake.blend')
        self.assertEqual(o.active_stage, stage.Stage.INITIALIZATION)
        with self.assertRaises(stage.ScopeViolation):
            o.record_attempt('bad', 'material too early', ['materials'])
        for i in range(2):
            att = o.record_attempt(f'i{i}', 'init', ['collections'])
            o.review_attempt(att.attempt_id, i == 1)
        self.assertEqual(len(o.memory_window()['last_attempts']), 2)

    def test_retrieval(self):
        idx = retrieval.ExampleIndex.from_jsonl(UP / '06_examples/examples.jsonl')
        results = idx.search('stylized hand sphere floating fingers true 360', top_k=3)
        self.assertTrue(results)
        self.assertEqual(results[0].record['id'], 'ex_hand_sphere_runtime')

    def test_security(self):
        safe = security.preflight('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        self.assertTrue(safe['allowed'])
        bad = security.preflight('import subprocess\nsubprocess.run(["x"])')
        self.assertFalse(bad['allowed'])
        with tempfile.TemporaryDirectory() as tmp:
            p = security.ensure_allowed_path(Path(tmp) / 'file.txt', [tmp])
            self.assertTrue(str(p).startswith(str(Path(tmp).resolve())))

    def test_json_assets(self):
        for path in UP.rglob('*.json'):
            json.loads(path.read_text(encoding='utf-8'))
        for line in (UP / '06_examples/examples.jsonl').read_text(encoding='utf-8').splitlines():
            if line.strip():
                json.loads(line)


if __name__ == '__main__':
    unittest.main()
