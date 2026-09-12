# RECOVERY GAPS — HONEST STATUS

This consolidation was built after searching current conversation uploads, File Library history, project memory, the available local runtime, the connected GitHub installation and the only ProductOS workspace currently exposed.

## Recovered physically now
- assets.zip
- GAMEPLAY_DATA_CORE.zip
- GAMEPLAY_MODELS_CORE.zip
- config.arm64_v8a.zip
- config.armeabi_v7a.zip
- UnityDataAssetPack.zip
- current inventory/transcript/screenshots
- regenerated focused XPLAYABLE/COFMOTION/TIMELINE/CONFIG/AI/SCENERES archives
- extracted current native libraries and Unity support files

## Recovered historically, bytes NOT currently available
The old generated release ZIPs listed in `HISTORICAL_RELEASES.json`, including Animation Recovery v1.0 and Physics Recovery v0.2. Their hashes/test results are preserved from durable transcripts, but the original ZIP bytes are not silently fabricated.

## Missing base APK bytes in current runtime
`com.estar.bap.zip` was uploaded in the earlier conversation and is confirmed by historical transcript, but it is not mounted in the current runtime/library result. Therefore `global-metadata.dat` and `data.unity3d` are not in this new archive. Add the original base APK ZIP later and rerun `04_TOOLS/augment_master_from_base_apk.py`.

## Historical 92/92 workspace
Known to have existed after Physics v0.2; not physically found in accessible local/ProductOS/GitHub sources. The checkpoint is preserved, but this consolidation does not claim to be that exact workspace.

## Current assets.zip versus historical StreamingAssets count
Current `assets.zip`: 16,546 non-directory entries. Historical canonical StreamingAssets was documented as 16,551 real files with SHA256 `8253956d...`. Treat them as potentially different captures until a formal mobile-source version matrix is completed.
