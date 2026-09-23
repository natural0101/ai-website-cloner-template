# Разрешения по этапам

| Stage | Разрешено | Запрещено |
|---|---|---|
| INITIALIZATION | collections, names, units, camera scaffold | финальные материалы, destructive remesh |
| GEOMETRY | mesh/curve objects, modifiers, transforms внутри part construction | shader redesign, final lighting |
| MATERIAL | material slots, shader nodes, texture coordinates | mesh vertices, object dimensions, camera |
| COMPOSITION | object transforms, parenting, target camera | vertex edits, materials |
| LIGHTING | lights, world, exposure, color management | geometry, materials |
| EXPORT_QA | apply approved transforms, triangulation/decimation copies, export | creative redesign |

Любое нарушение stage scope требует остановки и явного перехода на нужный этап. Это предотвращает “исправил серебро — испортил букву”.
