# Production Lookdev Pipeline

## Gate 0 — безопасное состояние

- сохранить versioned checkpoint;
- зафиксировать камеру и композицию;
- проверить единицы и реальный масштаб;
- не применять destructive modifiers без копии объекта.

**Выход:** сцена восстанавливается одним действием.

## Gate 1 — neutral clay / geometry

1. Временно отключить emission, bloom/glare и сложные материалы.
2. Назначить нейтральный серый материал.
3. Осветить одной большой area light и слабым world fill.
4. Проверить силуэт, толщину, bevel, контакт, пересечения и масштаб деталей.
5. Добавить primary/secondary/tertiary geometry в таком порядке.

**Запрещено переходить дальше**, если объект выглядит игрушечным уже в clay render.

## Gate 2 — material ID

Разделить поверхности по физическому типу, а не только по цвету:

- painted metal;
- bare metal;
- plastic;
- rubber;
- glass;
- concrete/asphalt;
- emissive diffuser;
- decals/signage.

Сначала использовать чистые материалы без noise. Проверить различие roughness и specular при одинаковом нейтральном освещении.

## Gate 3 — material detail

- добавить roughness variation;
- добавить normal/bump только в масштабе реальной поверхности;
- добавить seams, dirt masks и edge wear умеренно;
- проверить UV и texel density;
- всё procedural, предназначенное для сайта, либо заменить текстурами, либо запечь.

## Gate 4 — lighting

Порядок:

1. environment/world;
2. key;
3. fill;
4. rim/separation;
5. practical fixtures;
6. emissive appearance;
7. exposure;
8. только затем glare/bloom.

В каждой итерации менять один параметрический блок. Сравнивать с предыдущим checkpoint.

## Gate 5 — camera and color

- perspective, если референс не ортографический;
- lens под композицию, а не для компенсации неправильного масштаба;
- AgX либо другой осознанный view transform;
- exposure выставляется по сохранению формы ярких поверхностей;
- contrast/look выбирается после правильной экспозиции.

## Gate 6 — diagnostic renders

Минимум:

1. clay;
2. final PBR;
3. front;
4. 3/4;
5. side;
6. clipping report;
7. scene audit.

## Gate 7 — web parity

1. Экспортировать GLB.
2. Проверить validator.
3. Открыть в целевом viewer.
4. Добавить environment map.
5. Настроить tone mapping/exposure.
6. Воссоздать lighting, который не переносится стандартом.
7. Сравнить Blender и browser screenshots рядом.

**Production-ready** означает прохождение всех gates, а не только красивый Blender viewport.
