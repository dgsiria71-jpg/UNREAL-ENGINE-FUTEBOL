#pragma once

#include "../FootballCore/FixedPoint.h"

namespace football::physics::recovered {

inline football::core::XNumber ShootRemapClamped(
    football::core::XNumber input,
    football::core::XNumber in_min,
    football::core::XNumber in_max,
    football::core::XNumber out_min,
    football::core::XNumber out_max) {
    using namespace football::core;

    // Canonical 1-221-5 ARM64 helper 0x126BF1C normal-return semantics.
    // Equal input bounds bypass division and return out_min directly.
    if (in_min.raw == in_max.raw) return out_min;

    // Preserve the native comparison order rather than assuming generic clamp
    // behavior when input bounds are reversed.
    const XNumber bounded = input.raw < in_min.raw
        ? in_min
        : (input.raw > in_max.raw ? in_max : input);

    const XNumber numerator = Subtract(bounded, in_min);
    const XNumber denominator = Subtract(in_max, in_min);

    // Native 0x126BFD4/0x126BFF4 selects raw zero for a zero numerator.
    const XNumber ratio = numerator.raw == 0
        ? Create(0)
        : Divide(numerator, denominator);

    // Callee 0x126C3FC clamps t to [0, 1024] then computes
    // out_min + ((out_max - out_min) * t + 512) >> 10.
    return Lerp(out_min, out_max, Clamp(ratio, Create(0), Create(kOne)));
}

}  // namespace football::physics::recovered
