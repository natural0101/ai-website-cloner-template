# Рекомендуемая архитектура

## 1. Intake

Зафиксировать цель, reference, режим результата, poly budget, camera, dimensions, materials и acceptance criteria. Не начинать код, пока не понятна разница между front-match и true 360°.

## 2. Scene graph

Разложить объект на именованные semantic parts и связи:

- `parent/child`;
- `touches/overlaps`;
- `in_front_of/behind`;
- `symmetry`;
- `material_group`;
- `editable_parameters`.

## 3. Stages

1. `INITIALIZATION`: units, collections, camera, naming, reference plane.
2. `GEOMETRY`: proportions, silhouette, profile, connections, topology.
3. `MATERIAL`: только material slots, nodes, colors, roughness, metallic, normals.
4. `COMPOSITION`: transforms, relative scale, camera framing; без geometry edits.
5. `LIGHTING`: lights, world, exposure/color management; консервативные изменения.
6. `EXPORT_QA`: topology, transforms, connectivity, budgets, GLB compatibility.

## 4. Внутри каждого stage

`inspect read-only → generate one targeted edit → render canonical views → verifier checklist → approve or rollback`

Не более заранее заданного числа раундов. После исчерпания бюджета выбрать лучшую сохранённую попытку, а не продолжать бесконечно.

## 5. Память

Хранить:

- authoritative current scene/script state;
- последние 5 попыток;
- принятые параметры;
- unresolved checklist;
- ссылки на renders и audit reports.

Не хранить весь разговор и все неудачные скрипты в active context.

## 6. Retrieval

Перед нестандартной формой искать 3–5 ближайших проверенных examples. Возвращать только релевантные snippets/paths, а не всю базу.

## 7. Human checkpoint

Запрашивать выбор только при настоящей неоднозначности: силуэт A/B, stylization, скрытая сторона, material mood. “Верно/нет” остаётся достаточным интерфейсом, но агент должен показать диагностические виды и конкретную разницу.
