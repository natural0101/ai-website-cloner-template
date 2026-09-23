// Minimal lookdev baseline for a current Three.js GLB viewer.
// Integrate with your existing renderer, camera, controls and GLTFLoader.

renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.AgXToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Load an HDR environment, prefilter it with PMREMGenerator, then:
scene.environment = prefilteredEnvironmentTexture;
scene.environmentIntensity = 1.0;
scene.environmentRotation.set(0, 0.35, 0);

// Do not assume Blender Area lights or World/HDRI were stored in the GLB.
const key = new THREE.DirectionalLight(0xd9e6ff, 2.0);
key.position.set(-5, -4, 8);
key.castShadow = true;
scene.add(key);

const warmPractical = new THREE.PointLight(0xffb56b, 18.0, 8.0, 2.0);
warmPractical.position.set(0, 0, 3);
warmPractical.castShadow = true;
scene.add(warmPractical);

// Calibrate with a browser screenshot beside the approved Blender reference.
// Change one factor at a time: environment -> runtime lights -> exposure.
