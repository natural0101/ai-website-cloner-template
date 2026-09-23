# Источники и оценка достоверности

Использованы преимущественно первичные источники: официальная документация Blender/Khronos/Three.js/Google Filament и исследовательская статья. Случайные блоги, SEO-статьи и непроверенные YouTube-рецепты не использовались как техническая основа.

## Уровень A — нормативные и официальные источники

### Blender Manual

1. Color Management / AgX
   - https://docs.blender.org/manual/en/latest/render/color_management.html
   - Зачем: view transform, exposure, highlight handling.

2. Light Objects
   - https://docs.blender.org/manual/en/latest/render/lights/light_object.html
   - Зачем: типы источников, size/soft shadows, power.

3. Principled BSDF
   - https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
   - Зачем: metallic, roughness, coat, transmission, emission.

4. Bevel Modifier
   - https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html
   - Зачем: физически читаемые края и specular highlights.

5. Cycles Sampling / Denoising
   - https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
   - Зачем: production sampling, adaptive sampling, denoise.

6. glTF 2.0 Exporter
   - https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
   - Зачем: экспорт материалов, текстур, света и ограничений.

### Khronos glTF 2.0

7. Core glTF 2.0 Specification
   - https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc
   - Подтверждает metallic-roughness PBR и каналы base color, normal, occlusion, emissive.

8. KHR_lights_punctual
   - https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_lights_punctual
   - Подтверждает перенос только directional, point и spot lights; area/environment не входят в это расширение.

### Three.js

9. WebGLRenderer
   - https://threejs.org/docs/#api/en/renderers/WebGLRenderer
   - Зачем: outputColorSpace, toneMapping, toneMappingExposure, shadows.

10. Scene
    - https://threejs.org/docs/#api/en/scenes/Scene
    - Зачем: environment, environmentIntensity, environmentRotation.

### Google Filament

11. Crafting Physically-Based Materials
    - https://google.github.io/filament/Materials.html
    - https://github.com/google/filament/blob/main/docs_src/src_mdbook/src/notes/material_properties.md
    - Зачем: физические диапазоны albedo, metallic 0/1, dielectric reflectance, roughness/clear coat.

## Уровень B — исследовательская работа

12. Thinking in Blender: Staged Executable Inverse Graphics with Vision-Language Models, 2026
    - https://arxiv.org/abs/2606.02580
    - Вывод, используемый в патче: агенту полезно независимо и последовательно оптимизировать geometry, materials, composition и lighting, а не менять всё одним шагом.
    - Ограничение: свежий preprint; это не нормативная документация и не гарантия качества конкретной сцены.

## Практический вывод

- PBR-параметры строятся по физическому типу поверхности, а не по «красивому цвету».
- Сначала форма и material response, затем свет и exposure.
- GLB не является контейнером полного Blender lookdev: viewer должен воспроизвести environment, tone mapping и неподдерживаемые источники.
- Любой preset в этом пакете — стартовая точка, а не универсально правильное значение.
