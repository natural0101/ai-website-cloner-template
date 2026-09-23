# Что не ставить по умолчанию

- PyTorch/CUDA внутрь Blender Python.
- Несколько image‑to‑3D моделей одновременно.
- Случайные Blender add-ons без конкретной операции.
- Автоматические asset downloaders, если цель — моделирование с нуля.
- Большую vector database из непроверенных YouTube transcripts.
- Любой tool, который не возвращает deterministic file/report и не имеет rollback.

Сначала измерить, какой этап проваливается: mask, camera, blockout, union, profile, topology, material или export. Устанавливать tool только для конкретного bottleneck.
