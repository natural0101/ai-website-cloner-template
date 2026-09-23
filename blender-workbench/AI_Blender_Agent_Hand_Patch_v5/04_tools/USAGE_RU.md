# Использование target-board tools

## Проверить hand-target

```bash
python validate_hand_target.py ../02_spec/hand_target.example.json \
  --check-files \
  --output ../06_example/example_validation.json
```

## Создать board

```bash
python make_hand_target_board.py ../02_spec/hand_target.example.json \
  --output ../06_example/example_target_board.png
```

## Для рабочего проекта

1. Скопировать `hand_target.example.json` как `bottom_hand_target.json`.
2. Заменить координаты по референсу.
3. Запустить validator.
4. Исправить все errors.
5. Создать board.
6. Получить `верно` или `нет`.
7. Начать Blender blockout.
