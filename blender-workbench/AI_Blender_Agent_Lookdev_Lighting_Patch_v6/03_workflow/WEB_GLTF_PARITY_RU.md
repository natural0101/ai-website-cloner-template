# Blender → GLB → Web parity

## Что переносится надёжнее

- mesh geometry;
- transforms и hierarchy;
- UV;
- base color;
- metallic/roughness;
- normal;
- occlusion;
- emissive;
- поддерживаемые glTF material extensions;
- animation.

## Что нельзя считать автоматически перенесённым

- Blender compositor;
- AgX look/exposure;
- HDRI/world setup;
- reflection cards;
- Cycles bounce lighting;
- Blender area lights;
- произвольные procedural shader nodes;
- точный bloom/glare;
- точная прозрачность и refraction во всех браузерах.

Стандарт `KHR_lights_punctual` описывает directional, point и spot lights. Area lights и environment lighting требуют отдельной реализации в runtime или baking.

## Обязательная настройка Three.js

Пример для актуального Three.js:

```js
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.AgXToneMapping;
renderer.toneMappingExposure = 1.0;

scene.environment = prefilteredEnvironmentTexture;
scene.environmentIntensity = 1.0;
```

После этого отдельно настроить:

- environment rotation;
- toneMappingExposure;
- shadow maps;
- runtime lights;
- material extension support;
- texture color spaces.

## Правило сравнения

1. Сделать Blender EEVEE preview.
2. Сделать browser screenshot с той же камерой.
3. Сравнить side-by-side.
4. Исправлять runtime, а не Blender-asset, если Blender GLB уже корректен.
5. Не менять одновременно asset material и viewer exposure.

## Варианты для статичного hero

Если модель не должна свободно вращаться, допустимы:

- lightmap;
- baked AO;
- baked shadow plane;
- environment map, подготовленная под конкретный ракурс;
- hybrid 2.5D/3D presentation.

Для вращаемого 360° объекта lighting должен быть устойчивым во всех ракурсах.
