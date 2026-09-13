# Unreal automation entry points

- validate_content.py performs read-only provenance and gate checks.
- import_normalized_data.py emits a deterministic import plan; it does not
  create assets from unresolved physics.
- Run these scripts with Unreal's embedded Python after the project is
  associated with an installed Unreal Engine 5.x version.

The scripts intentionally keep the mobile Unity/IL2CPP parser boundary
offline. Gameplay runtime consumes normalized records and never opens
AssetBundles or IL2CPP metadata.

The current plan also exposes Recovery/Normalized/spmove_normalized.json and
the native static trace. Import code may consume the record schema for offline
asset preparation, but the server-side contact adapter must continue to reject
records while velocity semantics are unresolved.

`Recovery/Normalized/playable_match_contract.json` is the authored new-game
contract for the first playable headless fixture. It describes the fixed 120 Hz
simulation, 3v3/5v5/11v11 roster sizes, actions and Unreal class mapping. It is
safe to import as design/tuning data; it does not unlock unresolved mobile
velocity records.
