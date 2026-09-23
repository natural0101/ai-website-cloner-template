# Начать здесь

## Порядок чтения агентом

1. `01_agent_memory/PASTE_INTO_AGENT_PROMPT_RU.md`.
2. `02_spec/HAND_TARGET_SPEC_RU.md`.
3. `03_workflow/HAND_FROM_SINGLE_REFERENCE_RU.md`.
4. `03_workflow/QA_GATES_AND_REJECTION_RU.md`.
5. `05_skill/blender-stylized-hand-reconstruction/SKILL.md`.

## Обязательный первый результат

До построения финальной геометрии агент должен сохранить:

- `hand_target.json`;
- `hand_target_board.png`;
- `hand_target_validation.json`.

На board должны быть видимый контур, скрытый контур, landmarks, centerlines, радиусы и точки перекрытия предметом.

## Роль пользователя

Пользователь не обязан вручную рисовать точки. Агент сам подготавливает board и просит только ответ `верно` или `нет`.

## Установка рядом с основным kit

Распаковать каталог целиком рядом с `AI_Blender_Agent_Kit` либо внутрь него как `hand_reconstruction_patch_v5`.

## Что не подключать

Не добавлять новые MCP tools по умолчанию. Патч меняет порядок работы и критерии качества, а не расширяет глобальный tool list.
