---
name: blender-mcp-security
description: Use before arbitrary Python execution, local file ingestion, downloads, external generation services, or writing outside the project output folder.
license: MIT
---

# MCP security

1. Default network access to OFF.
2. Resolve every input/output path and require it under configured allowlisted roots.
3. Run `security_guard.preflight(code)` before arbitrary code execution.
4. BLOCK subprocess/socket/ctypes/eval/exec and equivalent calls unless the owner explicitly enables an isolated workflow.
5. WARN and review `open`, pathlib, requests/urllib, library loading and main-file operations.
6. Do not send local files to external APIs without explicit user intent and destination disclosure.
7. Keep API keys outside prompts, scenes and reports.
8. Use OS/container isolation for untrusted code; AST scanning is not a sandbox.
9. If the active bridge supports telemetry, disable it for confidential projects (`DISABLE_TELEMETRY=true` for ahujasid/blender-mcp).
10. Log tool, arguments, paths, stage, result and error class without secrets.
