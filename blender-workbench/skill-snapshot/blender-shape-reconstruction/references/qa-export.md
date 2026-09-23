# QA and export

Clean-mask shape gate: IoU ≥ 0.85, boundary F1 ≥ 0.90 при tolerance 2–3 px, holes exact. Это guideline, не универсальная гарантия.

Для TRUE_360 front score дополняется side/3⁄4/back review. Проверяй disconnected parts, implausible profile, self-intersections и contact zones.

Перед GLB: export only OUTPUT/tagged objects, closed mesh where required, no degenerate faces, material present, triangle budget respected. SOURCE, contours, cameras и lights не экспортировать.
