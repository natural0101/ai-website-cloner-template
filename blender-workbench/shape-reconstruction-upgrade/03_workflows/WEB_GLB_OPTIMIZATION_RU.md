# Web GLB optimization

## Перед экспортом

1. Экспортировать только объекты с `abt_shape_export=true`.
2. Исключить SOURCE, contour guides, cameras, lights и review meshes.
3. Применить нужные transforms/modifiers.
4. Проверить manifold/boundary edges.
5. Проверить normals и materials.
6. Проверить triangle budget.

## Бюджет

Начальный ориентир для одного hero‑asset: до 80 000 triangles. Реальный бюджет зависит от числа объектов на странице, устройств и анимации.

## High → web

- держать high/editable source отдельно;
- создать копию для decimate/retopology;
- проверять silhouette после каждого упрощения;
- не уменьшать polygons ценой пальцев, отверстий и rounded profile;
- для деформируемой руки нужна отдельная topology/rigging процедура, не только voxel mesh.

## Материал

Для надёжного GLB использовать простой Principled/PBR материал. Сложные Blender procedural nodes не гарантированно переносятся в glTF без bake.
