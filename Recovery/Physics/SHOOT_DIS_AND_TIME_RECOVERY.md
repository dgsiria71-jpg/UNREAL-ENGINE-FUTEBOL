# shootDisAndTime and new-GetVVer vertical kernel recovery

Status: source-bound normal-path equation recovered. Physics v0.3 remains BLOCKED.

## Evidence boundary

The behavioral source is the canonical build 1-221-5 ARM64 listing:

- GetVVer: 0x016E84A4..0x016EA55C
- nested lookup slice: 0x016E9268..0x016E9B20
- vertical solve and clamp: 0x016E9B40..0x016E9CF4
- normalized-LF disassembly SHA-256: c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4
- originating libil2cpp.so SHA-256: 2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496

The committed metadata excerpt binds:

- ShootSpeedConfigItem.shootDisAndTime as List<List<int>> at +0x108;
- ShootSpeedConfigItem.ySpeedMin at +0x98;
- XNumber.thousand at static offset +0x50.

The source table is normalized from FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip, whose
SHA-256 remains 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac.
The decoded shootspeed payload is 133872 bytes, consumes all 133872 bytes across
28 records, and has SHA-256
f437f83465a541bc85f07e1cab655afd59a2fb927233302a40a1d09b6355d0ad.

## Recovered lookup

Let:

- speed = magnitude(vHor);
- distance = horizontal distance from shootPoint to ballPos;
- table = shootDisAndTime;
- loSpeed = clamp(floor(speed), 0, table.size-1);
- hiSpeed = clamp(ceiling(speed), 0, table.size-1).

For each selected speed row, the native loop finds the first integer interval
i <= distance <= i+1. Rows with fewer than two entries, or distances beyond the
final interval, produce zero for that row.

Each serialized integer is milliseconds. It enters the fixed-point domain as:

timeSeconds = XNumber(tableMilliseconds) / XNumber.thousand

The per-row result is:

rowTime = ShootRemapClamped(
    distance,
    XNumber(i),
    XNumber(i+1),
    seconds(row[i]),
    seconds(row[i+1]))

When both row times are nonzero:

flightTime = ShootRemapClamped(
    speed,
    XNumber(loSpeed),
    XNumber(hiSpeed),
    lowerRowTime,
    upperRowTime)

When either row time is zero, the runtime uses the nonzero result. It returns
zero only when both results are zero.

The config 5800/identify 0 normalized source proves:

- table[20][25] = 1327 milliseconds;
- 1327 milliseconds converts to fixed-point raw 1359.

## Recovered vertical solve

When flightTime is zero, the base vertical speed is XNumber.zero.

Otherwise the native operation order is preserved:

1. accelTime = fixed_mul(flightTime, vertical_accel_raw)
2. accelTimeSquared = fixed_mul(accelTime, flightTime)
3. halfAccelTimeSquared = accelTimeSquared / integer 2
4. numerator = verticalDelta - halfAccelTimeSquared
5. solvedY = numerator / flightTime
6. finalY = max(ySpeedMin, min(ySpeedMax, solvedY)), with the original comparison order

The name vertical_accel_raw is intentionally preserved for AIParameterConfig
+0x1C0. This slice does not claim that the original semantic name is gravity.

The historical config-5800 vector is executable again:

- flightTime raw 1359
- verticalDelta raw 1551
- vertical_accel_raw -10035
- ySpeedMax raw 9216
- solved/final vY raw 7828

## Executable material

- Tools/analyze_shoot_dis_and_time.py verifies exact ARM64 anchors and emits the static trace.
- Tools/extract_shoot_dis_and_time_metadata.py reproduces the metadata excerpt from hash-bound local sources.
- Tools/normalize_shoot_dis_and_time.py parses the canonical Physics v0.2 archive and emits config 5800 as normalized JSON.
- Reference/FootballPhysics/ShootDisAndTime.h contains the fixed-point lookup, zero fallback, solver and clamp.
- Tests/shoot_dis_and_time_semantics_test.cpp covers conversion, interpolation, zero fallback and the historical vector.

## Remaining gate

This closes the flight-time and ballistic vertical kernel. It does not yet close:

- the entire executable upstream target-height and energy-protection path;
- the surviving new-path spmove modifiers 0x3FC and 0x41A;
- the final GetVVer vector as a whole;
- complete GetKickVelocity behavior;
- BALL_CONTACT.velocity;
- the regression and packaging gate for Physics v0.3.
