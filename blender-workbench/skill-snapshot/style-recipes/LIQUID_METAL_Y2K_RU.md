# Рецепт: liquid metal / Y2K chrome

## Когда использовать

Для модного web hero, логотипа, музыкального/креативного проекта, «жидкие серебряные буквы».

## Отличия от обычного chrome

- Больше bevel.
- Более текучий силуэт.
- Можно слегка деформировать mesh через lattice/simple deform/displace.
- Отражения контрастнее.

## Параметры

```json
{
  "style": "liquid_metal",
  "material": {
    "base_color": "#E7EAEE",
    "metallic": 1.0,
    "roughness": 0.05,
    "coat_weight": 0.45
  },
  "text": {
    "extrude": 0.28,
    "bevel_depth": 0.085,
    "bevel_resolution": 12
  },
  "deform": {
    "noise_strength": 0.025,
    "smooth": true
  }
}
```

## Алгоритм

1. Начни с rounded/script/bold font.
2. Сделай глубокий extrude.
3. Сделай крупный bevel.
4. Convert to mesh только после утверждения формы.
5. Применяй мягкую deformation очень осторожно.
6. Добавь chrome material.
7. Добавь reflection cards с вертикальными полосами.
8. Рендери 3/4, чтобы была видна толщина.

## Ошибка

Если буквы становятся нечитаемыми, уменьши deform и bevel. В liquid metal читабельность важнее «жидкости».
