---
name: blender-example-retrieval
description: Use before writing unfamiliar Blender geometry/material code or when the first attempt fails due to API, topology, or style mismatch.
license: MIT
---

# Example retrieval

1. Query `06_examples/examples.jsonl` with task, representation, style and failure terms.
2. Return at most 5 examples.
3. Prefer `RUNTIME_TESTED` over `STATIC_ONLY` and `RESEARCH_PATTERN`.
4. Read only the referenced source files needed for the active stage.
5. Copy no code blindly: check Blender version and input assumptions.
6. After success, create a new record only when script, render, `.blend`/report and acceptance criteria are preserved.
7. Never store a chat-only anecdote as a verified example.
