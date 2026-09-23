# Рецепт: brushed/satin silver

## Когда использовать

Для tech, premium, calm luxury, UI-hero, где chrome слишком кричащий.

## Параметры

```json
{
  "style": "brushed_silver",
  "material": {
    "base_color": "#C9CED6",
    "metallic": 1.0,
    "roughness": 0.34,
    "specular_ior_level": 0.65,
    "coat_weight": 0.12
  },
  "text": {
    "extrude": 0.18,
    "bevel_depth": 0.025,
    "bevel_resolution": 5
  }
}
```

## Алгоритм

1. Создай строгий силуэт: sans или serif.
2. Дай среднюю толщину.
3. Дай маленький аккуратный bevel.
4. Поставь roughness 0.25–0.42.
5. Добавь широкие мягкие area lights.
6. Добавь слабые reflection cards, не такие агрессивные как у chrome.
7. Камера front/3-4, без сильной перспективы.

## Проверка

- Материал должен выглядеть как металл, но не зеркало.
- Highlights широкие и мягкие.
- Текст читается даже в маленьком размере.
