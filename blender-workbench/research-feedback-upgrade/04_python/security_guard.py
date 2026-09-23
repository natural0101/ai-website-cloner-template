"""Advisory preflight for AI-generated Blender Python.

This is intentionally conservative and is NOT a complete sandbox. Run Blender
with OS-level isolation when executing untrusted code.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

BLOCKED_IMPORTS = {'subprocess', 'socket', 'ctypes', 'ftplib', 'telnetlib'}
WARN_IMPORTS = {'os', 'pathlib', 'shutil', 'requests', 'urllib', 'http', 'importlib'}
BLOCKED_CALLS = {
    'eval', 'exec', 'compile', '__import__', 'os.system', 'os.popen',
    'subprocess.run', 'subprocess.Popen', 'subprocess.call',
    'shutil.rmtree', 'socket.socket',
}
WARN_CALLS = {
    'open', 'Path.open', 'requests.get', 'requests.post', 'urllib.request.urlopen',
    'bpy.ops.wm.open_mainfile', 'bpy.ops.wm.save_as_mainfile', 'bpy.data.libraries.load',
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = _name(node.value)
        return f'{left}.{node.attr}' if left else node.attr
    return ''


class GuardVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split('.')[0]
            if root in BLOCKED_IMPORTS:
                self.findings.append(Finding('BLOCK', 'blocked_import', alias.name, node.lineno))
            elif root in WARN_IMPORTS:
                self.findings.append(Finding('WARN', 'sensitive_import', alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ''
        root = module.split('.')[0]
        if root in BLOCKED_IMPORTS:
            self.findings.append(Finding('BLOCK', 'blocked_import', module, node.lineno))
        elif root in WARN_IMPORTS:
            self.findings.append(Finding('WARN', 'sensitive_import', module, node.lineno))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _name(node.func)
        if name in BLOCKED_CALLS:
            self.findings.append(Finding('BLOCK', 'blocked_call', name, node.lineno))
        elif name in WARN_CALLS or name.endswith('.open'):
            self.findings.append(Finding('WARN', 'sensitive_call', name, node.lineno))
        self.generic_visit(node)


def scan_code(code: str) -> list[Finding]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [Finding('BLOCK', 'syntax_error', str(exc), exc.lineno)]
    visitor = GuardVisitor()
    visitor.visit(tree)
    return visitor.findings


def ensure_allowed_path(path: str | Path, allowed_roots: Iterable[str | Path], must_exist: bool = False) -> Path:
    candidate = Path(path).expanduser().resolve(strict=False)
    roots = [Path(root).expanduser().resolve(strict=False) for root in allowed_roots]
    if not roots:
        raise PermissionError('No allowed roots configured')
    if not any(candidate == root or root in candidate.parents for root in roots):
        raise PermissionError(f'Path outside allowlist: {candidate}')
    if must_exist and not candidate.exists():
        raise FileNotFoundError(candidate)
    return candidate


def preflight(code: str) -> dict:
    findings = scan_code(code)
    return {
        'allowed': not any(f.severity == 'BLOCK' for f in findings),
        'findings': [asdict(f) for f in findings],
        'disclaimer': 'Advisory AST preflight only; not an OS sandbox.',
    }
