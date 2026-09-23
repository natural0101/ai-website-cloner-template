# Research & Feedback Upgrade v4

Это **опциональный слой** поверх v3. Он не заменяет Blender MCP и не загружает агенту всю исследовательскую папку в каждый запрос.

## Что добавлено

1. Срез официальных анонсов, исследований, GitHub-проектов, issues, видео и отзывов.
2. Оценка достоверности каждого источника и отделение доказанного от маркетинга.
3. Staged workflow: `scene graph → geometry → material → composition → lighting → export`.
4. Разделение read-only наблюдения и изменений сцены.
5. Ограниченная память последних попыток вместо бесконечного чата.
6. Локальный retrieval по проверенным примерам без внешней БД.
7. Structural QA: соединения, gaps, floating parts, transforms, topology и версии API.
8. Security preflight для путей и Python-кода.

## Что читать

- Владелец: `00_research/EXECUTIVE_SUMMARY_RU.md`.
- Кейсы и способы реализации: `00_research/CASE_STUDIES_RU.md`.
- Агент: `02_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`.
- Для сложной задачи: `05_skills/blender-staged-production/SKILL.md`.
- Для сломанных соединений: `05_skills/blender-structural-qa/SKILL.md`.
- Для поиска похожего рецепта: `05_skills/blender-example-retrieval/SKILL.md`.
- Для безопасности MCP: `05_skills/blender-mcp-security/SKILL.md`.
- Для настройки bridge: `08_install/MCP_HARDENING_RU.md`.

## Политика активации

Активировать v4 только когда задача содержит сложную форму, несколько связанных частей, reference matching, необычный material/lookdev или уже провалилась минимум одна попытка. Для простого текста, шара, смены цвета или экспорта остаётся базовый workflow.
