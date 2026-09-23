# Установка v4

1. Оставьте текущий Blender MCP без изменений; затем проверьте `MCP_HARDENING_RU.md`.
2. Добавьте `research_feedback_upgrade/04_blender` в Blender `sys.path` или ресурсный путь агента.
3. Добавьте `research_feedback_upgrade/04_python` в окружение MCP/агента.
4. Подключите только нужные skills из `05_skills`.
5. Передайте агенту `02_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`.
6. Зарегистрируйте максимум четыре optional contracts из `07_mcp/tool_manifest_v4.json`.
7. Выполните первый runtime check из `09_review/FIRST_RUNTIME_CHECK_RU.md`.

## Дополнительные программы

Сейчас **не обязательны**.

- OpenCV-venv из v3 остаётся нужен только для masks/overlay.
- Qdrant/embedding model добавлять только когда проверенных examples станет больше примерно 200–500 и stdlib retrieval перестанет хватать.
- External text/image-to-3D сервисы подключать только как optional imported-source workflow, не как замену modeling skills.
