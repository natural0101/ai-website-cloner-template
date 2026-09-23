# Что действительно требуется настроить

## Обязательно

1. Blender 5.1.x с MCP, который выполняет Python внутри текущей сцены.
2. Каталог `04_blender_tools` в `sys.path` Blender.
3. Skill `blender-shape-reconstruction` с активацией только на shape/reference‑задачи.
4. Возможность агенту получить structured scene report, render path и validation report.
5. Для автоматического сравнения: обычный Python‑venv с `numpy` и `opencv-python-headless`.

## Желательно

1. MCP должен возвращать полный JSON результата, а не только скриншот.
2. Должны быть доступны абсолютные пути к reference, mask, output и GLB.
3. Пользовательская сцена должна сохраняться checkpoint перед Voxel Remesh или массовыми изменениями.
4. Агенту нужны минимум front silhouette и один perspective/side render для `TRUE_360`.
5. Для точного референса желательно исходное изображение 800–1500 px или clean alpha mask.

## Не требуется по умолчанию

- fine‑tuning модели;
- скачивание готовых рук или иконок;
- SAM, Depth Anything, Hunyuan3D, TRELLIS;
- PyTorch внутри Blender;
- Geometry Nodes для каждой фигуры;
- произвольный огромный `bpy`‑скрипт.

## Почему отдельный Python‑venv

Blender Python должен оставаться стабильным. OpenCV/AI‑модели имеют собственные бинарные зависимости. Внешний процесс создаёт только PNG/JSON, а Blender читает эти безопасные промежуточные файлы.
