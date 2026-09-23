# Краткий API catalog

## JSON вызов

```python
import shape_dispatcher

print(shape_dispatcher.dispatch_json({
    "action": "shape.create_hand_sphere",
    "arguments": {
        "name": "Hero",
        "sphere_radius": 1.0,
        "merge_hands": True,
        "voxel_size": 0.055
    }
}))
```

## `shape.create_part`

```json
{
  "action": "shape.create_part",
  "arguments": {
    "kind": "ELLIPSOID",
    "name": "Palm",
    "location": [0, 0, 0],
    "scale": [0.8, 0.35, 1.0],
    "material": {
      "base_color": [0.95, 0.45, 0.62, 1],
      "roughness": 0.5
    },
    "collection_name": "ABT_SOURCE",
    "export": false
  }
}
```

`kind`:

- `ELLIPSOID`: `location`, `scale`, optional `radius`, `rotation`;
- `ROUNDED_BOX`: `location`, `dimensions`, `radius`, `rotation`;
- `TUBE`: `points`, scalar/list `radii`, optional resolutions/endcaps.

## `shape.voxel_union`

```json
{
  "action": "shape.voxel_union",
  "arguments": {
    "source_names": ["Palm", "Finger", "Finger_EndCap"],
    "name": "Hand_Merged",
    "voxel_size": 0.04,
    "smooth_factor": 0.25,
    "smooth_iterations": 2,
    "output_collection": "ABT_OUTPUT",
    "export": true
  }
}
```

Dispatcher сохраняет исходники независимо от аргументов.

## Reference camera

`world_height` — вертикальный размер кадра в Blender units. Tool сам переводит его в Blender `ortho_scale` с учётом aspect ratio.
