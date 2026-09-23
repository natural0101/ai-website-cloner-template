# Occlusion и layer graph

## Зачем

В маленькой картинке цветовые области часто перекрываются. Если агент не запишет порядок, он может построить правильные контуры отдельных деталей, но неправильную композицию.

## Формат

```yaml
layers_back_to_front:
  - background
  - left_wrist
  - right_wrist
  - left_palm
  - right_palm
  - sphere
  - front_fingertips
  - highlight_only

contacts:
  - [left_fingertips, sphere]
  - [right_fingertips, sphere]

forbidden_intersections:
  - [left_cuff, sphere]
  - [right_cuff, sphere]
```

## Как отличать слой от света

1. Слой меняет внешний контур или закрывает другую деталь.
2. Блик не создаёт новую геометрию и не должен превращаться в отдельную маску формы.
3. Мягкая тень не является выемкой.
4. Антиалиасинг и blur не являются толщиной.
5. Если граница неясна, отметить uncertainty и не делать необратимый remesh.

## Для Blender

При камере на отрицательной оси Y, смотрящей в +Y, более отрицательный `depth_y` находится ближе к камере. Этот convention использует `shape_tools.py`.
