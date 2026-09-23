# Первичные источники

Проверено 22.06.2026. В пакет не включались случайные asset‑сайты, непроверенные prompt‑подборки или пересказы без исходного кода.

## Blender 5.1

1. Curve Geometry — bevel/extrude превращают curve в ribbon/tube/volume:  
   https://docs.blender.org/manual/en/latest/modeling/curves/properties/geometry.html
2. Voxel Remesh — создаёт новую manifold mesh по объёму; операция теряет часть исходных mesh data:  
   https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tool_settings/remesh.html
3. Remesh Modifier:  
   https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/remesh.html
4. Skin Modifier — построение skin вокруг vertex skeleton:  
   https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/skin.html
5. Metaballs — implicit surfaces для органических соединений:  
   https://docs.blender.org/manual/en/latest/modeling/metas/index.html
6. Sculpting tools:  
   https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/index.html
7. Cameras:  
   https://docs.blender.org/manual/en/latest/render/cameras.html
8. glTF 2.0 exporter:  
   https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
9. Blender Python API, Mesh remesh properties:  
   https://docs.blender.org/api/current/bpy.types.Mesh.html

## Контуры и метрики

1. OpenCV contours:  
   https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html
2. OpenCV contour hierarchy — parent/child topology для holes:  
   https://docs.opencv.org/4.x/d9/d8b/tutorial_py_contours_hierarchy.html
3. OpenCV morphology:  
   https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
4. PyTorch3D mesh fitting via differentiable silhouette rendering:  
   https://pytorch3d.org/tutorials/fit_textured_mesh

## Почему один вид неоднозначен

H. Kato, T. Harada, “Learning View Priors for Single-view 3D Reconstruction”, CVPR 2019. Авторы прямо описывают, что разные 3D‑формы могут иметь одинаковую проекцию и что результат, подогнанный под наблюдаемый вид, может быть неверен с ненаблюдаемых сторон:  
https://openaccess.thecvf.com/content_CVPR_2019/html/Kato_Learning_View_Priors_for_Single-View_3D_Reconstruction_CVPR_2019_paper.html

## Optional segmentation/depth

1. Meta SAM 3 / 3.1 official repository:  
   https://github.com/facebookresearch/sam3
2. Depth Anything V2 official repository:  
   https://github.com/DepthAnything/Depth-Anything-V2

## Optional image-to-3D proposals

1. Hunyuan3D 2.1 official repository:  
   https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1
2. TRELLIS.2 official repository:  
   https://github.com/microsoft/TRELLIS.2

## Вывод из источников, реализованный в пакете

- curves подходят для управляемых tapered limbs/fingers;
- voxel remesh подходит для мягкого объединения, но требует сохранённой source copy;
- contour hierarchy необходимо сохранять для holes;
- silhouette fitting измеряет наблюдаемый вид, а не истинность скрытой геометрии;
- optional segmentation/depth/image‑to‑3D используются только как aids/proposals;
- GLB требует отдельной topology/material/export проверки.
