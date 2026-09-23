# Blender Lifehacks Distilled From Shorts

This file is the reusable part: each item is written as a production move, not as a video summary.

## Animation

### BH-001: Carousel Phase Offset

Sources: [001](https://www.youtube.com/shorts/Dhwrw2RtD8I), [002](https://www.youtube.com/shorts/994732mCNDA), [035](https://www.youtube.com/shorts/k617xfb4QcM)

Use one repeated action with per-object phase offsets instead of hand-keying every duplicate. This is ideal for cards, coins, UI tiles, product variants, flying papers, bullets, petals, and orbiting icons.

Implementation habit: store `phase`, `orbit_radius`, `spin_speed`, and `showcase_frame` as custom properties or script constants.

### BH-002: Showcase Beat

Sources: [004](https://www.youtube.com/shorts/eIExezP647w), [032](https://www.youtube.com/shorts/9-6LbQXFc0Y)

An animation feels more expensive when every hero object gets a short front-facing pause. Add a support pose before and after the showcase pose so interpolation does not blur the moment.

### BH-003: Snappy Extremes

Sources: [016](https://www.youtube.com/shorts/S4PpnlE-qoc), [024](https://www.youtube.com/shorts/iueVZuQGckU)

For punchy motion, push extremes close together in time, then let the settle take longer. Keep amplitude controllable from one value so the same rig can be dramatic or subtle.

### BH-004: Hinge Before Deform

Source: [046](https://www.youtube.com/shorts/L1DPOuZ_iy4)

For boxes, cards, lids, panels, wings, and book pages, set real pivot origins and parent/empty controls first. Animate hinge rotation before considering mesh deformation.

### BH-005: Loop Closure Check

Source: [047](https://www.youtube.com/shorts/EYH9U22rN4Q)

For looping assets, compare first and last frame visually and numerically. A loop is not safe just because frame 1 and frame N have keyframes.

## Modeling

### BH-006: Bevel + Weighted Normals First

Sources: [005](https://www.youtube.com/shorts/NVEuv2WmAyY), [010](https://www.youtube.com/shorts/zn7lmi6KzJU), [023](https://www.youtube.com/shorts/85A4TYOAQmo)

Thin hard-surface objects look cheap until their edges catch light. Add small bevels and weighted normals before spending time on decorative details.

### BH-007: Real Thickness For Flat Objects

Sources: [006](https://www.youtube.com/shorts/zbvn6t9ik9E), [049](https://www.youtube.com/shorts/na2lGLE09XY)

Cards, cloth panels, stickers, paper, screens, and shells need small physical thickness. Even `0.01-0.04m` can make a web GLB read as real.

### BH-008: Decal Planes Are Legit Geometry

Sources: [003](https://www.youtube.com/shorts/8-ET9L_VDkk), [009](https://www.youtube.com/shorts/E4jKNvaY12s)

Flat planes are not a shortcut failure when they are intentional: use them for decals, anime strokes, UI layers, parallax panels, motion lines, and hair-card-like silhouettes.

### BH-009: Curves For Fast Organic Lines

Sources: [008](https://www.youtube.com/shorts/ofjmOXSUBVQ), [038](https://www.youtube.com/shorts/FLnvwgoH8RA)

Use bevel-depth curves for cables, hair tufts, energy strokes, rims, glass outlines, and motion streaks. Convert only when topology must be edited.

### BH-010: Proportional Editing Before Sculpt

Source: [048](https://www.youtube.com/shorts/_JjoZ21z8fg)

For organic silhouette changes, try proportional editing/falloff deformation before jumping into dense sculpting. It keeps forms editable and easier to QA.

### BH-011: Hard Surface From Big Forms

Sources: [011](https://www.youtube.com/shorts/NHHn4zMTqKA), [023](https://www.youtube.com/shorts/85A4TYOAQmo)

Block silhouette and primary bevel language first. Add panels/cuts after the object reads at thumbnail size.

## Materials

### BH-012: Reflection Cards For Gloss

Source: [018](https://www.youtube.com/shorts/NgT5WSa9Hfk)

Glossy materials often need bright shapes to reflect. Add off-camera white/colored cards or area lights so plastic, glass, metal, and lacquer have readable highlights.

### BH-013: Texture Stretch Is Geometry/UV Debt

Source: [034](https://www.youtube.com/shorts/l28g6DgYduU)

When textures stretch, inspect UV scale, object scale, and face aspect ratio before changing shader settings. Apply scale and use consistent texel density.

### BH-014: Material Mixing With Masks

Source: [026](https://www.youtube.com/shorts/0B4dDLAkpI4)

Mix two materials with masks/noise/attributes when possible. It gives wear, gradients, dirt, and local variation without duplicating mesh parts.

### BH-015: Cheap Material Variation Layer

Source: [022](https://www.youtube.com/shorts/ez3bLnCcaIE)

Keep materials node-grouped or parameterized so one texture/color swap can create variants quickly. Useful for decks, product lines, icons, and cloned objects.

## Lighting And Lookdev

### BH-016: Key/Fill/Rim Before Decoration

Sources: [013](https://www.youtube.com/shorts/LWjr-PAUfFM), [021](https://www.youtube.com/shorts/Ta82egt3TVE), [029](https://www.youtube.com/shorts/Z_PqXnv1wrE)

Start with a named light rig: key defines form, fill controls shadow density, rim separates silhouette. Only then add colored accents.

### BH-017: Black Background Needs Edge Separation

Source: [036](https://www.youtube.com/shorts/RWGvTNSSwuM)

On black backgrounds, subject edges disappear unless rim/back lights draw the contour. Always inspect side and thumbnail views.

### BH-018: Light Type By Job

Source: [033](https://www.youtube.com/shorts/Il4snUma2MQ)

Use area lights for soft product lighting, point lights for local glow, spot lights for directed theatrical emphasis, and sun lights for broad parallel direction.

### BH-019: Before/After Lighting Renders

Source: [044](https://www.youtube.com/shorts/Vfe94NzAyL0)

Keep a lighting comparison render whenever changing scene light. This catches "more light but less form" regressions.

### BH-020: Track Highlights To Moving Heroes

Source: [050](https://www.youtube.com/shorts/OLLWJTQSNnY)

When a hero object moves, constrain a small rim/kicker light to track it. This preserves readable highlights through animation.

## NPR / Anime

### BH-021: Rim Color Is An Anime Shortcut

Sources: [007](https://www.youtube.com/shorts/hFuXAjpoe_0), [037](https://www.youtube.com/shorts/srMwm1Z1qIQ), [045](https://www.youtube.com/shorts/eqsk4Ss1WfA)

For anime/NPR look, combine simple base colors with aggressive colored rim and controlled ramps. Do not over-texture every surface.

### BH-022: Manga Motion Lines As Geometry

Sources: [008](https://www.youtube.com/shorts/ofjmOXSUBVQ), [009](https://www.youtube.com/shorts/E4jKNvaY12s)

Build speed lines from tapered planes/curves with emissive or high-contrast materials. Keep them behind or beside the hero object so they add energy without clutter.

## Camera And Export

### BH-023: Camera Motion After Framing

Source: [043](https://www.youtube.com/shorts/lXVy1j_bu1I)

Lock hero framing first, then add subtle camera drift/noise. Camera tricks cannot save an unreadable composition.

### BH-024: Render Loop QA

Sources: [039](https://www.youtube.com/shorts/b3Q6Xa4RU88), [047](https://www.youtube.com/shorts/EYH9U22rN4Q)

For animation deliverables, export a short frame strip/contact sheet before final video or GLB. It is faster to catch stutters in 6-8 still frames.

### BH-025: Web GLB Budget Gate

Source: [023](https://www.youtube.com/shorts/85A4TYOAQmo)

After applying modifiers, check triangle count and remove hidden dense helpers before GLB export. Keep source objects in the `.blend`, but export only production objects.

## Micro Habits

### BH-026: Batch Material Application

Source: [041](https://www.youtube.com/shorts/Jlb_oG2aYe4)

Name material families consistently (`Card_Front_*`, `FX_*`, `Metal_*`) so scripts can batch-assign and audit them.

### BH-027: Grounding Check

Source: [030](https://www.youtube.com/shorts/HH4gsnsqJUM)

For grounded objects, add a tiny contact shadow or base plane during QA. Floating errors show up immediately.

### BH-028: Queue Unknowns Honestly

Sources: this log, YouTube search snippets, failed `yt-dlp` search attempts.

Do not promote a title-only video into a trusted trick. Mark it as `queued` until visual review or transcript/description confirms the technique.

## Geometry Nodes

### BH-029: Frame Node Graphs Early

Sources: [055](https://www.youtube.com/shorts/0iztwYK70-8), [071](https://www.youtube.com/shorts/3R0bd1h_Ads), [100](https://www.youtube.com/shorts/Bya53QEvsT4)

Frame and label node groups while the graph is still small. A tidy procedural graph is faster to debug than a clever unlabeled one.

### BH-030: Scatter As First-Class Dressing

Source: [059](https://www.youtube.com/shorts/mW04KpCSiQw)

Use `Distribute Points on Faces` as the baseline for rocks, sparkles, labels, rivets, leaves, screws, and background detail. Keep seed/scale/density exposed.

### BH-031: Texture-Driven Displacement

Source: [063](https://www.youtube.com/shorts/r95bSiFV8YI)

Use texture -> vector math -> `Set Position` for quick non-destructive surface variation. Bake or apply only when export/runtime requires it.

### BH-032: Procedural Orbit And Rotation Limits

Sources: [072](https://www.youtube.com/shorts/pDbYQCGn7oI), [083](https://www.youtube.com/shorts/JFuwOnZcg0I)

For showcases, orbit camera/objects procedurally, then clamp or constrain rotation so the asset never shows its weakest angle for too long.

## Camera

### BH-033: Compose With A Live Preview

Sources: [052](https://www.youtube.com/shorts/C3vtjVPeaIw), [076](https://www.youtube.com/shorts/49uewowIGqA)

Keep camera/wireframe preview and composition guides visible while blocking. It prevents beautiful models from landing in weak frames.

### BH-034: Lock/Pilot Camera For Blocking

Sources: [056](https://www.youtube.com/shorts/EX4rjWaLB44), [060](https://www.youtube.com/shorts/buI4Gd4wiyE), [080](https://www.youtube.com/shorts/aY3KWEed6v8), [084](https://www.youtube.com/shorts/Z5RvnzHNpUo)

Use lock-to-view, pilot camera, and move-camera-to-view for first framing. Fine numeric camera transforms come after the shot already reads.

### BH-035: Save Preview Cameras

Sources: [064](https://www.youtube.com/shorts/vwlGKibalMQ), [068](https://www.youtube.com/shorts/Q7aCfGR_jmk)

Create named preview cameras: `CAM_Hero`, `CAM_Ortho`, `CAM_Isometric`, `CAM_SideQA`. This makes render QA repeatable.

## Rigging

### BH-036: IK Before Fancy Controls

Sources: [053](https://www.youtube.com/shorts/77RvfjaWvRQ), [065](https://www.youtube.com/shorts/3fOyNYvO6Kc)

For limbs, cables, fingers, mechanical arms, and props, add basic IK first. Custom controls are only worth it after the deformation test passes.

### BH-037: Test Extreme Poses Early

Sources: [069](https://www.youtube.com/shorts/YT095f5ahlQ), [077](https://www.youtube.com/shorts/PmDKsV7yd8k), [085](https://www.youtube.com/shorts/qzjXJvs5QSw)

Rig deformation quality is judged at the worst pose, not the bind pose. Test elbows, shoulders, knees, hinges, and squash before adding final texture detail.

## UV And Textures

### BH-038: UV Grid Before Texture Art

Sources: [058](https://www.youtube.com/shorts/0Gi3eKo6jcE), [082](https://www.youtube.com/shorts/DwuuRzXyFiI), [090](https://www.youtube.com/shorts/GC9ip1H-DjY)

Put a UV/checker grid on the model before painting or assigning final maps. Stretched UVs are easiest to fix while the material is still boring.

### BH-039: Preserve UVs While Modeling

Sources: [062](https://www.youtube.com/shorts/tS63p4eOWV8), [074](https://www.youtube.com/shorts/K_FMb9FiQbo), [086](https://www.youtube.com/shorts/SdxjjcSG4tE)

Use Live Unwrap, correct transform options, and precise island alignment when editing textured meshes. This prevents late-stage label and normal-map drift.

## Simulation And Sculpt

### BH-040: Art-Direct Simulations With Guides

Sources: [091](https://www.youtube.com/shorts/MfH1ogizzyw), [094](https://www.youtube.com/shorts/X_-E8-3ZM5A), [097](https://www.youtube.com/shorts/qpIwTG63qJI)

Use particles, curve guide fields, and proxy objects to steer simulations. Simulations become production-friendly when their motion has handles.

## Session 002 Additions

### BH-041: Curve Direction Is Data

Sources: [101](https://www.youtube.com/shorts/uGEqAQQxtLM), [097](https://www.youtube.com/shorts/qpIwTG63qJI)

For bevel taper, path animation, curve guides, and particle flow, inspect/invert curve direction before blaming the effect. Direction errors often look like broken timing or backwards scattering.

### BH-042: Stylized Strands From Curves

Sources: [102](https://www.youtube.com/shorts/5by_eD6EM44), [103](https://www.youtube.com/shorts/XlXLyZH5f38)

Use editable curves with bevel depth or bevel objects for hair, energy strokes, decorative lines, cables, and motion ribbons. It keeps silhouette flexible until late.

### BH-043: Alignment Before Beauty

Sources: [104](https://www.youtube.com/shorts/wedGVKPYcEM), [142](https://www.youtube.com/shorts/_D7Jp9r3xXA)

Straighten edges, align axes, and clean obvious skew before bevels/materials. Beautiful shaders exaggerate sloppy base geometry.

### BH-044: Choose Hole-Cutting By Final Need

Sources: [106](https://www.youtube.com/shorts/BJggard5lYk), [133](https://www.youtube.com/shorts/TdJgL8UYz_w)

Use booleans for speed tests, knife/inset/topology for editable hero surfaces, and grid fill/retopo after cuts that must deform or export cleanly.

### BH-045: Export Mesh And Collision Mesh Are Different Jobs

Sources: [108](https://www.youtube.com/shorts/rC3h1vumRxQ), [122](https://www.youtube.com/shorts/XMDuKCNyg-U)

For engine or web work, create separate visual meshes, collision/proxy meshes, and export filters. Do not assume one mesh should do every job.

### BH-046: Optimization Is A Stage, Not A Panic Button

Sources: [110](https://www.youtube.com/shorts/kPhK9KZJ8Ok), [113](https://www.youtube.com/shorts/8x1pfwkERC8), [119](https://www.youtube.com/shorts/b-UQ6ye4jf0)

Use decimate, limited dissolve, proxy simplification, and render settings deliberately after the asset reads. Avoid optimizing before silhouette and material decisions are stable.

### BH-047: Scale Discipline

Sources: [115](https://www.youtube.com/shorts/kxCumNumvdY), [137](https://www.youtube.com/shorts/IhGbdL5cBJI)

Apply scale and keep object dimensions sane before modifiers, physics, lighting, and export. Many bevel, mirror, array, cloth, and normal issues are scale debt.

### BH-048: Mirror And Array Before Manual Duplication

Sources: [121](https://www.youtube.com/shorts/B1Vxh2-8cpY), [125](https://www.youtube.com/shorts/jdWcYsBkGsQ), [134](https://www.youtube.com/shorts/aAuR8Xj0NEM)

Use Mirror for symmetry and Array/Object Offset for repeated parts. Manual duplicates are fine only after the repeat pattern is approved.

### BH-049: Turntable As QA

Source: [124](https://www.youtube.com/shorts/uafPg27H4ms)

A model spin is not just presentation; it reveals bad backs, weak side views, inconsistent materials, and pivot mistakes quickly.

### BH-050: Origins Are Animation Controls

Source: [130](https://www.youtube.com/shorts/6xq2n7rtpGQ)

Before hinge, spin, mirror, array, or follow-path work, set origins intentionally. Origin mistakes are animation bugs waiting to happen.

### BH-051: File Hygiene Before Export

Sources: [120](https://www.youtube.com/shorts/EB1ACmAd5G8), [128](https://www.youtube.com/shorts/UoTWjbn13ms)

Autosave recovery, action cleanup, unused object cleanup, and export flags are part of production. A clean file prevents accidental tracks and stale test meshes in GLB.

### BH-052: Normals First When Shadows Look Wrong

Sources: [131](https://www.youtube.com/shorts/KMM8-bjcRsg), [141](https://m.youtube.com/shorts/zwmPKtUpqr0), [143](https://www.youtube.com/shorts/OYBC4mN5-_s)

When shading breaks, inspect normals, scale, smoothing, and weighted normals before changing lights. Bad normals can masquerade as bad materials.

### BH-053: Use World/Sky Lighting Carefully

Sources: [135](https://www.youtube.com/shorts/C6ueuuPOPsg), [144](https://www.youtube.com/shorts/1MtwlSJUwMI)

World/sky lighting and emissive materials help mood, but they can flatten hero forms. Keep separate controllable key/rim lights for silhouette and material highlights.

### BH-054: Node Readability Is Production Speed

Sources: [149](https://www.youtube.com/shorts/_fPjLfyQx9M), [150](https://www.youtube.com/shorts/QOoTvCB08sk), [055](https://www.youtube.com/shorts/0iztwYK70-8)

Frame node groups, keep labels visible, and use color ramps as named art-direction controls. A shader graph should explain itself when reopened later.

### BH-055: Variation For Repeated Assets

Sources: [148](https://www.youtube.com/shorts/nyjp2B3q_6Y), [125](https://www.youtube.com/shorts/jdWcYsBkGsQ)

When arrays/scatters create repeats, add controlled per-object scale, rotation, or color variation. This keeps repeated detail from looking copy-pasted.

## Session 003 Additions

### BH-056: Pin Cloth Before Simulating

Sources: [151](https://www.youtube.com/shorts/EsIdAdj-sXw), [162](https://www.youtube.com/shorts/GD7L9nLj0UY)

Cloth needs vertex groups or painted weights before simulation. Pinning gives the artist a handle on what should stay anchored and what should fold.

### BH-057: Cloth Is A Shot Asset

Sources: [156](https://www.youtube.com/shorts/Nl-PvHCotx4), [167](https://www.youtube.com/shorts/vL08qJBlcfQ), [171](https://www.youtube.com/shorts/uGXVQfpTxW4)

Treat cloth and tearing as shot-specific cached results. Keep source planes/weights, but export cleaned final mesh unless runtime cloth is explicitly required.

### BH-058: Grease Pencil As Planning Layer

Sources: [155](https://www.youtube.com/shorts/MFpKAaYoeWw), [157](https://www.youtube.com/shorts/4HBNqa5DJZw), [163](https://www.youtube.com/shorts/gz9MpnmHufI)

Use Grease Pencil or curve strokes to plan motion, pose arcs, outlines and timing offsets inside 3D space before committing geometry.

### BH-059: Bake Readability, Not Everything

Sources: [152](https://www.youtube.com/shorts/09yHHFWXfms), [153](https://www.youtube.com/shorts/eOHjXydeW3o), [165](https://www.youtube.com/shorts/CsnrUsoic7M)

Bake AO/normal/detail maps when they improve readability or real-time export. Baking should solve a specific delivery problem, not become default complexity.

### BH-060: Reference Video Is Temporary Scaffolding

Source: [172](https://www.youtube.com/shorts/b3tuXktAVnU)

Import video for timing or pose reference, then record what was used and remove/disable it from final export. Hidden media dependencies make files brittle.

### BH-061: Procedural Data Needs Named Controls

Sources: [173](https://m.youtube.com/shorts/729leU4YFRg), [174](https://m.youtube.com/shorts/MpbW0Ts3SyM), [183](https://www.youtube.com/shorts/KOW3GV9i-EM)

Geometry Nodes effects should expose seed, threshold, density, size, direction, and timing. A procedural effect without named controls is hard to art-direct.

### BH-062: HDRI Is Light, Not The Whole Look

Sources: [176](https://www.youtube.com/shorts/yE5-X7b4gL0), [179](https://www.youtube.com/shorts/g_mknP_hvDU)

Use HDRI for fast environmental fill/reflections, but separate the visible background from the lighting and keep key/rim lights for hero shape.

### BH-063: DOF As Hierarchy

Source: [175](https://www.youtube.com/shorts/9Ym1lqEIn-E)

Depth of field should clarify the hero plane. If DOF is hiding unreadable geometry or weak composition, fix the asset/camera first.

### BH-064: Instance Rotation And Random Transform

Sources: [180](https://m.youtube.com/shorts/cDyB89b4wvA), [199](https://www.youtube.com/shorts/BiUQlPXkYFY)

When scattering or duplicating props, randomize transform within a believable range. Variation should break repetition without making layout chaotic.

### BH-065: Product Shadows Ground Scale

Sources: [184](https://m.youtube.com/shorts/zEcECEO8cC0), [188](https://www.youtube.com/shorts/mG7Tw1Jvm74), [193](https://www.youtube.com/shorts/5Sia-Tyi2H4)

Contact shadows and shadow catchers make objects feel physically present. Use them before adding more decorative props.

### BH-066: Choose The Renderer By Constraint

Source: [185](https://www.youtube.com/shorts/-FpHe2AeM3c)

Use Eevee/viewport for speed and iteration, Cycles for path-traced glass/shadows/reflections when final quality needs it. Do not mix expectations.

### BH-067: Glass Needs Both Material And Render Settings

Sources: [186](https://www.youtube.com/shorts/_6nQyHwfXk8), [189](https://www.youtube.com/shorts/r1DWDlyfkkE), [194](https://www.youtube.com/shorts/rqLj-W9C3Mk), [195](https://www.youtube.com/shorts/DVcQwli-WOA)

Glass readability comes from IOR/transmission/alpha/absorption plus enough bounces and reflections. If glass looks dead, inspect render settings too.

### BH-068: Physical Water Defaults

Sources: [192](https://www.youtube.com/shorts/6BnwBKsK9YE), [178](https://www.youtube.com/shorts/A4UFCoN4I3I)

For water, start from physical IOR near `1.333`, then add scale-appropriate roughness, droplet size variation and contact highlights.

### BH-069: Two-Sided Material Logic

Source: [197](https://www.youtube.com/shorts/hd9QF16-42s)

Cards, leaves, stickers, cloth and thin panels often need different front/back treatment. Model or shader that distinction intentionally.

### BH-070: Snap Surface Details To The Surface

Sources: [198](https://www.youtube.com/shorts/uzXwNom-7aY), [200](https://www.youtube.com/shorts/gRH3bjsFl1A)

Use Mapping controls for texture scale and face-aligned snapping for physical detail. Surface detail should follow the surface, not float above it.

## Session 004 Additions

### BH-071: Constraints Are Relationships

Sources: [201](https://www.youtube.com/shorts/ySsTgrXUxAw), [204](https://www.youtube.com/shorts/FP1meazZPRc), [227](https://www.youtube.com/shorts/7fHAo1vMmiQ)

Use constraints to express relationships like track, copy, limit, hold, and aim. Copy reusable constraint setups across repeated parts, then inspect the stack after version/addon changes.

### BH-072: Follow Path Is A Motion Rail

Sources: [205](https://www.youtube.com/shorts/u1jAqZyxsNA), [209](https://www.youtube.com/shorts/eEiqegVMQsw), [220](https://www.youtube.com/shorts/ITaCBUVHeQw), [233](https://www.youtube.com/shorts/mLvvWbekVAQ)

For camera or object movement, separate path shape, path direction, origin, and timing/offset. That makes the rail reusable and debuggable.

### BH-073: Drivers Encode Ratios

Sources: [203](https://www.youtube.com/shorts/85oospWTIQ8), [207](https://www.youtube.com/shorts/TGlnao7RtI0), [211](https://www.youtube.com/shorts/YZ79wtyTdYI), [226](https://www.youtube.com/shorts/rgclr47bNQ4)

Use drivers when values have a mathematical relationship, such as gears, wheels, linked indicators, or procedural walk previews. Do not hand-key linked quantities.

### BH-074: Shape Keys Need Stable Topology

Sources: [202](https://www.youtube.com/shorts/R4PfeQLNhzc), [206](https://www.youtube.com/shorts/61NX9hgRrAc), [210](https://www.youtube.com/shorts/ZRLQ6PT5c5g), [234](https://www.youtube.com/shorts/jIUgfd0kM8U)

Shape keys are powerful when vertex order/topology stays identical. Name each key for the intended state: blink, squash, bend, inflate, damage, open.

### BH-075: Shape Keys Can Be Rig Controls

Sources: [217](https://www.youtube.com/shorts/ovSmvJEVvzE), [221](https://www.youtube.com/shorts/AjYB8IocvtE), [225](https://www.youtube.com/shorts/pUbxiZ6tLTE)

Drive shape-key values from bones, empties, sliders, or other animation values to make morphs reusable and art-directable.

### BH-076: Bake Constraints Before Fragile Export

Sources: [215](https://www.youtube.com/shorts/77cKd6_P_a0), [219](https://www.youtube.com/shorts/DFFmoJgXWFo), [222](https://www.youtube.com/shorts/rDLWmYrCP1w)

Constraints/addons are authoring tools. If the target viewer/export path cannot evaluate them, bake to ordinary keyframes and keep the rig source in the `.blend`.

### BH-077: Pickup And Hold Are Ownership States

Sources: [208](https://www.youtube.com/shorts/wYjb-qeiuUM), [235](https://www.youtube.com/shorts/wk1731VND_s)

For characters or mechanical arms holding objects, plan the moments where object ownership changes. Use Child Of/constraints or baked handoffs instead of messy reparenting.

### BH-078: Physics Constraints Need Real Scale

Source: [232](https://www.youtube.com/shorts/brLzSu0N22E)

Rigid-body constraints depend heavily on scale, pivots and limits. Put those in the scene graph before trusting a simulation.

### BH-079: Compositor Glow Is A Separate Stage

Sources: [239](https://www.youtube.com/shorts/Le1sDpC5O5I), [240](https://www.youtube.com/shorts/902DtSJeJTs), [242](https://www.youtube.com/shorts/RyyH3-fFAUw), [247](https://www.youtube.com/shorts/Farai3yQSvg)

Emission material, bloom/glare threshold and final exposure are separate controls. Keep the base object readable without glow, then add glow as a style pass.

### BH-080: Mist/Depth Passes Are Review Outputs

Sources: [238](https://www.youtube.com/shorts/6WT_68xxKmw), [241](https://www.youtube.com/shorts/Qpd_KEby7Ik), [243](https://www.youtube.com/shorts/S4a7-xC8RW8), [245](https://www.youtube.com/shorts/zHsCOA-bUFE)

For fog, atmosphere and depth blur, render or store mist/depth evidence separately. Depth effects should clarify spatial layering, not hide weak composition.

### BH-081: Volumetrics Need Bounds

Sources: [237](https://www.youtube.com/shorts/QhJ_QsH-6sM), [241](https://www.youtube.com/shorts/Qpd_KEby7Ik)

Use simple bounded volumes/cubes for fog beams and keep density low enough that silhouettes survive. Volumetrics are mood, not a replacement for lighting.

### BH-082: Edge Glow Must Not Carry The Design

Sources: [244](https://www.youtube.com/shorts/odQk2-75aO8), [249](https://www.youtube.com/shorts/12utzwu3DBc)

Glow outlines, lightning and FX controllers are secondary. If the base silhouette is weak, FX makes the problem louder.

### BH-083: Camera Rail Can Release

Sources: [224](https://www.youtube.com/shorts/-916JkSrOkk), [236](https://www.youtube.com/shorts/cc7J5LM1hTY)

Camera movement can start on a rail and then transition to free motion. Plan the release beat instead of fighting the constraint mid-shot.

### BH-084: Light Iteration Needs Fast Knobs

Sources: [248](https://www.youtube.com/shorts/UUBZfQomeNw), [250](https://www.youtube.com/shorts/_rmmaixanqQ)

Reflective/shiny materials are only readable under meaningful reflections and controllable light values. Keep light energy, size, spread and reflection cards easy to adjust.

### BH-085: Troubleshooting Motion Starts With Origins

Sources: [213](https://www.youtube.com/shorts/6xni9VLC4hs), [216](https://www.youtube.com/shorts/Mj-FrRc29YU), [229](https://www.youtube.com/shorts/o-mrEdE6QmI)

When follow-path, driver or constraint motion behaves strangely, inspect origin, scale, curve direction, offset, and evaluation order before rebuilding the rig.

## Session 005 Additions

### BH-086: Retopo Is A Translation Layer

Sources: [251](https://www.youtube.com/shorts/A8UKyOZe5R0), [259](https://www.youtube.com/shorts/HmIeYfdmm34), [281](https://www.youtube.com/shorts/X_Em-IPAlQc), [284](https://www.youtube.com/shorts/38Ekj5Keam8)

Retopology translates a dense sculpt into clean editable flow. Judge it by silhouette, edge flow, deformation paths and UV readiness, not just lower triangle count.

### BH-087: Shrinkwrap Is Projection, Not Magic

Sources: [253](https://www.youtube.com/shorts/odlW0fuBh04), [257](https://www.youtube.com/shorts/JOcnno5eGIE), [265](https://m.youtube.com/shorts/JFU4M8358Ls), [269](https://www.youtube.com/shorts/KMM8-bjcRsg)

Use Shrinkwrap for retopo cages, labels, clothes and decals, but check offsets, normals and target surface quality. Projection inherits target problems.

### BH-088: Remesh By Purpose

Sources: [252](https://www.youtube.com/shorts/Mz0hrH50Ogc), [264](https://www.youtube.com/shorts/oyHzUkPMRZo), [268](https://www.youtube.com/shorts/lcJkDbvVgXY), [272](https://www.youtube.com/shorts/DxcthXYiM6s)

Voxel remesh unifies sculpt volumes; quad remesh aims toward editable flow; stylized voxel remesh is a look. Choose before clicking.

### BH-089: Scale Controls Remesh Density

Sources: [256](https://www.youtube.com/shorts/y8-MaUOQt20), [276](https://m.youtube.com/shorts/8oPN9p2R9iI)

Apply scale and set feature-size targets before remeshing. Remesh quality is partly a scale problem.

### BH-090: UV Seams Are Strategy

Sources: [254](https://www.youtube.com/shorts/UhJZ0fIg4KY), [258](https://www.youtube.com/shorts/SvLz6hTJ2mc), [262](https://www.youtube.com/shorts/VDVNYT4ViVU), [270](https://www.youtube.com/shorts/Tn4E457iEO0)

Place seams where distortion, visibility and construction logic are balanced. Good seams are managed, not invisible by wish.

### BH-091: Seam-Driven Detail Can Help

Sources: [274](https://www.youtube.com/shorts/rEAWyRI2sPE), [277](https://www.youtube.com/shorts/I1Y_vA4DeTI)

Use seams/face sets as guides for wrinkles, color changes or cloned base colors. Let UV structure support detail placement.

### BH-092: Generated Topology Is Draft Topology

Sources: [263](https://www.youtube.com/shorts/n8Eb8TCr0sQ), [271](https://www.youtube.com/shorts/914PGfj5pOo), [278](https://www.youtube.com/shorts/8B_8IEeEboc)

Auto-retopo and retopo addons are drafting tools. Validate deformation, UVs and export topology before calling them production-ready.

### BH-093: Bad Topology Needs A Named Cleanup Stage

Sources: [275](https://www.youtube.com/shorts/E1KPr8rSBzE), [267](https://www.youtube.com/shorts/V5HYXK6H7Gw)

Do topology cleanup as an explicit stage with acceptance criteria. Do not mix cleanup with material/lookdev polish.

### BH-094: Line Art Is Inspection And Style

Source: [285](https://www.youtube.com/shorts/h8q6NrFZS_M)

Use line art/outlines both as a stylized NPR layer and as a quick silhouette/edge-flow inspection pass.

### BH-095: Texture Isolation Prevents Paint Bleed

Sources: [286](https://www.youtube.com/shorts/ujZyU07NAPw), [287](https://www.youtube.com/shorts/xp47c7EU_sg)

Use material IDs, masks, object separation or named slots to isolate texture painting areas. Wrong-part painting is usually an organization bug.

### BH-096: Asset Browser Is A Production Multiplier

Sources: [288](https://www.youtube.com/shorts/4pcZew1tTEI), [291](https://www.youtube.com/shorts/3TUNexcKbJM), [298](https://www.youtube.com/shorts/aXUjRAfX7lE), [299](https://www.youtube.com/shorts/gGhz8Qi-hrA)

Reusable assets and materials should be named, marked and stored intentionally. A small asset library beats remaking the same bevel box/material again.

### BH-097: Collection Instances Need Clean Origins

Sources: [289](https://www.youtube.com/shorts/Qj3YXm3_0Yc), [292](https://www.youtube.com/shorts/LjZ0whxQw5M), [297](https://www.youtube.com/shorts/c5hUXg-zw2g)

Collection instances are only painless when collection origins and local offsets are planned. Fix origin/center issues before animation.

### BH-098: Render Passes Are Planned Deliverables

Source: [290](https://www.youtube.com/shorts/wJISRlbZeME)

Enable needed passes like Z, lighting, masks or Cryptomatte before the render. Missing passes cannot always be reconstructed later.

### BH-099: Asset Browser Settings Are Part Of Workflow

Sources: [296](https://www.youtube.com/shorts/MiZ6Oo_QhWk), [300](https://www.youtube.com/shorts/DNxYggoCM2E)

For kitbash/modular work, make browser defaults and filters repeatable. A good workspace removes setup friction.

### BH-100: Automation Still Needs QA

Sources: [279](https://www.youtube.com/shorts/g4W2c5qSYGk), this log's Blender lab workflow.

MCP/AI/addons can generate Blender scenes faster, but PNG review, validation, GLB inspection and state logging still decide quality.

## Session 006 Additions

### BH-101: Physics Needs Roles

Sources: [301](https://www.youtube.com/shorts/W4L2cRLB8gk), [317](https://www.youtube.com/shorts/0ydDt6hTK3E), [329](https://www.youtube.com/shorts/IUpNbDp75xI)

Rigid-body work starts with active bodies, passive bodies, collision shape, origin, scale, mass, friction and bounce. Without roles, the simulation is guesswork.

### BH-102: Bake Simulations For Delivery

Sources: [313](https://www.youtube.com/shorts/5ePWMapEbsQ), [321](https://www.youtube.com/shorts/7xjkqdj_xpM), [324](https://www.youtube.com/shorts/-xfUAIaaNos)

Physics, particles and force-field shots should be cached or baked before final review/export. A viewport playback is not delivery proof.

### BH-103: Copy Settings, Then Verify Exceptions

Sources: [305](https://www.youtube.com/shorts/KRdIwLkfs18), [333](https://www.youtube.com/shorts/1Ab4pBpby9k)

Copying rigid-body or simulation settings is a speed tool. After copying, inspect object-specific mass, collision thickness, material and role exceptions.

### BH-104: Force Fields Are Art Direction

Sources: [304](https://www.youtube.com/shorts/ne80HLjYulU), [308](https://www.youtube.com/shorts/0k6G6KZHp9Y), [316](https://www.youtube.com/shorts/3ggFqqj0BtI), [320](https://www.youtube.com/shorts/hRlgu62hNTc)

Wind, attraction, turbulence and vortex fields are motion controls. Show their influence zones and keep strength/radius/timing adjustable.

### BH-105: Particle Density Needs A Mask

Sources: [306](https://www.youtube.com/shorts/M2ieJJolRuk), [310](https://www.youtube.com/shorts/sFKXRpnn-EE), [330](https://www.youtube.com/shorts/eL5pmfXWlUc)

Use vertex groups, weight paint or named masks to control particle density. Random uniform emission rarely looks designed.

### BH-106: Particle Render Visibility Is A Gate

Sources: [337](https://www.youtube.com/shorts/4zvLfi-5cG4), [310](https://www.youtube.com/shorts/sFKXRpnn-EE)

Particles must be checked in viewport, render and export context. Many particle systems fail because the render object, collection, visibility or frame range is wrong.

### BH-107: Particle Paths Need Direction

Sources: [314](https://www.youtube.com/shorts/xc9udpazX6Q), [318](https://www.youtube.com/shorts/hyJgr2wWgAA), [339](https://www.youtube.com/shorts/nTyYIkc50as)

For particle trails, reveals or dispersal, path direction, wind direction and timing should be visible and testable.

### BH-108: Smoke Starts With Domain Bounds

Sources: [307](https://www.youtube.com/shorts/HG45umDLFOA), [311](https://www.youtube.com/shorts/wGKCxKt2sgg), [327](https://www.youtube.com/shorts/w4s3VJzYGxY), [334](https://www.youtube.com/shorts/gJ-BuL40Dm0)

Quick Smoke is only a shortcut to setup. The domain size, flow source, cache, material and frame-strip review still decide whether the shot works.

### BH-109: Simulation Resolution Is A Lookdev Control

Sources: [331](https://www.youtube.com/shorts/kTKfaDpMJEE), [343](https://www.youtube.com/shorts/t4A-Ramb8qU), [350](https://www.youtube.com/shorts/sFAcvS89eRE)

Smoke/fire/explosion resolution controls blockiness, cost and detail. Compare low/medium/high previews before committing a final cache.

### BH-110: Fluid Needs Boundaries

Sources: [340](https://www.youtube.com/shorts/eITixmIIvIw), [341](https://www.youtube.com/shorts/XAMHVC0k_BU), [344](https://www.youtube.com/shorts/gAV3EUNTbik), [345](https://www.youtube.com/shorts/bPrS6HiB4QA)

Fluid shots need clear domain, inflow/outflow, collision thickness, smoothing/material and frame-strip review. The liquid is only believable when its container is believable.

### BH-111: Fire Is Three Layers

Sources: [342](https://www.youtube.com/shorts/Gz7PNztcUV8), [346](https://www.youtube.com/shorts/uBn3LncKvbs), [350](https://www.youtube.com/shorts/sFAcvS89eRE)

Fire is fuel/flame, smoke density and lighting/exposure. Tuning one without the others produces noisy or flat results.

### BH-112: Explosion Layers Stay Separate

Sources: [347](https://m.youtube.com/shorts/z4E8mL3pbTs), [343](https://www.youtube.com/shorts/t4A-Ramb8qU)

Explosions should separate fracture/debris, force direction, smoke/fire, glow and camera shake. This keeps the effect editable and reviewable.

### BH-113: Shield FX Are Surface Plus Trigger

Sources: [312](https://www.youtube.com/shorts/WFDssJq6L3w), [335](https://www.youtube.com/shorts/uut2aDvT7IE)

Reactive shield or force-field effects need a surface, a trigger/impact zone, and a falloff. Do not let glow carry the whole effect.

### BH-114: Dust Is Subtle Motion

Sources: [306](https://www.youtube.com/shorts/M2ieJJolRuk), [326](https://www.youtube.com/shorts/tnp73qhvP94)

Dust usually reads through slow drift, uneven size, subtle lighting and limited density. Too much dust becomes visual noise.

### BH-115: Simulation Helpers Are Not Export Geometry

Sources: [319](https://www.youtube.com/shorts/lm248lMwpbk), [337](https://www.youtube.com/shorts/4zvLfi-5cG4), this log's validation workflow.

Domains, emitters, field visualizers, collision helpers and preview floors should be clearly named and excluded from GLB unless runtime simulation is intentionally delivered.

## Session 007 Additions

### BH-116: Procedural Systems Need Exposed Controls

Sources: [353](https://m.youtube.com/shorts/-Zx7CTH5E2g), [357](https://www.youtube.com/shorts/tqqsZLL_soM), [359](https://www.youtube.com/shorts/yXAyqJwFkOk)

Geometry-node and generator assets should expose density, spacing, profile, seed and scale controls. A hidden node tree is not a production control system.

### BH-117: Realize Procedural Geometry Before Fragile Delivery

Sources: [354](https://www.youtube.com/shorts/CKa9uLyLQCE), [360](https://www.youtube.com/shorts/mW04KpCSiQw)

When export, editing, collision or web playback depends on concrete geometry, convert/realize procedural results and validate the mesh count/materials.

### BH-118: Instance Distribution Needs Masks And Orientation

Sources: [355](https://www.youtube.com/shorts/JhGVktxT2ZQ), [356](https://www.youtube.com/shorts/Y_5hs4SVI0g), [358](https://www.youtube.com/shorts/oUr4gEa4gr4), [365](https://www.youtube.com/shorts/cv63w3seiro)

Scattering is not just "many copies." Use density masks, chosen instance collections, randomization limits, orientation rules and camera-distance checks.

### BH-119: Proximity Effects Need A Debug Layer

Sources: [352](https://www.youtube.com/shorts/pkgqRyXvQvU), [361](https://www.youtube.com/shorts/rY0uMPyaFA4)

Attract/avoid/growth effects should show their attractor, repulsor, radius and falloff in an inspectable layer before beauty material polish.

### BH-120: Procedural Materials Need Coordinates

Sources: [363](https://www.youtube.com/shorts/ZGuo82b4aYo), [362](https://www.youtube.com/shorts/r95bSiFV8YI), [364](https://www.youtube.com/shorts/wGHg-2nA4RY)

Procedural material and displacement setups need named coordinate strategy, bounded strength and material slots/attributes that survive export checks.

### BH-121: Cloth Starts With Pins

Sources: [366](https://www.youtube.com/shorts/EsIdAdj-sXw), [368](https://m.youtube.com/shorts/TaJrYftKhCc), [370](https://www.youtube.com/shorts/PWdLlf6Sy34)

Before wind, collisions or high-quality settings, cloth needs pinned vertex groups, anchors, collision clearance and a known frame range.

### BH-122: Cloth Motion Needs Frame Strips

Sources: [367](https://m.youtube.com/shorts/4G5Dr04OD6s), [371](https://www.youtube.com/shorts/hODiyaFuejk), [372](https://www.youtube.com/shorts/2_th4k6lKnE)

Cloth should be judged across a frame strip. One nice frame can hide popping, penetration, overstretched folds or unstable wind.

### BH-123: Thin Materials Need Physical Thickness Cues

Sources: [369](https://www.youtube.com/shorts/Euw8cLbYWOw), [373](https://www.youtube.com/shorts/r13_MdumvtE)

Garments, paper and curtains need thinness, fold direction, wrinkle scale, collision spacing and broken silhouettes. Flat sheets rarely read as fabric.

### BH-124: Drivers Need Visible Controls

Sources: [374](https://www.youtube.com/shorts/2jzbVueSwbA), [375](https://www.youtube.com/shorts/qABH04Yj7d0), [376](https://www.youtube.com/shorts/bMDj_GrX1qI), [379](https://m.youtube.com/shorts/emDXsK4y3C8)

Driver-heavy rigs should include visible control objects, limits, labels or reports for amplitude, damping, rotation ratio and loop timing.

### BH-125: Bake Constraints For Delivery

Sources: [377](https://www.youtube.com/shorts/AU1C-l8D8ow), [378](https://www.youtube.com/shorts/DFFmoJgXWFo), [380](https://www.youtube.com/shorts/bUC2Fn7hqmE)

Constraints are excellent for authoring but risky as an interchange assumption. Bake final motion to keyframes when export/runtime support is uncertain.

### BH-126: IK Needs Pole And Twist Planning

Sources: [381](https://www.youtube.com/shorts/M9ktE_VBjAg), [382](https://m.youtube.com/shorts/mHqHI0mZZ8M), [383](https://www.youtube.com/shorts/VxkWd2qEPi8)

IK rigs need pole targets, twist axes and helper bones/objects planned up front. Otherwise limbs flip when camera or pose changes.

### BH-127: Shape Keys Need Named Targets

Sources: [384](https://www.youtube.com/shorts/jIUgfd0kM8U), [386](https://www.youtube.com/shorts/R4PfeQLNhzc), [389](https://www.youtube.com/shorts/Zl5TtE6b_28)

Shape-key rigs need a clean Basis, named target keys and matching topology. Treat morphs as part of the rig, not hidden mesh trivia.

### BH-128: Expressions Need Multiple Small Keys

Sources: [387](https://www.youtube.com/shorts/vuq0jl-eNX0), [388](https://www.youtube.com/shorts/nU_pzKbCSjQ), [390](https://www.youtube.com/shorts/pUbxiZ6tLTE), [391](https://www.youtube.com/shorts/XkPD4o1lCNs)

Good expressions and blinks are built from several small timed keys. One large deformation often looks broken from the render camera.

### BH-129: Shape Keys Can Be Rig Controls

Sources: [385](https://www.youtube.com/shorts/OTQblTwTu3s), [392](https://www.youtube.com/shorts/y8Shm8vMNlg)

Shape keys become more production-friendly when connected to bones or selection-driven controls, so animators can blend them intentionally.

### BH-130: Line Art Must Be Scoped

Sources: [393](https://www.youtube.com/shorts/ZypT4iqD_Q0), [394](https://www.youtube.com/shorts/VYOUzhI6xPw), [396](https://www.youtube.com/shorts/a9Ne3OItW3Y)

Line Art and Grease Pencil outlines need object/collection scope, layer separation and foreground/background line weights. Global outlines get messy fast.

### BH-131: Line Boil Needs Controlled Noise

Sources: [395](https://www.youtube.com/shorts/K_epbDC_qOg), [399](https://www.youtube.com/shorts/NMhwJaORKCk)

Animated line noise should have amplitude, frequency and timing limits. The stroke should feel alive without destroying silhouette readability.

### BH-132: Imported 2D Strokes Need Cleanup

Sources: [397](https://www.youtube.com/shorts/cyUKq1xSRYs), [398](https://www.youtube.com/shorts/tq2KuI12-jI), [400](https://www.youtube.com/shorts/jluGZwLynmc)

Imported sketches or rigged Grease Pencil strokes need scale, depth, layer names, material names and pose checks before being treated as production art.

## Session 008 Additions

### BH-133: Render Passes Are Contracts

Sources: [401](https://www.youtube.com/shorts/y-2yERk2HGQ), [405](https://www.youtube.com/shorts/6WT_68xxKmw), [413](https://www.youtube.com/shorts/kSDQkEuKWMo), [414](https://www.youtube.com/shorts/kv8PAy0DbPg)

Mist, depth and mask passes must be planned before rendering, named in reports and checked for range/banding/edge artifacts. Missing passes are a broken deliverable, not a minor inconvenience.

### BH-134: Cryptomatte Needs Clean IDs

Sources: [402](https://www.youtube.com/shorts/81-0vHTH2gc), [406](https://www.youtube.com/shorts/8kV9Q_cWZZo), [410](https://www.youtube.com/shorts/c8yJ9PCHYqA), [416](https://www.youtube.com/shorts/fXFNEmjGEUA), [420](https://www.youtube.com/shorts/l6GhGrUrwqo)

Cryptomatte only helps when objects/materials are named and grouped deliberately. Random names produce random post-production friction.

### BH-135: Glow Is A Two-Stage Effect

Sources: [403](https://www.youtube.com/shorts/WgoeTlTn3EQ), [407](https://www.youtube.com/shorts/902DtSJeJTs), [411](https://www.youtube.com/shorts/B4FtGpw7KEo), [417](https://www.youtube.com/shorts/RyyH3-fFAUw), [421](https://www.youtube.com/shorts/ZTXiMZC4sls)

Glow needs both an emissive source and compositor glare/bloom. Tune each separately so the glow supports shape readability instead of hiding it.

### BH-136: Denoise Must Preserve Detail

Sources: [404](https://www.youtube.com/shorts/6kmc2ViN1Ak), [408](https://www.youtube.com/shorts/oHXyzTJH7X8), [412](https://www.youtube.com/shorts/OiBr5V-Lsdo)

Denoising and low sample counts are production tools only after comparing detail, texture edges, small highlights and animation flicker.

### BH-137: Color Management Needs Clipping Checks

Sources: [426](https://www.youtube.com/shorts/ud2jbjbfk4g), [427](https://www.youtube.com/shorts/IB3xOmaGJ2w), [419](https://www.youtube.com/shorts/FlU8fvg-mR0)

View transform, look, exposure and highlight limiting are lookdev controls. Always pair them with clipping and flat-color readability checks.

### BH-138: Light Groups And Links Need Intent

Sources: [423](https://www.youtube.com/shorts/2RUuPGWRacI), [424](https://www.youtube.com/shorts/j1muitoyTfY), [425](https://www.youtube.com/shorts/NC9rEDZ6tOw)

Light groups/linking are powerful only when each light has a job and a target. Record why a light affects only selected objects.

### BH-139: Comp Stacks Need Source Layers

Sources: [428](https://www.youtube.com/shorts/ENmAhqRXu3U), [422](https://www.youtube.com/shorts/af8diQSssUg)

Compositor tricks need source layers, masks and geometry QA. A comp that hides seams should still keep the underlying objects understandable.

### BH-140: Camera Focus Needs A Named Target

Sources: [429](https://www.youtube.com/shorts/YoOz42w37V8), [430](https://www.youtube.com/shorts/EFrt_pq9BF0), [409](https://www.youtube.com/shorts/zHsCOA-bUFE)

Depth of field should be driven by a named focus target or measured distance, then reviewed in preview before final render.

### BH-141: Camera Paths Need Bakeable Controls

Sources: [431](https://www.youtube.com/shorts/1JzezgekBwc), [432](https://www.youtube.com/shorts/u1jAqZyxsNA), [433](https://www.youtube.com/shorts/eEiqegVMQsw), [436](https://www.youtube.com/shorts/cc7J5LM1hTY)

Path-follow cameras and objects need visible path, speed ticks, target lock and a way to preserve visual transform before hand-keyed polish.

### BH-142: Orbit Cameras Need Loop Checks

Sources: [434](https://www.youtube.com/shorts/-916JkSrOkk), [438](https://www.youtube.com/shorts/Bsg6CyxtEiM)

Circular camera rigs need a center target, first/last-frame comparison and path smoothness review so loops do not jump.

### BH-143: Path Motion Needs Orientation Review

Sources: [435](https://www.youtube.com/shorts/UWScbEgPnBY), [437](https://www.youtube.com/shorts/jhWAfnq1gvM), [439](https://www.youtube.com/shorts/p0zvPo2dWaw)

Objects on paths need banking, up-axis and target tracking checks. Translation alone is not believable path animation.

### BH-144: Texture Transitions Need Masks

Sources: [440](https://www.youtube.com/shorts/NcTGqrZBl5M), [444](https://www.youtube.com/shorts/To4qMK1kZX8)

Material transitions should be controlled by named masks or drivers with readable start/end states. Mixed shaders without a mask become guesswork.

### BH-145: Procedural Surface Detail Needs Scale QA

Sources: [441](https://www.youtube.com/shorts/sA44IHHIGJQ), [442](https://www.youtube.com/shorts/1wVbP_3FKnE), [443](https://www.youtube.com/shorts/Ze90cyKHuRA), [447](https://www.youtube.com/shorts/ZvIujVJlvNE)

Procedural grid, rust, dust and texture detail should be checked close-up and at final camera distance for scale, aliasing and readability.

### BH-146: Edge Wear Is A Mask Pass

Sources: [445](https://www.youtube.com/shorts/sSDEjEjnxOE)

Edge wear should be driven by curvature, position, hand masks or material IDs. Universal noise dirt makes assets look accidental.

### BH-147: Bake What The Viewer Cannot Rebuild

Sources: [446](https://www.youtube.com/shorts/6QlQgqGZSzw), [448](https://www.youtube.com/shorts/Qh5iJjSHR0Q), [449](https://www.youtube.com/shorts/jmrkVa5arrQ), [450](https://www.youtube.com/shorts/dvafNzR259I)

Bake procedural materials, normals, roughness, opacity or color maps when the target viewer cannot reproduce the Blender node tree. Then verify GLB/material output.

### BH-148: Version-Specific Render Tricks Need Notes

Sources: [411](https://www.youtube.com/shorts/B4FtGpw7KEo), [415](https://www.youtube.com/shorts/rKknm9PSmFg)

Bloom, Eevee/Cycles and compositor workflows change across Blender versions. Record the version assumption in the scene report.

### BH-149: Highlight Control Beats Exposure Guessing

Sources: [417](https://www.youtube.com/shorts/RyyH3-fFAUw), [427](https://www.youtube.com/shorts/IB3xOmaGJ2w)

If highlights clip, do not only lower all exposure. Balance emitter strength, glare threshold, view transform and highlight compression.

### BH-150: Post Flexibility Starts In The Scene

Sources: [402](https://www.youtube.com/shorts/81-0vHTH2gc), [423](https://www.youtube.com/shorts/2RUuPGWRacI), [428](https://www.youtube.com/shorts/ENmAhqRXu3U)

Good compositing is prepared in modeling/lookdev: named objects, material IDs, light groups, masks and render passes make post flexible.

## Session 009 Additions

### BH-151: Live Unwrap Is A Diagnostic Loop

Sources: [451](https://www.youtube.com/shorts/tS63p4eOWV8), [458](https://www.youtube.com/shorts/1xS2IKbIUG0), [469](https://www.youtube.com/shorts/JkjdE5-QsHk)

Use live unwrap while placing seams, but judge by distortion, island readability and hidden seam placement. Fast unwrap is not automatically good unwrap.

### BH-152: Texel Density Is A Visual Consistency Gate

Sources: [452](https://www.youtube.com/shorts/1DzxGGClRmk), [455](https://www.youtube.com/shorts/cX8dCeXcgmM), [459](https://www.youtube.com/shorts/wtyhjRET0u4), [470](https://www.youtube.com/shorts/sB2ahYMvVZ4)

Texel density needs consistent scale across assets, exceptions for hero detail and documentation when UDIMs or separate texture sets are used.

### BH-153: UV Packing Needs Margin

Sources: [457](https://www.youtube.com/shorts/HREG5VWajVY), [466](https://www.youtube.com/shorts/YTu43DcYJ3o), [473](https://www.youtube.com/shorts/EUvuEQULUWc), [476](https://www.youtube.com/shorts/-kUogQPrcYo)

UV packers are not enough: padding, bake margin, island priority and overlap detection are required before baking.

### BH-154: UV Overlap Must Be Intentional

Sources: [462](https://www.youtube.com/shorts/2OHnu-Ieh9g), [472](https://www.youtube.com/shorts/q6i7jsB-pkE)

Mirrored or overlapped UVs can save space, but accidental overlap breaks baking and painting. Mark intended overlaps and inspect the rest.

### BH-155: Texture Export Needs Image Accountability

Sources: [453](https://www.youtube.com/shorts/YYUt7BRooL4), [491](https://www.youtube.com/shorts/m8ryP_Fr2Ps)

Texture export should verify packed/external image paths, target format and GLB/material behavior. Do not assume materials carry images automatically.

### BH-156: Bake Setup Needs Source And Target Names

Sources: [454](https://www.youtube.com/shorts/VRukg8phW68), [456](https://www.youtube.com/shorts/DszGv5_8iS0), [478](https://www.youtube.com/shorts/uQUXqD0oBa0)

Every bake needs source object, target object, source UV, target UV, image size, map type and cage/ray assumptions named somewhere.

### BH-157: Material Atlases Need Remap QA

Sources: [460](https://www.youtube.com/shorts/-179pa-f5rQ), [468](https://www.youtube.com/shorts/7ReXtNUrL8E), [494](https://www.youtube.com/shorts/Dq_y02NOsY8)

Combining materials or joining meshes requires preserving UV maps, material slots and atlas remapping. Check after join, not after export failure.

### BH-158: Paint Isolation Starts In Mesh Organization

Sources: [463](https://www.youtube.com/shorts/H8eSd0Ghi8o), [467](https://www.youtube.com/shorts/eZKTnLnz1j4)

External texture-paint tools depend on clean mesh splits, material IDs and geometry masks. Organization mistakes become wrong-part painting.

### BH-159: Spherical Seams Need View-Aware Placement

Sources: [461](https://www.youtube.com/shorts/akUxL62g5xY), [475](https://www.youtube.com/shorts/RrHbRmb-Y9Y)

Eyes, heads and character forms need seams hidden from the hero camera and animation-facing side, not simply shortest seam placement.

### BH-160: Position Passes Need Stable Coordinates

Sources: [471](https://www.youtube.com/shorts/0cT80_LpVEw)

Position-pass or coordinate-driven texturing depends on stable world/object coordinates. Moving origins or scale after setup can invalidate the look.

### BH-161: Normal Bakes Need Moving-Light Review

Sources: [474](https://www.youtube.com/shorts/cissl9LKiUY), [450](https://www.youtube.com/shorts/dvafNzR259I)

High-to-low normal bakes need cage/ray checks and moving-light review. A normal map can pass one still frame and fail in motion.

### BH-162: Sculpt Detail Needs An Export Cage

Sources: [479](https://www.youtube.com/shorts/RcBzW-0XlBI), [482](https://www.youtube.com/shorts/1xLY_tbg-cA)

Sculpt/remesh detail should be paired with a lower-poly export cage or retopo plan. Sculpt density alone is not web delivery.

### BH-163: Weighted Normals Are Shading QA

Sources: [480](https://www.youtube.com/shorts/v_2ecoqHLe0), [483](https://www.youtube.com/shorts/ijfBtBDKG_c), [486](https://www.youtube.com/shorts/X3xj7BRJleY)

For hard-surface assets, bevels and weighted normals should be checked together under grazing light. Bad normals masquerade as bad materials.

### BH-164: Fix Normals Before Materials

Sources: [481](https://www.youtube.com/shorts/BGw482qVWew), [484](https://www.youtube.com/shorts/-uZPU2ARjfw), [487](https://www.youtube.com/shorts/2IyaBQTMFQ0)

When shading looks wrong, inspect normals, sharp edges, smoothing and geometry before changing shaders.

### BH-165: Straight Edges Support Everything Downstream

Sources: [485](https://www.youtube.com/shorts/wedGVKPYcEM), [488](https://www.youtube.com/shorts/D-h97B9-4ic), [489](https://www.youtube.com/shorts/z7hviMWG0lE)

Straightened edges, controlled bevels and clean blockout make UVs, normals, baking and material readability easier.

### BH-166: Origins Are Export And Animation Controls

Sources: [490](https://www.youtube.com/shorts/xfWjV8z5Enk), [492](https://www.youtube.com/shorts/-Q-Gyha4oJ0), [493](https://www.youtube.com/shorts/Lr2nXasDwK4), [495](https://www.youtube.com/shorts/F3XHMQKTBzQ)

Origins decide pivots, instancing, constraints and export hierarchy. Set them deliberately and record exceptions.

### BH-167: Pivots Need Transform QA

Sources: [497](https://www.youtube.com/shorts/Lg7AbSKbn38), [498](https://www.youtube.com/shorts/aTQZVDQUUt0), [499](https://www.youtube.com/shorts/xtCuZUWefSg)

Pivot modes and individual origins speed up modeling, but each animated/exported part still needs final transform and pivot verification.

### BH-168: Face-Aligned Placement Needs Normal Checks

Sources: [500](https://www.youtube.com/shorts/gRH3bjsFl1A), [496](https://www.youtube.com/shorts/2VJJANVIY5Y)

Snapping or aligning objects to faces should check surface normal direction, scale, origin and collection organization before export.

## Session 010 Additions

### BH-169: Geometry Nodes Need An Apply Boundary

Sources: [501](https://www.youtube.com/shorts/CKa9uLyLQCE), [516](https://www.youtube.com/shorts/UIRQCz0KNLk), [549](https://www.youtube.com/shorts/nuf2AxJTqFo)

Procedural outputs need a clear point where they stay live, realize instances, or convert to mesh. Manual edits and exports should not depend on an ambiguous node state.

### BH-170: Scatter Systems Need Exposed Density And Seed

Sources: [502](https://www.youtube.com/shorts/PO277gErhWs), [509](https://www.youtube.com/shorts/mW04KpCSiQw), [517](https://www.youtube.com/shorts/JYjrN5gU2ZI), [519](https://www.youtube.com/shorts/VyjwI0HAQUU)

Every scatter rig should expose density, seed, scale and mask controls. Review it at hero, mid and far camera distances before delivery.

### BH-171: Curve Procedurals Need Orientation QA

Sources: [510](https://www.youtube.com/shorts/l-EmVzP9dGU), [511](https://www.youtube.com/shorts/ixg7Zvex9HA), [513](https://www.youtube.com/shorts/SGSNQbvNAI0), [518](https://www.youtube.com/shorts/nbliYgHiJmI), [550](https://www.youtube.com/shorts/iGCARTF_GB4)

Curve arrays, springs and curve-to-mesh assets need tangent orientation, spacing, radius and end-cap checks.

### BH-172: Set Position Needs Bounds

Sources: [504](https://www.youtube.com/shorts/r95bSiFV8YI), [532](https://m.youtube.com/shorts/eFQga281u9A)

Displacement through Set Position needs amplitude limits, falloff controls and silhouette review. Procedural motion without bounds can wreck scale and export budgets.

### BH-173: Procedural Foliage Needs LOD Gates

Sources: [505](https://www.youtube.com/shorts/WJG3gmkQAHY), [508](https://www.youtube.com/shorts/ZxlkZCwFfKk), [512](https://www.youtube.com/shorts/9-VwXd8JicY), [521](https://www.youtube.com/shorts/y2sXvim3huI)

Grass, plants, hair and fur need separate viewport/render density, random seed control, silhouette review and LOD or culling rules.

### BH-174: Instance Variation Needs Index Logic

Sources: [515](https://www.youtube.com/shorts/OBuXK-LkTdI), [516](https://www.youtube.com/shorts/UIRQCz0KNLk), [549](https://www.youtube.com/shorts/nuf2AxJTqFo)

Instance variation should be driven by explicit index/switch logic, not accidental collection order. Realize only when downstream tools require real geometry.

### BH-175: Surface Effects Need Contact Rules

Sources: [520](https://www.youtube.com/shorts/wWHmzq-Y6Xo), [524](https://www.youtube.com/shorts/A4UFCoN4I3I), [542](https://www.youtube.com/shorts/PvfMzEq3lrg), [545](https://www.youtube.com/shorts/ijJ6ZoOQ21k), [546](https://www.youtube.com/shorts/rY0uMPyaFA4)

Droplets, proximity growth and raycast-driven effects need surface normals, hit distance, miss state, falloff and overlap checks.

### BH-176: Node Materials Need Attribute Contracts

Sources: [543](https://www.youtube.com/shorts/YH9TlU7szHE), [547](https://www.youtube.com/shorts/gxUKivylRSI)

When Geometry Nodes drives materials, write down attribute names, ranges and expected shader behavior. Store Named Attribute is a material interface, not a casual side effect.

### BH-177: Simulation Zones Need Reset And Loop QA

Sources: [529](https://www.youtube.com/shorts/0EmKFMk27H8), [531](https://www.youtube.com/shorts/8KJWwL2VXAo), [535](https://www.youtube.com/shorts/QEEk-BGi99A), [536](https://www.youtube.com/shorts/gyi2s1g9keI), [537](https://www.youtube.com/shorts/yuquzjq_YPg), [538](https://www.youtube.com/shorts/OTtY6nQPqMI)

Simulation-zone setups need deterministic reset state, cache strategy, lifetime/decay controls and first/last-frame continuity checks.

### BH-178: Repeat Networks Need Stop Conditions

Sources: [528](https://www.youtube.com/shorts/GF3R_tM6K90), [534](https://www.youtube.com/shorts/HFeobQW8JgM)

Repeat and For Each procedural networks need iteration bounds, depth limits and performance gates so the result remains editable and exportable.

### BH-179: Procedural Grids Need Bounds

Sources: [527](https://www.youtube.com/shorts/QeGKP5ML8PY), [530](https://www.youtube.com/shorts/M025a-YCoTs)

Grids, countdowns and frame-indexed procedural layouts need clear bounds, scale references and legibility checks at the final camera.

### BH-180: Procedural Damage Needs A Clean Exit

Sources: [539](https://www.youtube.com/shorts/Y2DfE5ghbcM), [540](https://www.youtube.com/shorts/OH7TU-twwJU), [541](https://www.youtube.com/shorts/Ds3nyJ7DPMs)

Cracks and fractures need source curves or chunks preserved, mask widths documented, UV continuity checked and cleanup after physics or generation.

### BH-181: Intersections Can Become Guide Geometry

Sources: [525](https://www.youtube.com/shorts/8nZQvjq7hTk)

Generated intersection curves are useful as trim, guides or design lines only if the source objects and resulting curves are named and reviewed.

### BH-182: Procedural Stroke Animation Needs Timing QA

Sources: [526](https://m.youtube.com/shorts/liW3qWAm55w), [522](https://www.youtube.com/shorts/omRcs63g0rs)

Animated strokes and points-on-surface effects need seed, noise speed, deformation-follow and start/end shape checks.

### BH-183: Geometry Nodes Need Frame Hygiene

Sources: [548](https://www.youtube.com/shorts/0iztwYK70-8)

Frame and label node groups around inputs, masks, scatter, realization, material attributes and export handoff. A procedural rig must be readable after the first build.

### BH-184: Procedural Bevels Need Shading QA

Sources: [503](https://www.youtube.com/shorts/i1gOGlGfZEw), [523](https://www.youtube.com/shorts/NXGmKN4-jkg)

Wireframe and bevel procedurals need thickness, segment count, normals and grazing-light checks before materials are judged.

### BH-185: Procedural Shape Controls Beat Destructive Fixes

Sources: [506](https://www.youtube.com/shorts/O7-PpVDJKKA), [514](https://www.youtube.com/shorts/kVY6_DmtAUE), [507](https://www.youtube.com/shorts/m81mFjpbLa4)

Keep important shape decisions as exposed controls: transform alignment, corner radius, repeated detail spacing and surface-normal placement.

## Session 011 Additions

### BH-186: IK Needs Named Targets And Poles

Sources: [551](https://www.youtube.com/shorts/77RvfjaWvRQ), [555](https://www.youtube.com/shorts/gQAEV7vHViU), [559](https://www.youtube.com/shorts/oNsj2a_QCbs), [571](https://www.youtube.com/shorts/pgHLeSWGYAo), [572](https://www.youtube.com/shorts/XVygpM7l0pQ)

IK is not complete when the limb moves. Target, pole, chain length, pole angle and control naming must be visible and tested from rest pose to extreme pose.

### BH-187: Mechanical Rigs Need Locked Axes

Sources: [554](https://www.youtube.com/shorts/Rf57K1zWqFQ), [565](https://www.youtube.com/shorts/u74TJJS3gCw), [568](https://www.youtube.com/shorts/kIwCs2eJP4o), [570](https://www.youtube.com/shorts/Ux9jGvYTXVs), [577](https://www.youtube.com/shorts/2jzbVueSwbA)

Robotic arms, shock absorbers and mechanical systems need pivot hierarchy, hinge axes, rotation limits, segment-length preservation and collision clearance checks.

### BH-188: Constraint Motion Needs A Bake Gate

Sources: [552](https://www.youtube.com/shorts/AU1C-l8D8ow), [558](https://www.youtube.com/shorts/DFFmoJgXWFo)

Before exporting constraint-driven animation, review visual transform, frame range and target runtime. Bake to keyframes when the runtime will not evaluate Blender constraints.

### BH-189: Held Props Need Constraint Handoff QA

Sources: [557](https://www.youtube.com/shorts/8umN1Fs8COs)

Child Of or held-object workflows need influence handoff, inverse/visual transform checks and frame markers for grab, hold and release.

### BH-190: Weights Need Pose-Based Proof

Sources: [553](https://www.youtube.com/shorts/sYLo3TcoKLE), [556](https://www.youtube.com/shorts/dC-SJtXjIDs), [560](https://www.youtube.com/shorts/1axVvl-7NQ4), [563](https://www.youtube.com/shorts/C8SUpMcQfeU), [566](https://www.youtube.com/shorts/C0GM1-Qz5Tk), [569](https://www.youtube.com/shorts/-bIaedcU05k)

Transferred, mirrored or parented weights are not proven until deformation is checked in multiple poses, with left/right naming and clothing intersections reviewed.

### BH-191: Foot IK Needs Contact Semantics

Sources: [562](https://www.youtube.com/shorts/YwV7vjOhwsE)

Foot IK needs ground contact, heel/toe pivots, foot-roll limits and planted/sliding state checks.

### BH-192: Root Motion Needs Export Separation

Sources: [564](https://www.youtube.com/shorts/RgcR5W752kM)

Game-ready animation should separate root motion from in-place body motion, document the forward axis and verify the exported clip frame range.

### BH-193: Tail And Secondary Rigs Need Follow Order

Sources: [561](https://www.youtube.com/shorts/lUzXzMJ33Kg), [584](https://www.youtube.com/shorts/Aq0riPjmp7Y)

Tail rigs and attached secondary rigs need follow constraint order, parent space, namespace and controller conflict checks.

### BH-194: Drivers Need Named Variables And Ranges

Sources: [579](https://www.youtube.com/shorts/6v2Ut6PPx1E), [583](https://www.youtube.com/shorts/sr_bEstjpkU), [587](https://www.youtube.com/shorts/O6i1HnQ2AVQ), [588](https://www.youtube.com/shorts/606bv0QyMWY)

Drivers should expose named variables, expected value ranges, target paths and stale-driver cleanup. Gear ratios and visibility drivers need explicit verification.

### BH-195: Loop Helpers Need First Last Match

Sources: [578](https://www.youtube.com/shorts/SWJNp1ikqAs), [580](https://www.youtube.com/shorts/wa_Q5wH2d3w), [585](https://www.youtube.com/shorts/bMDj_GrX1qI), [586](https://www.youtube.com/shorts/8GefjzIceek)

Cyclic f-modifiers, extrapolation, springs and walk cycles need first/last-frame visual match, contact pose checks and range guards.

### BH-196: Curve Cables Need Anchors

Sources: [576](https://www.youtube.com/shorts/MoFCk3_uK24), [581](https://www.youtube.com/shorts/_7QHjrxio4c), [595](https://www.youtube.com/shorts/xI3DLkOBwws)

Curve cables and hooks need named controllers, endpoint anchors, curve direction checks and deformation scope limits.

### BH-197: Linked Rigs Need Edit Policy

Sources: [582](https://www.youtube.com/shorts/yjmbWFnmyaw)

Linked characters and rigs need a library override or source-link policy before editing, so animation fixes do not fork hidden asset state.

### BH-198: Controller Rigs Need Reset Pose

Sources: [567](https://www.youtube.com/shorts/dHPmp8Hlaok), [573](https://www.youtube.com/shorts/F5wlEjgBqRw), [589](https://m.youtube.com/shorts/ETDIEJkiLhw)

Controller rigs for props, windows or one-bone controls need visible handles, constraint limits, influence limits and a reliable reset pose.

### BH-199: Animation Cleanup Is Export QA

Sources: [574](https://www.youtube.com/shorts/UoTWjbn13ms)

Before export, remove unused actions, stale animation data and old clips unless they are intentionally delivered.

### BH-200: Deformation Modifiers Need Silhouette QA

Sources: [575](https://www.youtube.com/shorts/Hq3s-z6a5bI)

Any deformation modifier should be reviewed before/after for silhouette, topology stress and material stretching.

### BH-201: Cloth Pins Need Named Vertex Groups

Sources: [590](https://www.youtube.com/shorts/EsIdAdj-sXw), [591](https://www.youtube.com/shorts/J10PMrm1BS8), [593](https://www.youtube.com/shorts/iuvO5x4irPk), [598](https://www.youtube.com/shorts/nmt7ipHuW74), [600](https://www.youtube.com/shorts/gj_RbCuZmS4)

Cloth pins, hooks and root data need named vertex groups, animated anchors and motion tests. A cloth setup is fragile if the pin source is implicit.

### BH-202: Cloth Sims Need Cache And Scale Notes

Sources: [594](https://www.youtube.com/shorts/hODiyaFuejk), [597](https://www.youtube.com/shorts/th3W_cEPTZ0), [599](https://www.youtube.com/shorts/Hmfa2J0Y6Wg)

Cloth settings should record object scale, quality steps, collision margin, wind/force settings and cache state before final render or export.

### BH-203: Secondary Physics Need Amplitude Limits

Sources: [592](https://www.youtube.com/shorts/a4o9XPYA3h4), [596](https://www.youtube.com/shorts/FaNT1c_tEhk)

Jiggle, pressure and balloon effects need amplitude or pressure clamps, collision/self-collision checks and approval that secondary motion fits the asset.

## Session 012 Additions

### BH-204: Viewport Compositing Needs Final Parity

Sources: [601](https://www.youtube.com/shorts/ROzHhjXQtI4)

Live viewport compositor effects are useful only if the final render uses the same pass assumptions, camera display state and color-management checks.

### BH-205: Glow Needs Threshold Control

Sources: [602](https://www.youtube.com/shorts/902DtSJeJTs), [645](https://www.youtube.com/shorts/YaxMk6nGF7c), [649](https://www.youtube.com/shorts/jKybWGm-Mss)

Glow and bloom should be controlled with emission strength, glare threshold, pass isolation and clipping checks. A pretty viewport glow is not enough.

### BH-206: Camera Shake Needs Limits

Sources: [603](https://www.youtube.com/shorts/tKhzHSj2zUU)

Camera shake should expose amplitude, frequency and start/end damping, with a steady reference frame so motion does not hide composition problems.

### BH-207: Tracking Needs Solve QA

Sources: [604](https://www.youtube.com/shorts/GIC5L9f4v3A), [608](https://www.youtube.com/shorts/l8P6043cO4c), [615](https://www.youtube.com/shorts/SPW2Xjy2NiM), [617](https://www.youtube.com/shorts/KRxDXjTH6kY), [619](https://www.youtube.com/shorts/T6bY9eW_Dbc)

Tracking is not done when markers follow. Review solve error, outliers, frame drift, ground plane, update order and alignment with the CG object.

### BH-208: Tracking Shortcuts Need Assumptions

Sources: [605](https://www.youtube.com/shorts/F6LEHNbRTlk), [611](https://www.youtube.com/shorts/m-9BbVVP3Qk), [618](https://www.youtube.com/shorts/yBVniR3tE-I), [623](https://www.youtube.com/shorts/xEOQAtBOQ5Q)

One-marker, addon or external-tracker workflows need written assumptions: planar motion, scale, lens, coordinate system and object/proxy calibration.

### BH-209: Keying Needs Matte And Spill QA

Sources: [606](https://www.youtube.com/shorts/zMZM7FPH5io), [609](https://www.youtube.com/shorts/AEG4QsL1iFc), [612](https://www.youtube.com/shorts/iT957c86M3g)

Green screen and flash VFX comps need matte cleanup, spill suppression, edge review and background-specific color checks.

### BH-210: Shadow Catchers Need Contact Proof

Sources: [607](https://www.youtube.com/shorts/WBu02tkog0Q), [610](https://www.youtube.com/shorts/l1mL9OMRIDc), [613](https://www.youtube.com/shorts/1pUzvz3v6u0), [620](https://www.youtube.com/shorts/c4ey-uvgiYo), [621](https://www.youtube.com/shorts/G9yPhDLGBuQ), [622](https://www.youtube.com/shorts/SNYCRDMduNM)

Shadow catchers need matching light direction, contact softness, alpha behavior, per-object shadow notes and final-background verification.

### BH-211: Camera Tracking Rigs Need Framing QA

Sources: [614](https://www.youtube.com/shorts/t4I0AYRhKL4), [616](https://www.youtube.com/shorts/MWMJbBNDK-4)

Object-follow and camera-track rigs need target naming, distance, focal length, locked axes and frame-crop review through the shot.

### BH-212: Grease Pencil Needs Layer Discipline

Sources: [625](https://www.youtube.com/shorts/ukcgQTS3jCE), [629](https://www.youtube.com/shorts/WbwKXMwIKPM), [634](https://www.youtube.com/shorts/0haGlQ2F3-w), [637](https://www.youtube.com/shorts/-rzbKBypUz4), [644](https://www.youtube.com/shorts/_15_1-TTwVI), [647](https://www.youtube.com/shorts/jluGZwLynmc)

Grease Pencil work should name layers, stroke materials, imported sketches, timing holds and camera/depth rules before animation becomes hard to debug.

### BH-213: Line Art Needs Scope And Thickness QA

Sources: [626](https://www.youtube.com/shorts/ZypT4iqD_Q0), [630](https://www.youtube.com/shorts/VYOUzhI6xPw), [635](https://www.youtube.com/shorts/a9Ne3OItW3Y), [638](https://www.youtube.com/shorts/cyUKq1xSRYs), [639](https://www.youtube.com/shorts/eqsk4Ss1WfA)

Line Art and outline modifiers need collection/object scope, depth ordering, camera crop and thickness checks at the delivery resolution.

### BH-214: Line Boil Needs Noise Limits

Sources: [628](https://www.youtube.com/shorts/K_epbDC_qOg), [641](https://www.youtube.com/shorts/NMhwJaORKCk)

Animated line boil needs noise amplitude, speed, hold-frame and readability limits so it feels intentional instead of jittery.

### BH-215: Mixed 2D And 3D Needs Shared Space

Sources: [631](https://www.youtube.com/shorts/aZ9PZppucQQ), [632](https://www.youtube.com/shorts/VHS3YrJ4uY0), [648](https://www.youtube.com/shorts/S0I5ku5L1a4)

2D/3D hybrid scenes need shared camera space, depth order, parallax rules, timing and controller ownership.

### BH-216: Grease Pencil Rigs Need Pose Tests

Sources: [627](https://www.youtube.com/shorts/tq2KuI12-jI), [633](https://www.youtube.com/shorts/XAxvsf0CCGM), [642](https://www.youtube.com/shorts/1IPR1Z_lEAQ)

Rigged Grease Pencil assets need stroke deformation tests, layer grouping, parent-space checks and visual-transform preservation.

### BH-217: Toon Style Needs A Pass Contract

Sources: [636](https://www.youtube.com/shorts/srMwm1Z1qIQ), [646](https://www.youtube.com/shorts/9EsqHjN_Gl0)

Toon, watercolor and hand-painted styles need material bands, texture, outlines and color grade described as separate passes so each can be adjusted.

### BH-218: Fake Reflections Need Link Logic

Sources: [640](https://www.youtube.com/shorts/4uWOK0fX88o)

Fake Grease Pencil reflections should record source linkage, offset, opacity and update behavior so they do not drift from the main drawing.

### BH-219: 2D To 3D Conversion Needs Cleanup

Sources: [643](https://www.youtube.com/shorts/5hXGcBmpLAc), [650](https://www.youtube.com/shorts/7XoI_q3YlKw)

Mesh-to-Grease-Pencil or 2D-to-3D conversion needs source cleanup, silhouette depth assumptions, stroke/mesh validation and noise limits.

### BH-220: VFX Shots Need Pass Accounting

Sources: [624](https://www.youtube.com/shorts/rf9e8bS4GfA)

Complex VFX shots need pass accounting: camera solve, AOVs, shadow catchers, keying, color grade, sound handoff and final background notes.

## Session 013 Additions

### BH-221: Blend Files Need Collection Contracts

Sources: [651](https://www.youtube.com/shorts/EZEk6hLPr20), [669](https://www.youtube.com/shorts/5qKEq6EE4vQ), [680](https://www.youtube.com/shorts/Rsg3JslU2O0)

Production `.blend` files need named collections, viewport/render/export visibility notes, source grouping and orphan cleanup before handoff.

### BH-222: UV Speed Needs Seam And Pin Audits

Sources: [652](https://www.youtube.com/shorts/9tp1qzFXU1M), [654](https://www.youtube.com/shorts/5Pki4ONc3tI), [655](https://www.youtube.com/shorts/Uz3zdVkTEvU)

Fast UV tools are safe only when seams, pinned islands, padding, stretch and texel density are visible in the review.

### BH-223: Smart UV Is A Draft Pass

Sources: [653](https://www.youtube.com/shorts/FY1M5GxSnDs)

Smart UV unwrap is useful for blocking or quick previews, but final assets still need intentional seams, island grouping and distortion checks.

### BH-224: Texture Painting Needs Channel Versioning

Sources: [656](https://www.youtube.com/shorts/MrocITmnGFA), [661](https://www.youtube.com/shorts/C3dR2gcMeMk), [663](https://www.youtube.com/shorts/Vh6IjY8Ma8k)

Texture painting should record channel ownership, brush settings, image versions, displacement amplitude and backup outputs.

### BH-225: Shader Speedups Need Node Hygiene

Sources: [657](https://www.youtube.com/shorts/MHZ10n6cGGw), [662](https://www.youtube.com/shorts/L3vj6DjZmhc), [698](https://www.youtube.com/shorts/RyYZea6qMOw)

Node Wrangler and shader shortcuts should leave behind framed nodes, labels, muted-preview cleanup and a final material audit.

### BH-226: Textures Need Scale And Resolution Rules

Sources: [658](https://www.youtube.com/shorts/DgMf8D6JiNk), [660](https://www.youtube.com/shorts/w9_q5ZhFE68), [664](https://www.youtube.com/shorts/52bZLRkc_EI)

Texture work needs texel density, real-world scale, source license, resolution and GLB compatibility notes.

### BH-227: Shading Modes Are QA Views

Sources: [659](https://www.youtube.com/shorts/7SAmXei2BlA), [676](https://www.youtube.com/shorts/Pbv1fEfpEv0), [680](https://www.youtube.com/shorts/Rsg3JslU2O0)

Solid, material, rendered and face-orientation views should be treated as QA passes for normals, material slots, clipping and collection visibility.

### BH-228: Procedural Materials Need Bake Decisions

Sources: [665](https://www.youtube.com/shorts/XFQQP2ELaWY), [700](https://www.youtube.com/shorts/LcJRxWXD55zs)

Procedural gradients and Principled BSDF tweaks need a clear decision: keep as runtime PBR parameters or bake to textures for web delivery.

### BH-229: Asset Libraries Need Provenance

Sources: [666](https://www.youtube.com/shorts/SfkC5dW6xmI), [667](https://www.youtube.com/shorts/vPnDLiS4CHM), [668](https://www.youtube.com/shorts/4mUTnM8vq_M), [671](https://www.youtube.com/shorts/Sq6J5ovR21o), [672](https://www.youtube.com/shorts/xT2IhOm1tbQ), [673](https://www.youtube.com/shorts/1QXOkJZbphs), [674](https://www.youtube.com/shorts/NHOV8yspJYM), [675](https://www.youtube.com/shorts/4Hjcp7v0BxU)

Asset libraries need root paths, catalog names, thumbnails, append/link policy, license provenance, cache paths and missing-file checks.

### BH-230: Reusable Assets Need Scale Proof

Sources: [670](https://www.youtube.com/shorts/fChKu3TBEGo), [671](https://www.youtube.com/shorts/Sq6J5ovR21o), [674](https://www.youtube.com/shorts/NHOV8yspJYM)

Reusable assets need thumbnail, origin, bounds, unit scale and a quick placement test before they enter a shared library.

### BH-231: Mesh Cleanup Needs Before/After Metrics

Sources: [677](https://www.youtube.com/shorts/28MZ5BHXysc), [681](https://www.youtube.com/shorts/XdSEcR6ASu0), [682](https://www.youtube.com/shorts/iEo9a3VPz4c), [683](https://www.youtube.com/shorts/4H4UHdqiL68)

Cleanup operations should report selected scope, merge threshold, removed edges, overlap/z-fight checks and shading impact.

### BH-232: Poly Reduction Needs Silhouette Budget

Sources: [678](https://www.youtube.com/shorts/Ds-lmIgBPZw)

Polygon reduction must be judged against silhouette, deformation needs, material boundaries and the target triangle budget.

### BH-233: GLB Export Needs Transform And Material Audit

Sources: [679](https://www.youtube.com/shorts/qhVKrU3cv4c)

GLB export needs applied transforms, helper exclusion, material compatibility, animation inclusion and file-size checks.

### BH-234: Normals Need Weighted And Autosmooth Discipline

Sources: [676](https://www.youtube.com/shorts/Pbv1fEfpEv0), [684](https://www.youtube.com/shorts/brG9FL09_wk), [685](https://www.youtube.com/shorts/DSOHxMY0zhA), [686](https://www.youtube.com/shorts/SOTHtfN6xT4)

Face orientation, shade smooth, autosmooth and weighted normals should be reviewed together so smoothing improves highlights without hiding bad topology.

### BH-235: Bevels Need Parameter Audits

Sources: [687](https://www.youtube.com/shorts/ayWDGsYvJk0), [688](https://www.youtube.com/shorts/Jqf1PzC22Ec), [689](https://www.youtube.com/shorts/UV9aeIKvH2Y)

Bevel work needs applied scale, clamp/support-loop review, width, segments, profile and highlight checks.

### BH-236: Solidify Needs Thickness And Normal QA

Sources: [690](https://www.youtube.com/shorts/82JAg32Z9sQ)

Solidify setups need thickness, offset, rim closing, normal direction and backface checks before export.

### BH-237: Modifier Stacks Need Order Contracts

Sources: [691](https://www.youtube.com/shorts/A34Sw4NKZXc), [692](https://www.youtube.com/shorts/EmUb5EvJ-u4), [693](https://www.youtube.com/shorts/oTy_b5B0-Z0), [694](https://www.youtube.com/shorts/HBTv3Zyv0X4), [695](https://www.youtube.com/shorts/raxdCQ3hyHw)

Modifier stacks need an explicit order, strength/count limits, apply-or-live decisions, curve caps and loop-timing validation.

### BH-238: Hard Surface References Need Blockout Tags

Sources: [696](https://www.youtube.com/shorts/4T3zDNMYyN4), [697](https://www.youtube.com/shorts/dGwq-Wa7Nqk)

Hard-surface inspiration should become blockout modules, layer tags, modular scale rules and bevel/normal consistency checks, not copied source art.

### BH-239: Fast Color Changes Need Palette Ownership

Sources: [699](https://www.youtube.com/shorts/xevm1TLZPmY)

Fast color edits should route through owned palette materials or linked instances so late changes stay consistent across the scene.

## Session 014 Additions

### BH-240: Scattering Needs Mask Seed Density Controls

Sources: [701](https://www.youtube.com/shorts/mW04KpCSiQw), [704](https://www.youtube.com/shorts/9ZIQ9M8HBtQ), [716](https://m.youtube.com/shorts/-Zx7CTH5E2g), [720](https://www.youtube.com/shorts/C6hH_vd-bdY), [739](https://www.youtube.com/shorts/x8vtKJ8NaaU)

Scatter systems need explicit surface masks, density, random seed, collision/overlap review and viewport/render instance budgets.

### BH-241: Randomization Needs Stable IDs

Sources: [702](https://www.youtube.com/shorts/mxlTHHrHmB4), [705](https://www.youtube.com/shorts/Fn6yL7CHXuo), [706](https://www.youtube.com/shorts/CUoumIAXZ8U), [709](https://www.youtube.com/shorts/ssfsFAFbmSk), [710](https://www.youtube.com/shorts/NcJwduEi_QM), [741](https://www.youtube.com/shorts/oUr4gEa4gr4)

Random colors, transforms, scales and curve instances need deterministic seeds, stable IDs, axis masks and reset/bounds checks.

### BH-242: Procedural Animation Needs Exposed Timing

Sources: [703](https://www.youtube.com/shorts/ghogqc4M6Vk), [711](https://www.youtube.com/shorts/ptoqO-jFrqs), [712](https://www.youtube.com/shorts/JP5RNlNhuTg), [717](https://www.youtube.com/shorts/AI-NdYTZL20), [718](https://www.youtube.com/shorts/UVdv_HwKfDM), [721](https://www.youtube.com/shorts/lw0zkWXFGJA)

Procedural animation needs visible speed, phase, offset, angular clamps and loop controls rather than hidden frame math.

### BH-243: Curve Distribution Needs Tangent QA

Sources: [708](https://www.youtube.com/shorts/SGSNQbvNAI0), [726](https://www.youtube.com/shorts/NStTBJrDu4A), [734](https://www.youtube.com/shorts/_3__wto3A0w)

Instances on curves need tangent orientation, spacing, end caps, origin discipline and instance-vs-realize decisions.

### BH-244: Simulation Nodes Need Cache Reset Notes

Sources: [714](https://m.youtube.com/shorts/5HDmUIcHDmQ), [727](https://www.youtube.com/shorts/GgQAIJsYQuo), [731](https://www.youtube.com/shorts/PeyfwkRRPX4), [743](https://www.youtube.com/shorts/8KJWwL2VXAo), [747](https://www.youtube.com/shorts/XDAkLoUwUUE)

Simulation-node setups need cache strategy, frame range, reset state, timestep stability and bounds cleanup before handoff.

### BH-245: Particle Trails Need Lifetime Cleanup

Sources: [719](https://www.youtube.com/shorts/4h42cJa7qaA), [728](https://www.youtube.com/shorts/0EmKFMk27H8), [747](https://www.youtube.com/shorts/XDAkLoUwUUE)

Dust, particle emitters and trails need lifetime, alpha/size clamps, ID stability, memory budget and final-frame cleanup.

### BH-246: Realize Instances Is An Export Gate

Sources: [723](https://www.youtube.com/shorts/Sw0T5963DYo), [748](https://www.youtube.com/shorts/nuf2AxJTqFo), [750](https://www.youtube.com/shorts/31Rxr26pHwo)

Keep geometry instanced during authoring; realize instances only for edit/export requirements and measure the triangle/file-size impact.

### BH-247: Procedural Environments Need LOD Contracts

Sources: [713](https://www.youtube.com/shorts/1BdVXaTGcB0), [716](https://m.youtube.com/shorts/-Zx7CTH5E2g), [723](https://www.youtube.com/shorts/Sw0T5963DYo)

Procedural cities, landscapes and walls need block scale, LOD, seed, hierarchy and collection naming before they become production scenes.

### BH-248: Grass And Hair Need Distribution Masks

Sources: [724](https://www.youtube.com/shorts/4mlBtcRPbfU), [732](https://www.youtube.com/shorts/gaYNEcnS_oc), [736](https://www.youtube.com/shorts/ybc0ZMDHnnQ), [739](https://www.youtube.com/shorts/x8vtKJ8NaaU)

Grass, hair and foliage systems need density/texture masks, viewport-render splits, collision and clipping checks under motion.

### BH-249: Dissolves Need Progress And Final Cleanup

Sources: [725](https://www.youtube.com/shorts/KOW3GV9i-EM), [745](https://www.youtube.com/shorts/hcV5fqSq3G8)

Dissolve and disintegration effects need progression masks, particle lifetime, source mesh cleanup and a clean final-state frame.

### BH-250: Data Transfer And Baking Need Projection QA

Sources: [729](https://www.youtube.com/shorts/8gcIyunv8Kc), [737](https://www.youtube.com/shorts/i4rcOL-E5VM)

UV transfer and high-to-low baking need shape similarity, projection distance, cage settings, tangent space, map strength and low-poly validation.

### BH-251: Noise Deformation Needs Strength Bounds

Sources: [733](https://www.youtube.com/shorts/pIYalZHxitY)

Noise deformation should expose strength, frequency, axis influence and silhouette limits so it stays art-directable.

### BH-252: Procedural Modules Need Measurement Rules

Sources: [730](https://www.youtube.com/shorts/X_8M5TZC9WY), [738](https://www.youtube.com/shorts/l-EmVzP9dGU), [744](https://www.youtube.com/shorts/O32C3TzFcZw)

Fences, rails, springs and modular procedural assets need length, spacing, corners, caps and deformation limits as named controls.

### BH-253: Heavy Effects Need File And Cache Warnings

Sources: [735](https://www.youtube.com/shorts/Q8O6zZQyKyY), [742](https://www.youtube.com/shorts/uU5C3btT9Js)

Heavy simulation or surface-path effects need checkpoint saves, file-size risk notes, cache cleanup and fallback renders.

### BH-254: Branching Systems Need Visual Pruning

Sources: [727](https://www.youtube.com/shorts/GgQAIJsYQuo), [743](https://www.youtube.com/shorts/8KJWwL2VXAo)

Point-link and branching systems need neighbor/branch limits, line-count budgets and visual pruning controls.

### BH-255: Procedural Text Needs Readability Gates

Sources: [715](https://www.youtube.com/shorts/hmbcAIF2j9Q), [746](https://www.youtube.com/shorts/QeGKP5ML8PY)

Text morphs and procedural counters need topology/conversion strategy, frame mapping and readability checks at delivery resolution.

### BH-256: Geometry Nodes Need Statistics Overlays

Sources: [740](https://www.youtube.com/shorts/xaMg4dYr1Ho)

Geometry-node reviews should record viewport statistics: object count, realized triangles, instance count proxy and before/after budgets.

### BH-257: Looping Simulations Need First Last Proof

Sources: [749](https://www.youtube.com/shorts/QEEk-BGi99A), [718](https://www.youtube.com/shorts/UVdv_HwKfDM)

Looping simulations and offset animations need first/last frame comparison, seed stability and no visible pop at the seam.

### BH-258: Version Specific Nodes Need Compatibility Notes

Sources: [711](https://www.youtube.com/shorts/ptoqO-jFrqs), [731](https://www.youtube.com/shorts/PeyfwkRRPX4)

Geometry-node workflows tied to a Blender release need version, node availability and fallback notes in the handoff.

### BH-259: Addon Or Asset Node Tools Need License Boundaries

Sources: [704](https://www.youtube.com/shorts/9ZIQ9M8HBtQ), [720](https://www.youtube.com/shorts/C6hH_vd-bdY), [724](https://www.youtube.com/shorts/4mlBtcRPbfU)

Addon, asset-node or downloadable scattering tools need license, cache path, dependency and replacement-plan notes before production use.

## Session 015 Additions

### BH-260: Lighting Rigs Need Role Contracts

Sources: [751](https://www.youtube.com/shorts/Ta82egt3TVE), [752](https://www.youtube.com/shorts/jwp8mBjFw9w), [753](https://www.youtube.com/shorts/Z_PqXnv1wrE), [754](https://www.youtube.com/shorts/7f_nnpo5FSw), [764](https://www.youtube.com/shorts/Wrxh7XA9BjU), [769](https://www.youtube.com/shorts/FZClL30wA8k)

Lighting setups need named key, fill, rim and world roles, energy ratios, color temperature and shadow-softness checks.

### BH-261: Lighting Before After Needs Fixed Exposure

Sources: [761](https://www.youtube.com/shorts/LWjr-PAUfFM), [762](https://www.youtube.com/shorts/_UzPb7FHH8o), [763](https://www.youtube.com/shorts/Vfe94NzAyL0), [768](https://www.youtube.com/shorts/8-9Sc_27WQs)

Lighting comparisons need a fixed camera, fixed exposure and identical material state so the before/after is honest.

### BH-262: HDRI Needs Visibility And Reflection Policy

Sources: [755](https://www.youtube.com/shorts/t3S4UJZMF6M), [756](https://www.youtube.com/shorts/95lweeoyx-8), [757](https://www.youtube.com/shorts/gOHyKlfVhQY), [758](https://www.youtube.com/shorts/mxmwCjPsCwM), [759](https://www.youtube.com/shorts/lSH3WRPmnJo), [760](https://www.youtube.com/shorts/gEs_vbWflZE)

HDRI lighting needs source license, strength, rotation, blur, background visibility and diffuse/glossy/reflection behavior documented.

### BH-263: Lighting Tools Need Manual Fallback

Sources: [765](https://www.youtube.com/shorts/jzcH1CDhVs8), [766](https://www.youtube.com/shorts/hq61CLRG_dM), [767](https://www.youtube.com/shorts/wt_L2u8PT_M)

Lighting add-ons and global light controls need generated-light cleanup, grouping, locked overrides, dependency notes and reproducible manual settings.

### BH-264: Dark Backgrounds Need Separation Checks

Sources: [770](https://www.youtube.com/shorts/RWGvTNSSwuM)

Black or very dark backgrounds need rim separation, shadow detail and material readability checks so the subject does not disappear.

### BH-265: Camera DOF Needs Focus Ownership

Sources: [771](https://www.youtube.com/shorts/L4omVq18dlQ), [773](https://www.youtube.com/shorts/EFrt_pq9BF0), [774](https://www.youtube.com/shorts/AbkqnugkLig), [775](https://www.youtube.com/shorts/YoOz42w37V8)

Depth of Field needs a named focus target, f-stop, focus distance, viewport/final parity and frame-range test for animated cameras.

### BH-266: Lens Changes Need Perspective QA

Sources: [772](https://www.youtube.com/shorts/UlYwlewfcfQ)

Focal length and aperture changes need perspective, crop, DOF side effects and subject distortion checks.

### BH-267: Aspect Ratio Needs Safe Frame Review

Sources: [776](https://www.youtube.com/shorts/rY7pHoMGbZc), [777](https://www.youtube.com/shorts/_0KsmqhjTsI)

Aspect-ratio and camera-guide changes need safe frame, thirds/center guides, crop and text readability checks.

### BH-268: Transparent Renders Need Alpha Edge QA

Sources: [778](https://www.youtube.com/shorts/1pTexGQN3rc), [779](https://www.youtube.com/shorts/z64gKNAk3HY), [780](https://www.youtube.com/shorts/c9wTxaFLi6A), [781](https://www.youtube.com/shorts/SUzjwIfancM)

Transparent-background renders need Film alpha, output format, premultiply/edge review, shadow/reflection notes and target-background proof.

### BH-269: Backplates Need Matchmove-Like Checks

Sources: [782](https://www.youtube.com/shorts/EY_UGavsLYk)

Backplate renders need camera match, horizon, scale, color temperature, shadow contact and alpha behavior checks.

### BH-270: Cryptomatte Needs Naming Discipline

Sources: [783](https://www.youtube.com/shorts/9tmW0tQfvhM), [784](https://www.youtube.com/shorts/c8yJ9PCHYqA), [785](https://www.youtube.com/shorts/60afyhoM6v0)

Cryptomatte handoff needs stable object/material names, EXR pass delivery, channel compatibility and element-isolation notes.

### BH-271: Compositor Masks Need Matte Edge QA

Sources: [786](https://www.youtube.com/shorts/kv8PAy0DbPg), [787](https://www.youtube.com/shorts/Q37CzA8l9_o), [788](https://www.youtube.com/shorts/s2gwRqeBFqc)

Compositor masks and realtime compositor effects need named mask sources, edge/matte review, pass isolation and final-render parity.

### BH-272: Denoise Needs Detail And Flicker Checks

Sources: [789](https://www.youtube.com/shorts/6kmc2ViN1Ak), [790](https://www.youtube.com/shorts/ZUdWx_M9wUA), [791](https://www.youtube.com/shorts/bjDcLA9xLPo)

Denoising needs sample budget, noise threshold, before/after detail crops and animation flicker review.

### BH-273: Render Optimization Needs Quality Comparison

Sources: [792](https://www.youtube.com/shorts/CO8uM3fB1WU), [793](https://www.youtube.com/shorts/59nNe_WY1Zs)

Fast render settings need GPU/device, samples, light paths, noise threshold, denoise policy and quality/time comparison.

### BH-274: Eevee Cycles Parity Needs Feature Checklist

Sources: [794](https://www.youtube.com/shorts/N0mbUwqRTpw), [795](https://m.youtube.com/shorts/7xKm7eumYOI)

Eevee-to-Cycles parity needs SSR, AO, contact shadows, material response, hardware notes and color-management checks.

### BH-275: Volumetrics Need Density Budgets

Sources: [796](https://www.youtube.com/shorts/XpuVGKuywKo), [797](https://www.youtube.com/shorts/Uig4fEU4HEM), [798](https://www.youtube.com/shorts/6ttmci5luys)

Volumetric fog and god rays need density, bounds, step size, light direction, readability and render-time budget checks.

### BH-276: Light Linking Needs Scope Notes

Sources: [799](https://www.youtube.com/shorts/j1muitoyTfY)

Light linking needs object/collection scope, render-layer notes and a proof frame showing intended isolation.

### BH-277: Highlight Control Needs Display Review

Sources: [800](https://www.youtube.com/shorts/IB3xOmaGJ2w)

Highlight limiting needs clipping scopes, color-grade notes, display transform review and a final-output check.

### BH-278: Transparent Shadow Work Needs Destination Proof

Sources: [778](https://www.youtube.com/shorts/1pTexGQN3rc), [781](https://www.youtube.com/shorts/SUzjwIfancM), [782](https://www.youtube.com/shorts/EY_UGavsLYk)

Transparent products and overlays need shadow density, alpha behavior and destination-background proof, not just a transparent PNG.

### BH-279: Render Reviews Need Pass Accounting

Sources: [783](https://www.youtube.com/shorts/9tmW0tQfvhM), [786](https://www.youtube.com/shorts/kv8PAy0DbPg), [787](https://www.youtube.com/shorts/Q37CzA8l9_o)

Render reviews should account for beauty, alpha, masks, Cryptomatte, shadows, denoise, grade and final delivery format.

## Session 016 Additions

### BH-280: IK Chains Need Visible Control Proof

Sources: [801](https://www.youtube.com/shorts/77RvfjaWvRQ), [804](https://www.youtube.com/shorts/oNsj2a_QCbs), [810](https://www.youtube.com/shorts/1KjB2r8CuWw), [813](https://www.youtube.com/shorts/pgHLeSWGYAo), [834](https://www.youtube.com/shorts/WrDP9_yeHT8)

IK setups need named target controls, pole controls, chain length, pole angle and at least two proof poses showing the limb bends in the intended direction.

### BH-281: Constraints Need Axis And Owner Notes

Sources: [803](https://www.youtube.com/shorts/VxkWd2qEPi8), [807](https://www.youtube.com/shorts/Ux9jGvYTXVs), [825](https://www.youtube.com/shorts/UstdP0qm7g4), [830](https://www.youtube.com/shorts/ySsTgrXUxAw), [831](https://www.youtube.com/shorts/lvKjAGZVWqQ), [835](https://www.youtube.com/shorts/jItyBXRpygI)

Copy Rotation, Limit Rotation, Damped Track and mechanical constraints need documented target objects, axis filters, spaces, influence values and pose-range tests.

### BH-282: Shape Keys Need Driver Maps

Sources: [802](https://www.youtube.com/shorts/SAX7T69OmxE), [805](https://www.youtube.com/shorts/bpnj9U5Qv74), [808](https://www.youtube.com/shorts/et1mers52Bc), [814](https://www.youtube.com/shorts/ftw0gwfuqcY)

Shape-key rigs need a driver map from controller to key, min/max clamps, mirrored-name checks and debug sliders for manual override.

### BH-283: Corrective Shapes Need Problem-Pose Snapshots

Sources: [817](https://www.youtube.com/shorts/45ZX6HcmIo4), [836](https://www.youtube.com/shorts/Zr-2IcjTkFk)

Corrective shapes should be authored against saved problem poses and reviewed with before/after silhouettes at mid and extreme bend angles.

### BH-284: Weight Transfer Needs Assumption Logs

Sources: [838](https://www.youtube.com/shorts/fYvXstKmo-c), [842](https://www.youtube.com/shorts/C8SUpMcQfeU), [845](https://www.youtube.com/shorts/dC-SJtXjIDs)

Weight-transfer workflows need source/target topology assumptions, selected vertex groups, material/UV retention checks and a fallback repaint pass.

### BH-285: Auto Weights Need Topology Preflight

Sources: [824](https://www.youtube.com/shorts/fQbMJp0PS7g), [839](https://www.youtube.com/shorts/y4f9FyWbz_Q), [850](https://www.youtube.com/shorts/ovI1RRn5_Qk)

Automatic weights should run only after scale, normals, loose parts and mirror naming are checked, then be corrected manually at elbows, tails, wings and cloth edges.

### BH-286: Armature Deform Needs Modifier QA

Sources: [809](https://www.youtube.com/shorts/eRG43asq2bU), [843](https://www.youtube.com/shorts/DACNkSbUL2o)

Armature deformation failures should be debugged through parenting mode, modifier order, applied scale, vertex-group names and a simple bind-pose deformation test.

### BH-287: Mechanical Rigs Need Pivot Markers

Sources: [807](https://www.youtube.com/shorts/Ux9jGvYTXVs), [819](https://www.youtube.com/shorts/kIwCs2eJP4o), [822](https://www.youtube.com/shorts/Rf57K1zWqFQ), [827](https://www.youtube.com/shorts/u74TJJS3gCw), [847](https://www.youtube.com/shorts/HI4M-D0fJQ4)

Hard-surface rigs should show pivots, hinge axes, parent order and direct-bone parenting so rigid parts do not deform like skin.

### BH-288: Preserve Volume Is A Checkpoint, Not A Finish Line

Sources: [815](https://www.youtube.com/shorts/sxibKqmndek), [803](https://www.youtube.com/shorts/VxkWd2qEPi8), [836](https://www.youtube.com/shorts/Zr-2IcjTkFk)

Preserve Volume can reduce twist collapse, but the final gate is still silhouette, compression, texture stretching and joint readability in animated poses.

### BH-289: Face And Eye Rigs Need Follow Policies

Sources: [811](https://www.youtube.com/shorts/NRQbXpsxuMs), [814](https://www.youtube.com/shorts/ftw0gwfuqcY), [849](https://www.youtube.com/shorts/_PooSTDZ3FQ)

Eyes, pupils, eyelids and face plates need independent controls plus explicit follow-body constraints so offsets survive body motion.

### BH-290: Rig Animation Cleanup Needs Action Accounting

Sources: [820](https://www.youtube.com/shorts/UoTWjbn13ms)

Before publishing a rigged file, audit actions, NLA strips, fake users, orphan data and unwanted baked experiments so the file opens predictably.

### BH-291: Constraint Baking Needs Export Tests

Sources: [823](https://www.youtube.com/shorts/AU1C-l8D8ow)

Constraint-driven animation should be baked over the intended frame range, then reloaded or exported to prove motion survives outside the Blender dependency graph.

### BH-292: NLA Mixing Needs Root And Foot Checks

Sources: [832](https://www.youtube.com/shorts/uxPJbwXLqJs), [846](https://www.youtube.com/shorts/RgcR5W752kM)

Animation clip mixing needs root alignment, transition overlap, stride/foot-sliding review and a single explicit root-motion owner for game or web export.

### BH-293: Motion Paths Are Timing QA

Sources: [833](https://www.youtube.com/shorts/sKx216kVLI0), [840](https://www.youtube.com/shorts/uQGpz28dA0g)

Motion paths should be checked on key controllers to reveal spacing, arc breaks, tail follow-through and accidental pops between keys.

### BH-294: Controller Organization Prevents Animator Errors

Sources: [837](https://www.youtube.com/shorts/R1lQV0K21Q4), [841](https://www.youtube.com/shorts/cjgqrO6pxf4), [844](https://www.youtube.com/shorts/dxtrdI5cTlQ)

Dense rigs need bone collections, selection sets, custom control shapes and locked transforms so the animator touches controls, not deformation bones.

### BH-295: Clothing Deformation Needs Clipping Sweeps

Sources: [818](https://www.youtube.com/shorts/5wJTQu9CTio), [842](https://www.youtube.com/shorts/C8SUpMcQfeU), [845](https://www.youtube.com/shorts/dC-SJtXjIDs)

Clothing rigs need transfer weights plus pose sweeps for shoulders, elbows, knees and torso bends to catch clipping before render/export.

### BH-296: Symmetry Work Needs Naming Discipline

Sources: [805](https://www.youtube.com/shorts/bpnj9U5Qv74), [828](https://www.youtube.com/shorts/YY3QFnWTAPM), [848](https://www.youtube.com/shorts/1axVvl-7NQ4)

Mirroring shape keys, weights or mesh edits depends on origin, mirror plane, left/right names and a final asymmetric-pose check.

### BH-297: Joining Rig Parts Needs Data Preservation Checks

Sources: [829](https://www.youtube.com/shorts/Dq_y02NOsY8)

Joining objects in rig prep should preserve UV maps, material slots, vertex groups and custom normals, otherwise downstream deformation and textures can silently break.

### BH-298: Neck And Head Rigs Need Isolation Switches

Sources: [821](https://www.youtube.com/shorts/OpkCwxa3pdQ), [816](https://www.youtube.com/shorts/F5wlEjgBqRw)

Head/neck setups need separate control/deform bones, isolation switches and reset checks so local head motion can coexist with full-body control.

### BH-299: Rig Export Gates Need Control Filtering

Sources: [801](https://www.youtube.com/shorts/77RvfjaWvRQ), [823](https://www.youtube.com/shorts/AU1C-l8D8ow), [846](https://www.youtube.com/shorts/RgcR5W752kM)

Rigged exports need a clear decision on whether controls, helpers, constraints and baked animation are included, filtered or converted before GLB delivery.

## Session 017 Additions

### BH-300: Topology Cleanup Needs Before/After Mesh Proof

Sources: [851](https://www.youtube.com/shorts/a0KN6xr0Yq4), [852](https://www.youtube.com/shorts/E1KPr8rSBzE), [897](https://www.youtube.com/shorts/OjoFBONdzcA), [898](https://www.youtube.com/shorts/aLvw3g4uhw4)

Topology cleanup should be recorded with before/after mesh proof, duplicate-vertex checks, non-manifold checks and face-orientation overlays.

### BH-301: N-Gons And Booleans Need Risk Maps

Sources: [853](https://www.youtube.com/shorts/pOlWCFOBx6Q), [854](https://www.youtube.com/shorts/0fl4l3HX8Zk)

N-gons and boolean cuts need visible risk maps for beveling, subdivision, deformation, normal shading and export triangulation.

### BH-302: Automated Retopo Is Draft Topology

Sources: [856](https://www.youtube.com/shorts/l0L1uSDOOgk), [857](https://www.youtube.com/shorts/83CkDwloYg8), [858](https://www.youtube.com/shorts/x2qg18AhDJA), [859](https://www.youtube.com/shorts/A8UKyOZe5R0)

Auto-remesh and one-click retopo outputs need edge-flow, loop-density, deformation-zone and silhouette QA before being accepted.

### BH-303: Sculpt Remesh Needs Resolution Budgets

Sources: [860](https://www.youtube.com/shorts/DxcthXYiM6s), [861](https://www.youtube.com/shorts/OgL4MFLNaUQ), [862](https://www.youtube.com/shorts/4WCuMszwM2U)

Voxel, quad and multires sculpt workflows need resolution budgets, feature-loss checks and a clear high-poly-to-low-poly handoff.

### BH-304: High-Low Baking Needs A Cage Contract

Sources: [863](https://www.youtube.com/shorts/cissl9LKiUY), [864](https://www.youtube.com/shorts/RKpGTquQPuE), [865](https://www.youtube.com/shorts/9KLSdTvh-Lk), [866](https://www.youtube.com/shorts/99Cc2TliKDs), [867](https://www.youtube.com/shorts/aT9PMmE6sno)

Normal and texture baking need matched high/low names, scale parity, cage distance, ray-miss review, margin and tangent-space verification.

### BH-305: Normal Details Need Seam-Safe Placement

Sources: [868](https://www.youtube.com/shorts/x78frOrPBdU), [865](https://www.youtube.com/shorts/9KLSdTvh-Lk)

Normal-map stamps and baked details need UV scale, orientation, seam distance and flat-light artifact checks.

### BH-306: UV Seams Need Intent

Sources: [869](https://www.youtube.com/shorts/UhJZ0fIg4KY), [870](https://www.youtube.com/shorts/tS63p4eOWV8), [871](https://www.youtube.com/shorts/gWX1aS4bDgI), [872](https://www.youtube.com/shorts/FvS8l1HYOFA)

UV seams should be chosen for hidden edges, deformation breaks, texture direction and unwrap stability, then tested with checker distortion.

### BH-307: UV Transfer And Mirror Need Orientation QA

Sources: [873](https://www.youtube.com/shorts/S84tAVjdce4), [874](https://www.youtube.com/shorts/YntO7LmuY8E)

UV transfer and mirrored UVs need object naming, island overlap policy, text direction and tangent-space normal checks.

### BH-308: UV Packing Needs Texel And Margin Proof

Sources: [876](https://www.youtube.com/shorts/EUvuEQULUWc), [877](https://www.youtube.com/shorts/HREG5VWajVY), [878](https://www.youtube.com/shorts/GC9ip1H-DjY), [879](https://www.youtube.com/shorts/Dz781b0ABkk)

Packed UVs need target texture resolution, texel-density consistency, island padding and stretch-overlay proof.

### BH-309: UV Add-Ons Need Fallbacks

Sources: [875](https://www.youtube.com/shorts/Teoom9gYPEE), [876](https://www.youtube.com/shorts/EUvuEQULUWc)

UV add-on workflows need dependency/license notes and a manual seam/pack fallback for reproducible production files.

### BH-310: Bevel And Weighted Normals Need A Shading Contract

Sources: [880](https://www.youtube.com/shorts/KMM8-bjcRsg), [881](https://www.youtube.com/shorts/X3xj7BRJleY), [882](https://m.youtube.com/shorts/2ViHOTDmA00), [883](https://www.youtube.com/shorts/fVVbTgKyfYA)

Bevel and Weighted Normal setups need named width, segment, clamp, profile and modifier-order choices plus a flat-light shading check.

### BH-311: Hard-Surface Topology Needs Edge Policy

Sources: [884](https://www.youtube.com/shorts/CfdwW3fz0eg), [885](https://www.youtube.com/shorts/7tehyvzCd4o), [886](https://www.youtube.com/shorts/Qdva4Kz_3p8), [890](https://www.youtube.com/shorts/ocqYzvw3GQc)

Hard-surface assets need support-loop, bevel, crease/subdivision and weighted-normal policy before details are added.

### BH-312: Blockouts Need Cleanup Gates

Sources: [887](https://www.youtube.com/shorts/TizYmOl27VQ), [888](https://www.youtube.com/shorts/jCFC6iOUh0c), [889](https://www.youtube.com/shorts/Q6UabdJThy0)

Blockouts should pass seam, bevel, cap topology, modifier-order and material-slot cleanup before being called asset-ready.

### BH-313: Bevel Tricks Still Need Topology Review

Sources: [891](https://www.youtube.com/shorts/e7_cPqFKoa8), [883](https://www.youtube.com/shorts/fVVbTgKyfYA)

Any bevel trick should be followed by segment, profile, clamp, n-gon and shading review instead of being trusted visually.

### BH-314: Normals Need Face-Orientation Proof

Sources: [892](https://www.youtube.com/shorts/lPoaeVu6g5Q)

Normal fixes need face-orientation proof, recalculation, material-side checks and GLB viewer validation.

### BH-315: Edge Flow Is Shape QA

Sources: [893](https://www.youtube.com/shorts/wedGVKPYcEM), [894](https://www.youtube.com/shorts/86Y7hdruQSY), [899](https://www.youtube.com/shorts/Kfulk3nChns)

Straightening edges, editing edge flow and smoothing vertices should be judged by loop continuity, silhouette and volume preservation.

### BH-316: Extrude And Dissolve Need Manifold Checks

Sources: [895](https://www.youtube.com/shorts/DcbMRKDrt84), [896](https://www.youtube.com/shorts/nD90P5_1iuk), [900](https://www.youtube.com/shorts/b-UQ6ye4jf0)

Extrude, edge removal and limited dissolve operations need duplicate-face, hole, manifold, UV and normal-preservation checks.

### BH-317: Modifier Stacks Need Export Order

Sources: [880](https://www.youtube.com/shorts/KMM8-bjcRsg), [889](https://www.youtube.com/shorts/Q6UabdJThy0), [890](https://www.youtube.com/shorts/ocqYzvw3GQc)

Bevel, solidify, subdivision, weighted normal and decimation stacks need a declared order and export/apply policy.

### BH-318: Simplification Needs Preservation Metrics

Sources: [855](https://www.youtube.com/shorts/hTz0dSSwQyw), [900](https://www.youtube.com/shorts/b-UQ6ye4jf0)

Simplification should report triangle savings plus silhouette, UV and normal preservation instead of only lower counts.

### BH-319: Mesh Handoff Needs A Full Asset Checklist

Sources: [851](https://www.youtube.com/shorts/a0KN6xr0Yq4), [863](https://www.youtube.com/shorts/cissl9LKiUY), [877](https://www.youtube.com/shorts/HREG5VWajVY), [892](https://www.youtube.com/shorts/lPoaeVu6g5Q), [900](https://www.youtube.com/shorts/b-UQ6ye4jf0)

Before handoff, a mesh asset needs topology, UV, normals, bake, modifiers, material slots, triangle budget and GLB export checks in one report.

## Session 018 Additions

### BH-320: Line Art Needs Layer Ownership

Sources: [901](https://www.youtube.com/shorts/tT9u9DLmsOs), [902](https://www.youtube.com/shorts/yij-XT3fLPc), [903](https://www.youtube.com/shorts/h8q6NrFZS_M), [909](https://www.youtube.com/shorts/ZypT4iqD_Q0)

Grease Pencil and Line Art shots need source collection, layer ownership, edge filters, camera scope and render/export parity checks.

### BH-321: Comic Outlines Need Thickness Budgets

Sources: [904](https://www.youtube.com/shorts/a9Ne3OItW3Y), [912](https://www.youtube.com/shorts/VYOUzhI6xPw), [916](https://www.youtube.com/shorts/cyUKq1xSRYs), [918](https://www.youtube.com/shorts/rgUWpRN3ZiA), [919](https://www.youtube.com/shorts/f4n8m3mmugw)

Stylized outlines need line thickness, occlusion, camera distance, material behavior and export fallback notes.

### BH-322: Grease Pencil Cleanup Needs Frame-Range Proof

Sources: [905](https://www.youtube.com/shorts/PxHgetMsoQU), [906](https://www.youtube.com/shorts/YWWrrV0cGXw), [908](https://www.youtube.com/shorts/cHBAtTAFLdw), [911](https://www.youtube.com/shorts/GjNZFYuvRas), [914](https://www.youtube.com/shorts/XUaUnpzfeiE)

Stroke cleanup, fills, extensions and imported drawings need layer naming, point-density cleanup, gap checks and frame-range proof.

### BH-323: Boiling Lines Need Loop Discipline

Sources: [907](https://www.youtube.com/shorts/K_epbDC_qOg), [913](https://www.youtube.com/shorts/NMhwJaORKCk)

Boiling lines need controlled noise amplitude, per-layer seeds and first/last-frame continuity so the effect feels intentional.

### BH-324: Imported Sketches Need Source And Scale Notes

Sources: [910](https://www.youtube.com/shorts/jluGZwLynmc), [915](https://www.youtube.com/shorts/18Htx0uVdb0)

Imported sketches and vector exports need source rights, trace cleanup, scale alignment and downstream app verification.

### BH-325: Glow Outlines Need Separate Emission Controls

Sources: [917](https://www.youtube.com/shorts/YaxMk6nGF7c), [904](https://www.youtube.com/shorts/a9Ne3OItW3Y)

Glow outlines need visible stroke controls separated from bloom, emission intensity and final display exposure.

### BH-326: Graph Editor Polish Needs F-Curve Evidence

Sources: [920](https://www.youtube.com/shorts/ySHzAL_ZYwA), [921](https://www.youtube.com/shorts/WQw9jBDo7-0), [922](https://www.youtube.com/shorts/Kvt8dvV_D_8), [923](https://www.youtube.com/shorts/S4PpnlE-qoc)

Animation polish should show F-curve handles, channel filtering, spacing and overshoot checks, not only more keyframes.

### BH-327: Extrapolation Needs Endpoint Policy

Sources: [924](https://www.youtube.com/shorts/HvuDqDgGLME), [927](https://www.youtube.com/shorts/Vv87FIkQU9I), [929](https://www.youtube.com/shorts/ydaXoJC2-FM), [938](https://www.youtube.com/shorts/eTe0a9uy0hw)

Extrapolation and interpolation modes need explicit cycle, linear, constant and duplicate-end-frame policies.

### BH-328: Procedural Sway Needs Phase Controls

Sources: [925](https://www.youtube.com/shorts/Ac9umG7Mnhw), [926](https://www.youtube.com/shorts/LiByoYZ3ZMk), [937](https://www.youtube.com/shorts/iueVZuQGckU)

Sine/noise sway needs amplitude, phase, seed and channel isolation, plus loopability proof.

### BH-329: Seamless Loops Need Frame Proof

Sources: [927](https://www.youtube.com/shorts/Vv87FIkQU9I), [928](https://www.youtube.com/shorts/J0HtIYwDmG8), [930](https://www.youtube.com/shorts/qCpED44qZko), [931](https://www.youtube.com/shorts/ifUEbZ1cqfw), [932](https://m.youtube.com/shorts/lkuScmF4OrA)

Seamless loops need first/last state comparison, phase checks, axis ownership and material-value loop verification.

### BH-330: Motion Blur Needs Object Policy

Sources: [933](https://www.youtube.com/shorts/qbehV-YyQMc), [934](https://www.youtube.com/shorts/Y32pHUN8lms), [935](https://www.youtube.com/shorts/xZQNYlkbUOo)

Motion blur needs shutter, samples, per-object exclusions, render-time limits and readability proof frames.

### BH-331: Camera Cuts Need Timeline Notes

Sources: [936](https://www.youtube.com/shorts/2jpIhkgaPWw)

Camera jump cuts need markers, frame ranges, continuity notes and delivery aspect-ratio review.

### BH-332: Animation Add-Ons Need Manual Proof

Sources: [939](https://www.youtube.com/shorts/OWxWiQiH90k)

Animation add-ons can speed up loops, but need dependency notes and manual first/last-frame proof.

### BH-333: Asset Browser Needs Catalog Discipline

Sources: [940](https://www.youtube.com/shorts/Wn57c20CMFw), [941](https://www.youtube.com/shorts/eNiAA9GsRFY), [943](https://www.youtube.com/shorts/aXUjRAfX7lE)

Asset Browser workflows need catalogs, tags, preview thumbnails, version notes, dependencies and license/source fields.

### BH-334: Cross-File Reuse Needs Dependency Checks

Sources: [942](https://www.youtube.com/shorts/lKFdBdWa41M), [949](https://www.youtube.com/shorts/yjmbWFnmyaw)

Copying or linking assets across files needs material, scale, library path, override and animation dependency checks.

### BH-335: Asset Switching Needs Realization Gates

Sources: [944](https://www.youtube.com/shorts/UIRQCz0KNLk), [946](https://www.youtube.com/shorts/JhGVktxT2ZQ)

Collection Info, Index Switch and instancing workflows need naming, seed, density, realization and export-budget gates.

### BH-336: Material Reuse Needs Duplicate Cleanup

Sources: [945](https://www.youtube.com/shorts/pM8uPpRQFQo)

Material reuse needs catalog strategy, duplicate material cleanup, color-space checks and re-link notes.

### BH-337: GLB Optimization Needs Visual Regression Checks

Sources: [947](https://www.youtube.com/shorts/cAWVpe-jg5Q)

GLB optimization needs texture resolution, compression, geometry and material checks against a pre-optimization preview.

### BH-338: Texture Export Needs Re-Link QA

Sources: [948](https://www.youtube.com/shorts/YYUt7BRooL4)

Texture export needs file format, color space, naming, packing/unpacking and material re-link checks.

### BH-339: Physics Scatter Needs Bake And Cleanup Policy

Sources: [950](https://www.youtube.com/shorts/jNxTUnqKk30)

Physics scatter and asset-library scattering need source asset notes, simulation bake, cleanup, seed and instance/realize policy.

## Session 019 Additions

### BH-340: Cloth Pinning Needs Vertex-Group Proof

Sources: [951](https://www.youtube.com/shorts/EsIdAdj-sXw), [953](https://www.youtube.com/shorts/Hmfa2J0Y6Wg), [954](https://www.youtube.com/shorts/D3WawkUpbPo)

Cloth pinning needs named vertex groups, weight proof, pinned/loose edge policy, wind direction and cache frame-range checks.

### BH-341: Cloth Collision Needs Pose Sweeps

Sources: [952](https://www.youtube.com/shorts/lJgeLvbKHeE), [960](https://www.youtube.com/shorts/Eok-cLM21Vc)

Cloth collision fixes need collision thickness, self-collision, scale, animated pose sweeps and cache-stability proof.

### BH-342: Soft Furnishing Sims Need Final Freeze Policy

Sources: [955](https://www.youtube.com/shorts/mLnhyokj_kA), [956](https://www.youtube.com/shorts/zvdQnlN5H5s), [957](https://www.youtube.com/shorts/2Txv4T1jxaE), [958](https://www.youtube.com/shorts/zkx5MQq6Lxo), [959](https://www.youtube.com/shorts/gWeuYx0cxRo)

Pillows, blankets and bedding sims need pressure, wrinkles, seam shaping, thickness, cache reuse and final freeze/apply decisions.

### BH-343: Hair Needs Strand Budget Discipline

Sources: [961](https://www.youtube.com/shorts/B0erUgje7VQ), [963](https://www.youtube.com/shorts/QlRa38D-VKs), [967](https://www.youtube.com/shorts/74CxVUTWruA), [968](https://www.youtube.com/shorts/knkqr4sqXos)

Hair and fur setups need guide smoothness, length, density, children, interpolation and viewport/render strand budgets.

### BH-344: Hair Grooming Needs Fallbacks

Sources: [962](https://www.youtube.com/shorts/j-nD0JfYIP0), [966](https://www.youtube.com/shorts/AMHb2NqIqw4)

Hair grooming add-ons and mirror fixes need dependency notes, object transform checks, symmetry proof and manual grooming fallback.

### BH-345: Hair Dynamics Need Versioned Cache Proof

Sources: [964](https://www.youtube.com/shorts/Ad7R3TgLQaI), [965](https://www.youtube.com/shorts/0nw7W2AcUXQ), [969](https://www.youtube.com/shorts/rQCxebMc6H4), [970](https://www.youtube.com/shorts/vQPFAhKDTV4), [1000](https://www.youtube.com/shorts/YssKo8aQHjc)

Hair dynamics need Blender version notes, solver/cache proof, collision, wind strength, bake policy and fallback for experimental features.

### BH-346: Smoke Sims Need Memory Budgets

Sources: [971](https://www.youtube.com/shorts/o099XQW9p34), [972](https://www.youtube.com/shorts/NCaWbiZZlAI), [973](https://www.youtube.com/shorts/MHWQe9YdshM)

Smoke sims need domain bounds, resolution, interpolation, step size, cache size and quality/time comparison.

### BH-347: Fluid Sims Need Domain/Flow Naming

Sources: [974](https://www.youtube.com/shorts/PELnlc43nX4), [975](https://www.youtube.com/shorts/BGGi_uPUYCE), [976](https://www.youtube.com/shorts/hT64HFXjU08)

Fluid sims need named domain, flow and effector objects, collision proof, cache policy and mesh/export decision.

### BH-348: Particles Need Seed And Density Gates

Sources: [977](https://www.youtube.com/shorts/15d9yWT5A4Y), [978](https://www.youtube.com/shorts/X_-E8-3ZM5A), [999](https://www.youtube.com/shorts/PgCXYuNMQdg)

Particles and weather systems need minimum-distance, seed, density, collision, visibility, cache and render budget gates.

### BH-349: Render Passes Need Pass Accounting

Sources: [979](https://www.youtube.com/shorts/hcE389sUg2U), [981](https://www.youtube.com/shorts/tCCSzuqihrQ), [982](https://www.youtube.com/shorts/0qGqEyaYK3I)

Render-pass workflows need pass selection, preview, naming, overrides, output paths and downstream handoff notes.

### BH-350: View Layers Need Collection Contracts

Sources: [980](https://www.youtube.com/shorts/Q5viIxJbiaU), [982](https://www.youtube.com/shorts/0qGqEyaYK3I)

View layers need collection masks, holdouts, material overrides, relight/composite plan and output path discipline.

### BH-351: Depth/Position Passes Need Space Notes

Sources: [983](https://www.youtube.com/shorts/y-2yERk2HGQ), [985](https://www.youtube.com/shorts/OX2W6diBDoE)

Mist, Z-depth and position passes need camera clipping, depth range, coordinate-space notes and downstream app compatibility checks.

### BH-352: Compositor Blur Needs Vector Proof

Sources: [984](https://www.youtube.com/shorts/K2HwZk-lYXw)

Vector blur in compositing needs a vector pass, quality settings, render-time comparison and artifact review.

### BH-353: Shadow Catchers Need Destination Proof

Sources: [986](https://www.youtube.com/shorts/G9yPhDLGBuQ)

Shadow-only transparent renders need alpha behavior, shadow density and proof over the intended destination background.

### BH-354: Cinematic Composites Need Before/After Reviews

Sources: [987](https://www.youtube.com/shorts/ud2jbjbfk4g), [988](https://www.youtube.com/shorts/GNSKLmmJops)

Cinematic compositing and Nuke handoff need denoise data, grade, channel naming, pass compatibility and before/after proof.

### BH-355: GLTF Export Needs Transform And Material Checks

Sources: [989](https://www.youtube.com/shorts/FJHVhRpOm1k), [992](https://www.youtube.com/shorts/2VJJANVIY5Y), [997](https://www.youtube.com/shorts/MJDzfNa5csE), [998](https://www.youtube.com/shorts/GEdh_96PhpE)

GLTF/GLB scene export needs transforms, scale, material simplicity, texture links, node cleanup, animation and target platform verification.

### BH-356: Vertex Animation Export Needs Viewer Tests

Sources: [990](https://www.youtube.com/shorts/awArQyvncmU), [994](https://www.youtube.com/shorts/sgMp3U0tomg)

Vertex animation and Grease Pencil GLB exports need conversion strategy, material checks and target-viewer tests.

### BH-357: Game Collision Exports Need Naming Discipline

Sources: [991](https://www.youtube.com/shorts/rC3h1vumRxQ)

Game collision exports need collision object naming, scale, engine import proof and non-render helper filtering.

### BH-358: Texture Bake/Export Needs Relink QA

Sources: [993](https://www.youtube.com/shorts/jmrkVa5arrQ), [996](https://www.youtube.com/shorts/GF2tCfqD5C8)

Texture baking and image-plane workflows need file naming, color space, margin, packing/unpacking, alpha mode and material relink checks.

### BH-359: Destructive Cleanup Needs Deform Proof

Sources: [995](https://www.youtube.com/shorts/f5FUlxPpmCE)

Removing armatures or destructive helpers needs apply/bake decisions, scale proof, deformation before/after checks and old-data cleanup.
