# Видео: что использовать

## Проверяемые ссылки из репозиториев

1. **AI Agent Creates 3D Models in Blender from Text (MCP Tutorial)**  
   https://www.youtube.com/watch?v=lCyQ717DuzQ  
   Источник ссылки: основной BlenderMCP repo. Полезно для общего workflow; не считать benchmark.

2. **Blender MCP setup instruction video**  
   https://www.youtube.com/watch?v=neoK_WMq92g  
   Полезно для установки; не обучает сложной форме.

3. **Blender MCP Assembly Skill tutorial**  
   https://youtu.be/fsLkJNEtsTw  
   Связан с открытым `SKILL.md`; полезен для соединений, bounds и overlap.

## Как превращать видео в память агента

1. Зафиксировать точную ссылку, автора, дату и Blender version.
2. Выделить один законченный приём, а не всё видео.
3. Переписать приём в `input → prerequisites → actions → parameters → validation → failure fixes`.
4. Заменить UI-клики на устойчивый Python/semantic tool, где возможно.
5. Запустить на чистой сцене.
6. Сохранить script, render, `.blend`, version и result.
7. Только после успешного теста добавить example record.

Транскрипт без воспроизводимого результата не считается skill.
