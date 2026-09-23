---
name: blender-structural-qa
description: Use for multi-part objects, hands, fingers, mascots, furniture, tubes, assemblies, or any result with possible gaps/floating components.
license: MIT
---

# Structural QA

1. Define expected contacts in the scene graph before modeling.
2. Use stable names for every semantic part.
3. Measure world-space bounds; do not derive dimensions from unapplied local scale alone.
4. For every expected `TOUCHES/OVERLAPS` relation, record tolerance/minimum overlap.
5. Run `scene_qa.audit_scene()` after blockout and before export.
6. Treat `potential_floating_components` as a warning requiring multi-view inspection.
7. Check fingers/limbs at palm or body junctions; tube-like appearance usually means missing transition volume.
8. Check negative/unapplied scale, loose vertices, degenerate faces and non-manifold counts.
9. Do not join all parts merely to hide gaps. Preserve sources and create a fused output copy when needed.
10. Approve only when expected contacts pass and no unintended intersections remain.
