# Blender Donut 2025: выжимка для агента

Источник: https://www.youtube.com/playlist?list=PLjEaoINr3zgGUwGwXlj9kBe7TrVWNjkyv  
Курс: Blender Guru, Blender Donut Tutorial 2025, Blender 5.0, 8 частей.  
Данные: выжимка сделана по скачанным English captions, без публикации полного transcript.

## Цель

Собрать сцену: пончик с розовой глазурью и цветной посыпкой на тарелке, рядом кружка кофе, бетонный/кафе-стол, утреннее окно-световое пятно, финальный render в Eevee или Cycles.

## Горячие клавиши

- `MMB` orbit, `Shift+MMB` pan, wheel zoom.
- `Numpad .` focus selected.
- `Shift+A` add object.
- `G` move, `R` rotate, `S` scale.
- Axis locks: `G X`, `G Y`, `G Z`; plane lock: `G Shift+Z`.
- `Tab` Object/Edit mode.
- `1/2/3` vertex/edge/face select.
- `Ctrl+R` loop cut.
- `I` inset.
- `E` extrude.
- `Alt+click` select loop.
- `X` delete menu.
- `F2` rename.
- `Shift+D` duplicate, `Esc` keep duplicate in place.
- `Ctrl+E > Mark Seam` UV seams.
- `U > Unwrap > Angle Based` unwrap.
- `M` move to collection.
- `/` local view.
- `Ctrl+P > Keep Transform` parent.
- `F12` render.

## Pipeline

### 1. Base donut

1. Delete default cube.
2. `Shift+A > Mesh > Torus`.
3. In Add Torus/F9, make it donut-like: smaller overall scale than default, thicker tube, enough segments for later shaping.
4. Right click `Shade Smooth`.
5. Name object `donut`.

### 2. Mug and plate, optional but in course

1. Add a reference image if needed for mug proportions.
2. Add cylinder for mug body.
3. Shape cylinder with edit mode scaling, loop cuts, inset, solidify and subdivision surface.
4. Use `Solidify` for wall thickness.
5. Add `Subdivision Surface`; add loop cuts near rim/base to keep edges crisp.
6. Extrude handle from selected mug faces, shaping with `E`, `G`, `R`; if extrusion normals break, select faces and use `Shift+N`.
7. Use `Shade Smooth`.
8. Add plate from a flattened cylinder/mesh, add subdivisions/loop cuts/inset to shape rim.

### 3. Icing mesh

1. Select donut, `Shift+D`, then `Esc` so duplicate stays in place.
2. Rename duplicate `icing`.
3. Front view, edit mode, vertex select.
4. Enable X-Ray/wireframe before box-selecting, otherwise only visible front vertices are selected.
5. Select lower half of duplicate and delete `Faces`, not vertices, so center edge remains.
6. Add `Solidify` to icing; set offset outward, because default thickness goes inward.
7. Add randomness to icing edge:
   - edit mode;
   - temporarily hide solidify in edit view if needed;
   - enable proportional editing;
   - move boundary vertices mostly along Z to make an uneven handmade edge.
8. Create drips:
   - select two boundary vertices;
   - `E`, then `Z`, pull downward;
   - vary lengths and positions;
   - avoid repeating identical drip shapes.
9. Add `Shrinkwrap` targeting `donut`.
10. Modifier order: `Shrinkwrap` first, then `Solidify`, then `Subdivision Surface`.
11. Apply `Shrinkwrap`, then `Solidify`, then use `Subdivision Surface`/sculpt for more geometry.
12. Sculpt icing:
   - switch to Sculpting;
   - use `Inflate/Deflate` for thickness variation and sugar-like puffiness;
   - use `Grab` brush to move drips/edges;
   - keep the result organic, not laser-cut.

### 4. Lumpy donut form

1. Select donut and icing together.
2. `Shift+A > Lattice > Lattice Deform Selected` in Blender 5.0.
3. Edit lattice points to deform donut and icing together.
4. Add uneven bulges, especially around the ring and inner hole.
5. Add slight concavity/less puffiness around the inner middle, like a real fried donut.
6. Apply lattice to donut and icing when satisfied, then delete lattice helper.

### 5. Basic materials

1. Work in rendered/material preview.
2. Icing:
   - material color pink/strawberry;
   - lower roughness for glossy glaze, but not mirror-like;
   - add subsurface scattering for food-like translucency.
3. Donut:
   - warm brown/golden base color;
   - subsurface scattering;
   - do not use pure black or fully saturated colors.
4. Mug:
   - ceramic material;
   - roughness adjusted artistically, not blindly from texture.
5. Plate:
   - light ceramic/white material, slight gloss.
6. Table:
   - use plane with concrete/wood PBR material.

### 6. PBR texturing

1. For image/PBR textures, load Base Color first.
2. For complex materials use Shader Editor, not only material panel.
3. Normal map workflow:
   - add Image Texture with `_normal`;
   - set Color Space to `Non-Color`;
   - pass through `Normal Map` node;
   - connect to Principled BSDF `Normal`.
4. Roughness map:
   - add Image Texture `_roughness`;
   - set Color Space to `Non-Color`;
   - connect to `Roughness`.
5. Only Base Color should stay `sRGB`; technical maps should be `Non-Color`.
6. For donut displacement/height:
   - use displacement/height map if available;
   - in material settings use displacement/bump where supported;
   - keep scale low enough to avoid icing clipping through the donut.

### 7. UV unwrap

