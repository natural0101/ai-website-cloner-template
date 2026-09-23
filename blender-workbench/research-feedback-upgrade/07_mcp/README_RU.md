# MCP integration v4

Не заменяйте рабочий MCP. Добавьте v4 как optional resources/skills.

## Минимальные новые контракты

1. `research.retrieve_examples` — read-only, вызывает локальный retrieval.
2. `quality.capability_probe` — read-only, запускает Blender probe.
3. `quality.scene_audit` — read-only, запускает structural QA.
4. `workflow.stage_state` — вне Blender, хранит stage/attempt/checkpoint metadata.

Stage-specific mutation продолжает идти через существующий semantic dispatcher/`execute_blender_code`, но только после scope preflight. Не открывайте агенту десятки новых tools без необходимости.
