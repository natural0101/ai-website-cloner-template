# Границы инструментов

## Read-only

- scene summary;
- object bounds/dimensions/transforms;
- material summary;
- topology and connectivity audit;
- canonical/multi-view render;
- reference comparison;
- retrieval of examples;
- Blender capability probe.

## State-changing

- semantic geometry creation;
- stage-scoped edit;
- material edit;
- composition edit;
- lighting edit;
- checkpoint/rollback;
- export.

Read-only tool не должен незаметно создавать камеры, менять active object, сохранять файл или применять modifiers. Если временный объект неизбежен, он создаётся в отдельной diagnostic collection и гарантированно удаляется.
