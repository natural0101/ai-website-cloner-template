# Краткие исследовательские выводы

1. **Single-view ambiguity — фундаментальная, а не Blender‑ошибка.** Один observed view ограничивает проекцию, но не уникальную скрытую поверхность.
2. **Силуэт — сильный сигнал для внешнего контура, слабый для concavity/back side.** Поэтому front mask нужно сочетать с category priors или дополнительными видами.
3. **Differentiable fitting существует, но не отменяет prior.** Даже идеальная optimization loss может найти форму, которая совпадает с камерой и неверна с других сторон.
4. **Production modeling начинается с blockout.** Для stylized asset semantic masses дают агенту более устойчивое пространство действий, чем прямое редактирование тысяч vertices.
5. **Voxel remesh — переход, не source of truth.** Он создаёт единую поверхность, но может уничтожить small gaps/details; source primitives обязательны.
6. **Метрики должны быть раздельными.** Front silhouette, multiview plausibility и web readiness нельзя сводить в один процент.
