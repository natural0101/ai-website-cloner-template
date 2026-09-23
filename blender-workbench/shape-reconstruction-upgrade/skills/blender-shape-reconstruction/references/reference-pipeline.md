# Reference pipeline

1. Предпочитай alpha/manual masks.
2. Раздели перекрывающиеся semantic parts на masks.
3. Запиши back-to-front layer graph.
4. Внешним `reference_preprocess.py extract` создай contour JSON с holes.
5. В Blender вызови `shape.setup_reference_camera` с исходным resolution.
6. Импортируй `shape.import_contours` или `shape.import_layer_stack`.
7. Render `shape.render_silhouette`.
8. Внешним `compare` получи IoU, boundary F1, holes, bbox/centroid.
9. Исправляй camera/transform перед local shape.
10. RGB/material сравнивай только после silhouette gate.
