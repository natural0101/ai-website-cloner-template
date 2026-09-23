# Quality review v6

## Что проверено

- документация разделяет geometry, materials, lighting, exposure и web parity;
- skill активируется только после утверждения формы и не конфликтует с hand/shape reconstruction;
- Blender helpers не удаляют пользовательские объекты;
- автоматически созданные lights помечаются тегом и удаляются отдельно;
- scene audit работает только на чтение;
- image audit измеряет clipping, luma и crushed blacks;
- material presets используют metallic/roughness PBR и не превращают все поверхности в один пластик;
- GLB-процесс явно отделён от Blender final render;
- источники имеют маркировку достоверности.

## Почему патч не должен мешать агенту

1. Он активируется только на финальном lookdev-этапе.
2. Он запрещает одновременно менять несколько классов факторов.
3. Он требует checkpoint и diagnostic renders.
4. Он не навязывает сторонний add-on.
5. Procedural детали маркируются как preview-only или bake-required.
6. Web runtime настраивается отдельно, поэтому агент не ломает asset для компенсации viewer.

## Ограничения

- Blender 5.1 runtime в этой среде недоступен: Python-файлы прошли статическую компиляцию, но первый запуск должен быть проверен в установленном Blender 5.1.
- Названия Principled sockets и render-engine enum защищены feature checks, но конкретная сборка Blender может потребовать точечной адаптации.
- Световые мощности зависят от масштаба сцены; rig создаёт стартовое состояние, а не финальный свет.
- По одному PNG нельзя проверить topology, UV, реальные материалы или GLB parity.
- Автоматический score scene audit — triage, а не художественная оценка.

## Итог ревью

Патч полезен и архитектурно изолирован. Его можно подключать без замены предыдущих shape/text skills. Production-ready статус разрешён только после runtime renders и browser parity test.
