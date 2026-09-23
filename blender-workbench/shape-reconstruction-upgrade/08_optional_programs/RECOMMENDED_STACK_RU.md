# Рекомендуемый стек по уровням

## Уровень 0 — обязательно

- Blender 5.1.x;
- MCP Python execution;
- `shape_tools.py` + `shape_dispatcher.py`;
- Agent Skill;
- PNG render и structured validation.

## Уровень 1 — для референсов

- отдельный Python‑venv;
- NumPy;
- OpenCV headless;
- `reference_preprocess.py`.

Это оптимальная конфигурация для текущей задачи.

## Уровень 2 — только при сложной маске

- SAM 3.1 либо ручная segmentation программа;
- человек подтверждает mask и holes.

## Уровень 3 — только при необходимости придумывать hidden geometry

- Hunyuan3D 2.1 или TRELLIS.2 как proposal;
- результат не заменяет blockout/retopology/review.

## Уровень 4 — research/automation

- PyTorch3D differentiable fitting;
- оправдан только при большом повторяющемся наборе assets и наличии инженера, который поддерживает optimization pipeline.
