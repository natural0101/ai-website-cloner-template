# Установка reference preprocessing

Запускать вне Blender.

## Windows PowerShell

```powershell
py -3.12 -m venv .venv-reference
.\.venv-reference\Scripts\python -m pip install --upgrade pip
.\.venv-reference\Scripts\python -m pip install -r requirements.txt
```

## macOS/Linux

```bash
python3 -m venv .venv-reference
.venv-reference/bin/python -m pip install --upgrade pip
.venv-reference/bin/python -m pip install -r requirements.txt
```

## Проверка

```bash
python reference_preprocess.py info ../demo/masks/combined.png
```

## Не делать

Не устанавливать OpenCV, PyTorch, SAM или image‑to‑3D модели в Python Blender. Передавайте между процессами только PNG/JSON/GLB.
