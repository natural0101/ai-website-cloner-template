# Third-party assets

## Shadow Hand E3M5

- Source: https://github.com/google-deepmind/mujoco_menagerie/tree/main/shadow_hand
- Source revision: `71f066ad0be9cd271f7ed58c030243ef157af9f4`
- Copyright: 2022 Shadow Robot Company Ltd
- License: Apache License 2.0
- Local license copy: `mujoco_menagerie/shadow_hand/LICENSE`

The TEAMON scene imports the original OBJ geometry and MJCF kinematic hierarchy,
changes the pose and materials, and converts the result to Blender and glTF/GLB
formats. The upstream files under `mujoco_menagerie/shadow_hand` are retained
unchanged. This asset is retained only for the rejected TEAMON v4 checkpoint
and is not used by the current v5 web scene.

## ORCA Hand v2

- Source: https://github.com/orcahand/orcahand_description
- Source revision: `b9b349a21ee0238c62b6cf92ae7597027867adf8`
- Copyright: 2025 ORCA Dexterity, Inc.
- License: MIT
- Local license copy: `orcahand_description/LICENSE`

The archived TEAMON v7 scene imports the official right-hand STL geometry and
MJCF hierarchy, changes the pose and materials, decimates only the Blender/web
copies, and adds a tapered reference-matching cuff shell parented to the hand
root. Upstream files under
`orcahand_description` are retained unchanged.

## RUKA Hand v2

- Source: https://github.com/ruka-hand-v2/RUKA-v2
- Source revision: `f19818821c90f985be30ce3ea7b35e5c5db6b7ce`
- License: MIT
- Local license copy: `RUKA-v2/LICENSE`

RUKA-v2 was imported from its official URDF/STL hierarchy for a documented
TEAMON v7 shape probe. Its fixed base was excluded from the hero probe. The
probe was rejected in favor of ORCA because the visible finger mechanics were
farther from the supplied reference. Upstream files under `RUKA-v2` are
retained unchanged.

## Rebelia / Yeah Hand V2

- Source: https://github.com/opsobot/rebelia
- Source revision: `41f2708999a01f8dd815642889281cea8bb1c0e9`
- Project page: https://hackaday.io/project/204373-yeah-robotic-hand-formerly-rebelia
- License for CAD/hardware: CERN Open Hardware Licence Strongly Reciprocal v2 (`CERN-OHL-S-2.0`)
- Local source design file: `rebelia-v2/Rebelia - Hierarchic.blend`
- Local upstream license notice: `rebelia-v2/LICENSE`

The rejected TEAMON v10 checkpoint uses evaluated copies of the official Rebelia V2
forearm cover, dorsal/palm shells, one complete straight finger, and the
complete pre-flexed printable finger. The pre-flexed finger is instanced for
the other fingers and thumb, positioned and scaled in Blender, and exported
with the original fixed-revision source design file retained beside this
notice. The source `.blend` remains unchanged.

## OpenBionics Ada v1.1

- Source: https://github.com/Open-Bionics/Ada_3D_model_files
- Source revision: `2dbf3cc6c5df112066f12c11af1d001e319a766f`
- Copyright: Open Bionics
- License: Creative Commons Attribution-ShareAlike 4.0 International (`CC BY-SA 4.0`)
- Local source design file: `openbionics-ada-v1.1/Ada Right v1.1.blend`
- Local source record: `openbionics-ada-v1.1/SOURCE.md`
- Local upstream license link: `openbionics-ada-v1.1/UPSTREAM_LICENSE.url`

The TEAMON v12 work uses evaluated copies of the official Ada v1.1 right-hand
palm, thumb, and four fingers. The source `.blend` is retained unchanged. Pose,
materials, scene scale, animation, and web export are adaptations and remain
subject to attribution and ShareAlike requirements.

## PSYONIC Ability Hand

- Source: https://github.com/psyonicinc/ability-hand-api
- Source revision: `34c9a9324d3739d976e6de441e56ccefafd0000b`
- Copyright: 2024 PSYONIC Inc.
- License: MIT
- Local upstream license: `ability-hand-api/LICENSE`
- Local right-hand URDF: `ability-hand-api/URDF/ability_hand_right_large.urdf`

The current TEAMON v15 scene imports the official articulated right-hand URDF
visual meshes, poses the index as the contact finger and curls the remaining
fingers, assigns new presentation materials, and exports an adapted Blender and
glTF/GLB composition. The upstream repository is retained at the fixed revision
listed above.
