# Blockout and hands

Используй именованные массы:

- ellipsoid: core/head/palm/joint;
- rounded box: cuff/foot/soft rigid part;
- tapered Bézier tube: finger/arm/tail/cable;
- voxel union: только пересекающиеся soft parts.

Рука: palm + 4 unequal curved fingers + separate thumb + wrist + cuff. Finger bases должны входить в palm; tips тоньше; pose образует fan. Перед remesh overlap минимум 1.5–2 voxel. Сохраняй SOURCE; объединяй дубликаты в OUTPUT. После remesh не стирай fingertips, valleys и gaps чрезмерным smooth.
