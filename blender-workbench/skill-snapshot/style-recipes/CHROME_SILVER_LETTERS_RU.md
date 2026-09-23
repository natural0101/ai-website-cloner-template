# Рецепт: серебряные/chrome буквы

## Когда использовать

Пользователь просит: «серебряные буквы», «chrome logo», «как на дорогом сайте», «Y2K metal», «зеркальный металл».

## Суть

Chrome — это не серый цвет. Chrome виден только через отражения. Если вокруг белая пустота, объект станет плоским серым пятном. Нужны bevel + reflective material + reflection cards.

## Параметры

```json
{
  "style": "chrome",
  "material": {
    "base_color": "#DDE1E7",
    "metallic": 1.0,
    "roughness": 0.08,
    "specular_ior_level": 0.8,
    "coat_weight": 0.35
  },
  "text": {
    "extrude": 0.22,
    "bevel_depth": 0.035,
    "bevel_resolution": 8,
    "resolution_u": 24
  },
  "lighting": {
    "world_strength": 0.15,
    "reflection_cards": true,
    "key_area_power": 350,
    "rim_area_power": 180
  }
}
```

## Алгоритм

1. Создай текст.
2. Выбери serif/sans шрифт по задаче.
3. Задай extrusion.
4. Задай bevel: без bevel металл будет дешёвым.
5. Создай chrome material: metallic=1, roughness 0.06–0.18.
6. Добавь чёрные и белые reflection cards слева/справа/сверху.
7. Поставь камеру 3/4 или front с фокусом 70–90mm.
8. Отрендери.
9. Проверь: видны ли белые edge highlights и чёрные отражённые полосы.
10. Если выглядит серым — увеличь контраст reflection cards, а не base color.

## Типичные ошибки

- Серебро выглядит серым: нет отражений.
- Буква плохо читается: слишком сильные чёрные полосы или низкий bevel.
- Край рваный: мало resolution/bevel segments.
- GLB выглядит иначе на сайте: окружение сайта не даёт таких отражений; нужен HDRI/environment в web viewer.
