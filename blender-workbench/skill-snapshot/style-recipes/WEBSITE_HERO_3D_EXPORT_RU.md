# Рецепт: 3D-буквы для сайта

## Цель

Сделать красивый hero asset, который не тормозит сайт и не разваливается после экспорта.

## Ограничения

```json
{
  "format": "glb",
  "target_width_units": 3.5,
  "max_triangles_preview": 80000,
  "max_triangles_mobile": 30000,
  "materials": "PBR metallic/roughness, без сложных unsupported nodes",
  "textures": "минимум или procedural baked only when needed"
}
```

## Алгоритм

1. Сначала добейся красивого рендера в Blender.
2. Уменьши polycount только после утверждения формы.
3. Применяй modifiers осознанно.
4. Проверь origin по центру объекта.
5. Нормализуй размер.
6. Экспортируй GLB.
7. Проверь GLB в web viewer/Three.js/Babylon.
8. Если chrome стал серым — на сайте не хватает окружения/отражений.

## Для сайта chrome требует окружения

GLB хранит материал, но окружение сайта задаётся отдельно. Поэтому web-разработчик должен добавить HDR/environment map или собственные reflection cards/lighting в сцене сайта.
