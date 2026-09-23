# Память v4

## Постоянные правила

- MCP = транспорт, skill = процедура, example = проверенный опыт.
- Reference appearance и true geometry — разные источники истины.
- Сначала отношения и размеры, потом детали.
- Connections проверяются числами, не только глазами.
- Материал не исправляет неверный силуэт.
- Свет не исправляет неверный материал.
- Front match не доказывает 360°.
- Accepted stage сохраняется checkpoint; rejected attempt откатывается.
- Старые попытки удаляются из active memory после 5 записей.

## Формат краткой рабочей памяти

```json
{
  "goal": "...",
  "mode": "TRUE_360|HYBRID_HERO|FRONT_2_5D",
  "active_stage": "GEOMETRY",
  "accepted_state": "checkpoint/path.blend",
  "scene_graph": "scene_graph.json",
  "last_attempts": [],
  "unresolved": [],
  "next_action": "one precise action"
}
```
