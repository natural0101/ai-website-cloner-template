# Canonical stylized hand base

## Решение

Не строить новую кисть из случайных примитивов для каждого задания. Один раз создать собственную редактируемую базу, затем позировать и подгонять её под target.

Это не загрузка чужой модели. Это project-owned production asset, созданный с нуля и повторно используемый для стабильности.

## Минимальная структура

- `HAND_SOURCE_PALM`;
- `HAND_SOURCE_THUMB`;
- `HAND_SOURCE_INDEX`;
- `HAND_SOURCE_MIDDLE`;
- `HAND_SOURCE_RING`;
- `HAND_SOURCE_LITTLE`;
- `HAND_SOURCE_WRIST`;
- `HAND_SOURCE_CUFF`;
- `HAND_RIG`;
- `HAND_OUTPUT`.

## Контролы

- wrist translation/rotation;
- palm scale X/Y/Z;
- palm arch;
- thumb base position;
- thumb spread/curl;
- finger spread;
- индивидуальный curl каждого пальца;
- индивидуальная длина каждого пальца;
- radius root/mid/tip каждого пальца;
- cuff width/depth/roundness.

## Варианты базы

1. `puffy_five_digit` — пять читаемых пальцев и мягкие valleys.
2. `mitten_graphic` — упрощённая масса, но с отдельным большим пальцем и осознанными намёками на остальные пальцы.

Не использовать `mitten_graphic`, если референс явно показывает четыре отдельных кончика.

## Геометрия до union

- ладонь — уплощённая объёмная масса;
- пальцы — tapered curved masses;
- большой палец — отдельная mass с корректным web;
- основания пальцев входят внутрь ладони;
- wrist входит внутрь ладони;
- cuff перекрывает wrist.

## Хранение

- base хранится в отдельном `.blend`;
- SOURCE не применяется destructively;
- версия базы записывается в QA JSON;
- изменения базы проходят отдельный review;
- asset library не подключается для задач без рук.
