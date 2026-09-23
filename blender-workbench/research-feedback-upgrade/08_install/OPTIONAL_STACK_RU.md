# Опциональный стек

| Инструмент | Когда нужен | По умолчанию |
|---|---|---|
| OpenCV venv | masks, contours, overlay | Уже предусмотрен v3 |
| Local embeddings + Qdrant | сотни/тысячи verified examples | Не ставить сейчас |
| Git/LFS | versioning больших `.blend`/renders | По желанию |
| Container/отдельный OS user | untrusted arbitrary code | Рекомендуется для рискованных workflows |
| External 3D generator | быстрый imported draft | Только явно |
| Exact mesh distance/collision library | инженерные contact tolerances | Только при необходимости |

Главное улучшение — не новая программа, а discipline процесса и проверяемые records.
