# Материалы, свет и камера

## Материалы

Для web‑экспорта предпочитай один Principled BSDF без сложных procedural nodes.

```python
abt.dispatch("material.create_principled", {
    "name": "ClayBlue",
    "base_color": "#65B9E8",
    "roughness": 0.52,
    "metallic": 0.0,
    "specular_ior_level": 0.32,
    "coat_weight": 0.02
})
```

Procedural Noise/Bump может выглядеть в Blender, но не обязан переноситься в GLB без baking.

## Свет

`scene.setup_studio` создаёт:

- key;
- fill;
- rim;
- world lighting;
- preview floor.

Удаляются только ранее созданные toolkit‑lights. Пользовательские lights не удаляются.

Floor имеет `abt_export=False` и не должен попадать в GLB.

## Камера

Всегда используй `camera.frame` после изменения геометрии.

- `FRONT`: максимальная читаемость текста.
- `FRONT_3Q`: показывает объём.
- `SIDE`: проверяет extrusion/depth.
- `TOP`: схемы и лежащие формы.

Камера рассчитывается по world bounds и FOV. Ручные координаты допустимы только для художественной финальной корректировки после автоматического кадрирования.

## Превью

- Для быстрых итераций: 256–512 px.
- Для финальной проверки: 768–1024 px.
- `AUTO`: Eevee в GUI, Cycles в background mode.
- `isolate=True`: скрывает постороннюю геометрию на время рендера.
- `transparent=True`: для прозрачного PNG без floor.
