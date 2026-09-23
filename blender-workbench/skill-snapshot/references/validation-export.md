# Validation и GLB

## Что проверяется

- наличие exportable geometry;
- vertices/faces/triangles;
- non-finite coordinates;
- zero-area faces;
- boundary/non-manifold topology;
- non-uniform или negative scale;
- наличие материалов;
- Principled BSDF;
- triangle budget.

Boundary edges не считаются ошибкой по умолчанию: открытая tube или текст после curve conversion могут корректно отображаться. Для закрытого solid включай `require_manifold=True`.

## Triangle budget

Начальные ориентиры:

- простая иконка: до 10k;
- слово из нескольких букв: до 50k;
- главный hero‑объект: до 100k;
- больше — только по явной причине и с измерением производительности сайта.

## Порядок

```python
report = abt.dispatch("asset.validate", {
    "object_names": ["AssetRoot", "Mesh01"],
    "max_triangles": 50000
})
```

При `status="fail"` GLB не экспортировать.

```python
abt.dispatch("asset.export_glb", {
    "name": "site_asset",
    "object_names": ["AssetRoot", "Mesh01"],
    "max_triangles": 50000,
    "validate": True
})
```

## Материалы glTF

Надёжно переносятся простые PBR‑параметры Principled BSDF. Сложные Blender‑nodes требуют baking или ручной проверки в целевом web‑viewer.

## После экспорта

Проверь:

- файл существует;
- размер больше нуля;
- floor/camera/lights отсутствуют;
- root hierarchy сохранена;
- материал и ориентация корректны;
- в целевом viewer нет отличий по цвету и scale.
