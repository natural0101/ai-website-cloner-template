# Blender Quality Gate

Этот чеклист обязателен перед словами "готово", "финал", "можно ставить на сайт".

## До моделинга

- Primary reference сохранен в `blender-workbench/references/`.
- Режим задачи выбран: `text/design`, `shape reconstruction`, `organic object`, `icon/hero object` или `GLB export`.
- Подходящий skill/workflow выбран до кода; для сложных задач открыт `AGENT_START_HERE.md`.
- Выписаны: силуэт, пропорции, occlusion order, crop/aspect, палитра, материал, камера, свет.
- Если референса нет, агент сам ищет 3-6 близких примеров и сохраняет ссылки/выводы в `REFERENCE_MATCHING.md` или `notes/`.
- Blender сцена проинспектирована.
- Если сцена не пустая и будут существенные изменения, сделан checkpoint.
- Для v4/staged задач есть scene graph: named parts, dimensions, expected contacts, material groups, acceptance criteria.

## Во время моделинга

- После 1-3 существенных операций сделан повторный inspect.
- Для v4/staged задач изменения идут по этапам: `INITIALIZATION`, `GEOMETRY`, `MATERIAL`, `COMPOSITION`, `LIGHTING`, `EXPORT_QA`.
- Одна попытка исправляет один dominant defect; если стало хуже, rollback к checkpoint/best attempt.
- Камера не угадывается на глаз: нужно frame/setup, orthographic для icon matching.
- Для chrome/silver есть reflection cards/environment и контрастные блики.
- Preview floor, backdrop, lights и камеры не попадают в GLB export.
- Старые тестовые объекты скрыты или исключены из export.
- Для multi-part объектов structural QA проверяет contacts/gaps/floating components до export.

## Перед экспортом

- PNG preview существует и просмотрен.
- Для reference matching создан overlay render vs reference.
- JSON scene/validation report сохранен в `artifacts/reports/`.
- `validation.errors` пустой.
- GLB существует и имеет ненулевой размер.
- `.blend` сохранен.
- Triangle count записан в handoff/current state.
- Warnings не скрываются: если warnings есть, они перечислены пользователю.

## Бюджеты

- Soft web icon target: до 60k triangles.
- Hero logo: допускается больше, если сайт грузит GLB нормально и визуально это оправдано.
- Если icon выше 60k, это не автоматический провал, но нужен явный выбор: сохранить визуальную точность или оптимизировать.

## Когда не считать готовым

- "Похоже по настроению" вместо "попало в силуэт".
- Плоский серый материал вместо серебра.
- Есть только screenshot/PNG без редактируемого `.blend` и GLB.
- Есть GLB, но нет render preview.
- Объект выглядит нормально только в Blender viewport, но не проверен в web/GLB.
- Пользователь просит 95%, а агент не сделал overlay и не перечислил отличия.
