# Skill: blender-production-lookdev

## Назначение

Довести утверждённую Blender-сцену от blockout/preview до контролируемого production lookdev и затем проверить воспроизводимость вида в GLB/web-viewer.

## Активировать, когда

- форма, пропорции, камера и композиция уже утверждены;
- пользователь жалуется на «резиновый», «пластмассовый», «плоский», «пересвеченный» или «типично Blender» вид;
- требуется улучшить материалы, свет, глубину, детализацию или web-подачу.

## Не активировать, когда

- ещё не утверждён силуэт;
- решается реконструкция руки, лица или другой органической формы;
- требуется только topology repair или анимация;
- пользователь просит быстрый черновой blockout.

## Обязательные входы

1. Путь к `.blend` или открытая сцена.
2. Активная камера.
3. Цель: Blender render, GLB для сайта или оба результата.
4. Утверждённый референс/стиль.
5. Ограничение по производительности сайта, если оно известно.

## Порядок выполнения

1. Создай versioned checkpoint через `save_checkpoint()`.
2. Запусти `scene_quality_audit.run_audit()` без изменения сцены.
3. Сделай neutral-clay render.
4. Исправь только геометрическую читаемость: bevel, толщину, контакт, пересечения, secondary details.
5. Сделай material-ID pass по физическим категориям поверхности.
6. Назначь PBR-материалы с различимой roughness response.
7. Добавь environment/world, затем key, fill, rim, practical lights.
8. Раздели видимый emissive diffuser и реальный источник света.
9. Настрой AgX/exposure до bloom/glare.
10. Сделай final render и запусти `image_quality_audit.py`.
11. Экспортируй GLB и отдельно настрой web-viewer.
12. Сравни Blender и browser screenshot рядом.

## Разрешённые инструменты

- `05_tools/production_lookdev_tools.py`
- `05_tools/scene_quality_audit.py`
- `05_tools/image_quality_audit.py`
- штатные `bpy`-операции, если они не дублируют готовый helper;
- целевой web-viewer и glTF validator.

## Ограничения

- Не удалять пользовательские объекты.
- Не применять destructive modifiers без checkpoint/копии.
- Не менять geometry, materials, lighting и exposure одной пачкой.
- Не считать viewport screenshot финальным proof.
- Не использовать один material preset для всей сцены.
- Не компенсировать плохой свет bloom, saturation или чисто белым emission.
- Не обещать parity Blender→GLB без browser screenshot.

## Обязательные артефакты результата

1. `scene_quality_report.json`
2. `clay.png`
3. `final_blender.png`
4. `final_blender.audit.json`
5. `scene.glb`
6. `final_browser.png`
7. краткий diff: что изменено и почему;
8. список оставшихся ограничений.

## Gate принятия

Результат принимается только если:

- clay render читается без материалов;
- нет крупных пересечений и неоправданно острых visible edges;
- поверхности различаются не только цветом, но и roughness/reflection response;
- яркие вывески и окна сохраняют форму и цвет;
- контактные тени привязывают объекты к земле;
- нет критического clipping по PNG-аудиту;
- браузерная версия визуально согласована с утверждённой Blender-версией.
