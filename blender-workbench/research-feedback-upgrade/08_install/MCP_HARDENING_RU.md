# Настройка и защита MCP bridge

Применять только к тому bridge, которым вы реально пользуетесь. Блок с `uvx` ниже относится к `ahujasid/blender-mcp`; не меняйте рабочую установку без причины.

## Рекомендуемая конфигурация для ahujasid/blender-mcp

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["--python", "3.11", "blender-mcp"],
      "env": {
        "UV_PYTHON_PREFERENCE": "only-managed",
        "DISABLE_TELEMETRY": "true"
      }
    }
  }
}
```

На Windows GUI-клиент иногда требует абсолютный путь к `uvx.exe` или wrapper `cmd /c`. Не меняйте Blender 5.1 bundled Python: pin `3.11` относится только к внешнему MCP server process.

## Обязательные operational rules

1. Запускайте только **один** экземпляр Blender MCP server на один Blender endpoint.
2. Перед production выполните read-only health sequence: connection → Blender version → scene name → object count → screenshot/preview.
3. При timeout не повторяйте mutating command вслепую. Сначала проверьте, была ли операция фактически выполнена.
4. Для конфиденциальных reference/prompt/code установите `DISABLE_TELEMETRY=true`. В текущем README bridge указано, что снятие consent оставляет минимальную телеметрию; переменная окружения отключает её полностью.
5. Poly Haven, Sketchfab, Hyper3D, Hunyuan и другие внешние integrations держите выключенными, пока конкретная задача их не требует.
6. Не передавайте local path внешнему generator без allowlist, явного согласия и известного destination.
7. Сохраняйте checkpoint до arbitrary Python и до больших non-idempotent операций.
8. Credentials храните в environment/add-on preferences, не в prompt, `.blend`, skill или отчёте.

## Что не надо менять

- Не ставьте второй MCP bridge только ради большего числа tools.
- Не включайте внешние generators как default modeling path.
- Не увеличивайте timeout бесконечно: длинную операцию разбивайте на checkpointed stages.
- Не разрешайте raw executor обходить security/allowlist policy.

Источник operational details: `S02` и issues `S03–S05` в `00_research/SOURCE_AUDIT.*`.