1. Flat plate/table: edit mode, select all, `U > Unwrap > Angle Based`; adjust UV scale/rotation.
2. Icing:
   - mark seam around existing cut/bottom edge;
   - add seam inside donut hole;
   - select all, `U > Unwrap > Angle Based`;
   - scale UVs until glaze texture size feels believable.
3. Mug:
   - apply texture first so stretching is visible.
   - mark seams where they will be hidden: handle joins, side near handle, inside/base rings.
   - enable `Live Unwrap` to see islands update while marking seams.
   - select islands with `L`, rotate/scale/move in UV editor.
   - use `Gridify`/straighten island where mug pattern needs clean alignment.
4. Coffee foam:
   - duplicate/extract circular top from mug mesh.
   - separate as `foam`.
   - unwrap from top view.
   - map UV island onto chosen foam in atlas texture.

### 8. Sprinkles

1. Place 3D cursor near top of donut: `Shift+Right Mouse`.
2. Add a small cylinder sprinkle.
3. Use low side count if needed, add `Subdivision Surface` for rounded ends.
4. Right click `Shade Smooth`.
5. Duplicate into several variants:
   - different lengths;
   - slight bends/twists;
   - different rotations;
   - do not make them identical.
6. Put all sprinkle variants into collection `sprinkles` with `M > New Collection`.
7. Hide the collection; it will be referenced by scatter.
8. Select `icing`.
9. Add modifier `Scatter on Surface`:
   - Instance mode: `Collection`;
   - collection: `sprinkles`;
   - enable `Pick Instance`;
   - use `Reset` transform if instances appear offset.
10. Adjust:
   - Density for amount;
   - Randomize rotation, especially around Y/axis along surface;
   - Surface Offset so sprinkles sit slightly above/in glaze, not buried.
11. Limit to top of icing:
   - switch icing to `Weight Paint`;
   - enable `Front Faces Only`;
   - set whole vertex group to 0 if needed, then paint red/weight 1 only where sprinkles should appear;
   - in `Scatter on Surface`, set `Distribution Mask` to the weight group, not `Density`.
12. Reduce intersections:
   - use Density method with `Poisson Disk`/disk distribution if available;
   - tweak `Minimum Distance`;
   - keep enough chaos so it does not look manually tweezer-placed;
   - change `Seed`;
   - set origin of sprinkle variants to geometry.
13. Keep scatter procedural unless final manual cleanup is absolutely needed.

### 9. Sprinkle material

1. Give all sprinkle variants one shared material: select variants, active one has material, `Ctrl+L > Materials`.
2. In Shader Editor:
   - add `Object Info`;
   - use `Random` output;
   - feed into `ColorRamp`;
   - feed ColorRamp to Base Color.
3. Set ColorRamp interpolation to `Constant`, not linear gradient.
4. Use a palette with one dominant sprinkle color plus a few accents; avoid equal rainbow noise.
5. Keep colors pastel/less saturated.
6. Add slight gloss and subsurface scattering; radius channels around 1, low scale.

### 10. Scene organization and parenting

1. Parent icing to donut: select icing, shift-select donut, `Ctrl+P > Keep Transform`.
2. Parent donut to plate.
3. Parent foam to mug.
4. Parent plate/mug to table plane if useful.
5. Organize lights/blockers into `lighting` collection.

### 11. Lighting

1. Target look: sunlit cafe / morning window.
2. Convert lamp to `Sun`.
3. Set sun strength around 10 as a starting point.
4. Use warm Kelvin/color temperature for morning sunlight.
5. Rotate sun; sun position does not matter, rotation does.
6. Add two plane blockers outside camera view to fake window strips/shadow shapes.
7. Add blue-ish sky fill:
   - duplicate light;
   - convert to point light;
   - place high;
   - large radius for soft shadows;
   - cool blue color.
8. Add bounce/fill light from opposite side/wall if shadows are too black.
9. Work on one light at a time by hiding others.

### 12. Camera and render

1. Frame donut as hero, mug secondary.
2. Use camera lock to view for composition, then disable lock.
3. Enable camera `Depth of Field`.
4. Focus object: icing/donut.
5. Blur background/table texture enough to guide viewer attention.
6. Eevee path:
   - fast and good enough;
   - increase samples if needed;
   - use light probe volume for bounce lighting;
   - bake light cache/probes;
   - enable jittered shadows for final render if shadows look too soft/fake.
7. Cycles path:
   - use for highest realism;
   - enable GPU in Preferences > System > Cycles Render Devices;
   - set render device to GPU;
   - use denoise;
   - expect slower renders.
8. Color management:
   - use Medium High/High Contrast look instead of default washed-out look;
   - avoid over-saturated material colors because contrast can blow them out.

## Agent acceptance checklist

- Donut is not a perfect torus: it has subtle lumpiness and fried-dough unevenness.
- Icing has varied edge, drips, thickness, and rounded sculpted blobs.
- Icing is shrinkwrapped/sits on donut without obvious floating gaps.
- Donut/icing use food-like subsurface material.
- PBR textures use correct color spaces.
- UVs are acceptable from camera view; visible stretching is fixed.
- Sprinkles are scattered only on top-visible icing, not underside.
- Sprinkle colors vary through shared material and ColorRamp, not manual per-object colors.
- Lighting has motivated warm sun, cool sky fill, and shaped shadows.
- Camera has depth of field and a clear focal point.
- Render is tested in Eevee fast path and optionally Cycles final path.
