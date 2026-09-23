# Типовые ошибки и исправления

| Ошибка | Причина | Действие |
|---|---|---|
| пальцы выглядят трубками | нет ладонной массы/overlap/taper | увеличить palm, заглубить finger bases, уменьшить tips |
| части не слились | overlap меньше voxel | увеличить overlap или уменьшить voxel size |
| исчезли пальцы | voxel слишком крупный или excessive smooth | откатиться, уменьшить voxel, убрать smooth |
| contour стал больше reference | неверная ortho camera/aspect | использовать `setup_reference_camera`; не угадывать ortho_scale |
| отверстие закрылось | потерян hierarchy или bevel/remesh | вернуть clean mask, bevel=0, проверить holes |
| IoU высокий, объект плоский | оценивался только front | перейти к side/3⁄4 volume review |
| вид сбоку нелепый | скрытая форма не спроектирована | добавить explicit profile assumptions/side reference |
| material «не похож» | geometry/light смешаны в одной итерации | сначала shape gate, затем lighting/material |
| GLB тяжёлый | экспортирован SOURCE/high poly | экспортировать только OUTPUT, создать web copy |
| агент перестраивает всё | нет локального diagnosis | исправлять одну категорию ошибки за итерацию |
