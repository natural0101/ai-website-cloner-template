# Необязательные инструменты

Ни один из них не нужен для базового workflow «примитивы → voxel union → silhouette QA → GLB».

## 1. SAM 3.1

**Назначение:** получить первичную mask сложного объекта по point/box/text prompt.

**Когда использовать:** фон и объект плохо разделяются, ручная маска слишком долгая.

**Ограничение:** результат обязательно проверяется и корректируется; segmentation не восстанавливает глубину.

По официальному репозиторию на 22.06.2026: SAM 3.1 опубликован 27.03.2026; заявлены Python 3.12+, PyTorch 2.7+ и CUDA 12.6+.

Источник: https://github.com/facebookresearch/sam3

## 2. Depth Anything V2

**Назначение:** rough relative-depth prior и подсказка для layer ordering/profile.

**Не использовать как:** точную metric depth маленькой stylized картинки или готовый mesh.

Источник: https://github.com/DepthAnything/Depth-Anything-V2

## 3. PyTorch3D

**Назначение:** advanced differentiable silhouette fitting, когда нужен автоматический gradient-based optimization camera/mesh.

**По умолчанию не ставить:** текущий OpenCV compare + semantic Blender edits проще, прозрачнее и стабильнее для MCP.

Источник: https://pytorch3d.org/tutorials/fit_textured_mesh

## 4. Hunyuan3D 2.1

**Назначение:** создать disposable proposal скрытой формы, затем вручную проверить/перестроить.

**Не считать:** истинной реконструкцией или production-ready web mesh без topology/scale/material review.

Официальный репозиторий указывает ориентировочно 10 GB VRAM для shape generation, 21 GB для texture и 29 GB для полного pipeline.

Источник: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1

## 5. TRELLIS.2

**Назначение:** альтернативный high-end image-to-3D proposal.

**Цена:** официальный репозиторий описывает 4B model, Linux и минимум 24 GB NVIDIA VRAM. Не нужен для обычной стилизованной иконки.

Источник: https://github.com/microsoft/TRELLIS.2

## Правило внедрения

1. Устанавливать каждый AI‑инструмент в отдельное окружение.
2. Не подключать его к системному prompt постоянно.
3. Сохранять provenance: какая часть наблюдалась, какая была сгенерирована.
4. Импортировать результат в Blender как reference/proposal, не как финальную истину.
5. После генерации всё равно выполнять silhouette, multiview, topology и GLB validation.
