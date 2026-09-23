# Optional tools

Базовый pipeline не требует AI image-to-3D.

- SAM 3.1: только initial segmentation mask, затем manual review.
- Depth Anything V2: rough relative-depth/layer hint, не точный mesh.
- Hunyuan3D 2.1/TRELLIS.2: disposable hidden-geometry proposal, не финальная истина.
- PyTorch3D: advanced differentiable fitting для повторяемого engineering pipeline.

Все работают во внешнем окружении, не внутри Blender Python.
