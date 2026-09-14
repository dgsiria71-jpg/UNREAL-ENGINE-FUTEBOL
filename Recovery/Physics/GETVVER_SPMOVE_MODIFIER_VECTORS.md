# GetVVer representative spmove modifier vectors

Status: **source-bound executable reference; native differential still pending**.

The recovered 0x3FC and 0x41A modifier chain now crosses the runtime selector boundary instead of receiving preselected booleans and ratios directly. GetVVerSpmoveRuntime.h converts the recovered XNumber vector to the validated selector representation, applies the native flag, magnitude, inventory, maximum-child and parameter-list guards, then returns the modified XNumber vector.

The committed representative fixture uses explicit post-eligibility inventories:

- 0x3FC: candidates 102001, 102003; selected child 102003; level 3; param[2] = 700.
- 0x41A: candidates 105001, 105002; selected child 105002; level 2; param[2] = 800.

For base raw vector [-3000, 1537, 777], the executable outputs are:

| Active modifiers | Output raw |
|---|---|
| none | [-3000, 1537, 777] |
| 0x3FC | [-2051, 1051, 531] |
| 0x41A | [-2344, 1201, 607] |
| 0x3FC then 0x41A | [-1602, 821, 415] |

The -3000 component proves the order-sensitive fixed-point boundary. Applying both native multiplications and committing rounding between them produces -1602; precombining the ratios produces -1603 and is therefore invalid.

These are deterministic host reference vectors derived from recovered data and verified by C++. They are not captured outputs from the canonical ARM64 method and do not establish whole-GetVVer equivalence. The next gate is to execute or capture matching native cases and compare the complete outputs. Physics Recovery v0.3 remains **BLOCKED**.
