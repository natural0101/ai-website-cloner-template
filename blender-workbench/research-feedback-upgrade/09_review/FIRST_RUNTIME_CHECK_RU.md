# Первый runtime check в вашей Blender 5.1

1. Открыть копию тестовой сцены.
2. Выполнить `capability_probe.probe()` и сохранить JSON.
3. Создать два куба: один касается второго, третий оставить отдельно.
4. Выполнить `scene_qa.audit_scene()`.
5. Проверить, что contact graph видит пару, а отдельный объект попадает в floating warning.
6. Выполнить material-only edit и убедиться, что bounds geometry не изменились.
7. Создать/approve один stage в `stage_orchestrator.py`.
8. Выполнить retrieval по “hand sphere floating fingers”.
9. Не подключать v4 к production до прохождения этих проверок.
