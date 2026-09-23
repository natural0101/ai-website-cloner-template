# Популярность и зрелость — снимок 22 июня 2026

| Система | Наблюдаемый сигнал | Что это означает | Чего не означает |
|---|---:|---|---|
| ahujasid/blender-mcp | ≈23k stars, ≈2.3k forks | Очень высокий интерес к Blender MCP | Не гарантирует сложный моделинг |
| Blender MCP Assembly Skill | ≈30 stars | Есть спрос на узкий geometry skill | Нет крупного benchmark |
| AGNO 17-agent studio | ≈48 stars | Multi-agent pipeline реализуем | Нет доказательства оптимальности 17 агентов |
| LLM-Blender-Agent | ≈29 stars, 56 commits | Несколько LLM/provider integrations работают | Внешние 3D generators не равны modeling from scratch |
| BlenderRAG | ≈12 stars, 41 commits | Research code опубликован | Пока небольшое реальное adoption |
| sandraschi/blender-mcp | ≈14 stars, 108 commits | Широкая headless/live automation реализуема | Небольшой пользовательский сигнал |

## Оценка зрелости

- **Transport/connection:** рабочий, популярный, но issues по таймаутам и совместимости сохраняются.
- **Простые операции и automation:** зрелые.
- **Procedural assets средней сложности:** реальны при наличии skills, RAG и verifier loop.
- **Сложная органика и точный single-image 360°:** экспериментальный уровень.
- **Полностью автономный “Blender expert”:** пока не подтверждён надёжными независимыми тестами.
