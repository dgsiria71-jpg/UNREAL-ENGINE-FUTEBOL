# Property lookup semantics behind GetVVer

The evidence uploaded as `20260914-010116-072c3bfd` establishes exact ScriptMethod boundaries and identities for the two helpers that remained address-labelled after PR #14:

- `0x01967D38..0x01967DC4`: `PlayerProperty.GetPropertyValue(PropertyType, SpmoveLogicId)`;
- `0x01B718D8..0x01B71958`: `XProperty.XPropertyManager.GetPropertyValue(PropertyType)`.

`PlayerProperty.GetPropertyValue` queries the spmove manager at `PlayerProperty +0x28`. It uses the buffer manager at `+0x20` only when an enabled spmove config exists and the logic check passes; the buffer property identifier is loaded from the selected config at `+0x40`. Otherwise it reads the base property through the property manager at `+0x10`.

The property manager stores its entry array at `+0x10`. Native code checks the array length at `+0x18`, resolves an eight-byte element pointer from the data region at `+0x20`, and returns the raw `XNumber` at element offset `+0x14`. Null and out-of-range cases follow managed exception paths. The reference implementation therefore does not invent a default value for invalid storage.

`PlayerProperty.getShootPropertyWithSpmove` first requests the spmove-aware value. If that raw value is zero or negative, it falls back to the base property manager value.

The same evidence corrects two earlier class-label assumptions. The thresholds read by `GetShootProperty` are `ShootConfig.shootAirBallHeighLimit` (`+0x24`), `ShootConfig.dis_shootlong` (`+0x148`) and `ShootConfig.dis_shoot` (`+0x14C`). The collection bonus comes from `Football.lastKickParam` (`+0x98`), whose `BallKickParam` fields are `biographyPointType` (`+0x40`) and `BiographyPassProperty` (`+0x44`).

Executable artifacts:

- `Reference/FootballPhysics/PropertyLookup.h`;
- `Recovery/Normalized/property_lookup_semantics_static_trace.json`;
- `Tools/analyze_property_lookup_semantics.py`.

This closes the identities and caller-visible branch contract of the two helpers. Whole-function `GetVVer` equivalence remains unclaimed. Physics v0.3 remains blocked on runtime `0x3FC/0x41A` modifier inputs, whole-function native differential validation, final `GetKickVelocity`, and `BALL_CONTACT.velocity`.
