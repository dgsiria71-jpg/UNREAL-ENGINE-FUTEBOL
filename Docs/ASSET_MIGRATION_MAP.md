# ASSET / GAMEPLAY MIGRATION MAP

Current physical sources in this bundle include the full current `assets.zip`, gameplay/data focused archives, models focused archive, ARM64/ARM32 native libraries and UnityDataAssetPack.

Priority mapping:
- `assets/config/match` → normalized gameplay tables (ActionFit, ActionSpeed, Collision, Shoot/Pass/Dribble/Tackle/GK etc.)
- `assets/LocalSettings` → readable tuning/config
- `assets/ai_configs/running` → behavioral/AI source data
- `assets/xplayable` → playable/animation source
- `assets/cofmotions` + `controller.ctrl` → animation database / contact metadata source
- `assets/nova_player` + `assets/fbxs` + `assets/prefabs` → Blender/Unreal mesh/rig/material/prefab conversion source
- `assets/timeline` → timeline/action sequence source
- `assets/sceneres` → stadium/scene resources
- `libil2cpp.so` → native gameplay implementation reference
- `global-metadata.dat` → REQUIRED pair for deeper IL2CPP mapping, but unavailable in current physical runtime because `com.estar.bap.zip` is missing here.

Do not assume extensionless `fbxs` entries are ready-made FBX files; they are Unity serialized assets requiring proper export/conversion.
