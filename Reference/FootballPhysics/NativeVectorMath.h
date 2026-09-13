#pragma once
#include "SpmoveModifiers.h"
#include "NativeSqrtTable.h"

namespace football::physics::recovered {
inline std::int64_t Signed64(std::uint64_t bits) noexcept {
    return bits <= 0x7FFFFFFFFFFFFFFFULL ? static_cast<std::int64_t>(bits)
        : -1 - static_cast<std::int64_t>(~bits);
}
inline std::int64_t ArmDivide(std::int64_t a, std::int64_t b) noexcept {
    // ARM SDIV returns zero for zero divisor; handle signed overflow explicitly.
    if (b == 0) return 0;
    if (a == (-9223372036854775807LL - 1) && b == -1) return a;
    return a / b;
}
inline std::int64_t FloorHalf(std::int64_t value) noexcept {
    return value / 2 - (value < 0 && value % 2 != 0 ? 1 : 0);
}

// Source algorithm, including its approximate/rounded lookup behavior.
// Do not replace this with std::sqrt or integer floor sqrt.
inline std::int32_t SqrtLong(std::int64_t value) noexcept {
    using football::core::WrapInt32;
    if (value < 1) return 0;
    if (value < 256) return kNativeSqrtTable[static_cast<std::size_t>(value)] >> 4;
    if (value < 65536) {
        unsigned shift = 2;
        while ((static_cast<std::uint64_t>(value) >> shift) >= 256) shift += 2;
        const auto seed = kNativeSqrtTable[static_cast<std::size_t>(value >> shift)] >> (4 - shift / 2);
        return seed + 1;
    }
    unsigned shift = 10;
    while ((static_cast<std::uint64_t>(value) >> shift) >= 256) shift += 2;
    const auto table = static_cast<std::uint32_t>(kNativeSqrtTable[static_cast<std::size_t>(value >> shift)]);
    const auto seed = static_cast<std::int64_t>(WrapInt32(static_cast<std::uint64_t>(table) << ((shift-8)/2)));
    const auto first = (seed | 1LL) + ArmDivide(value, seed);
    const auto half = FloorHalf(first);
    const auto next = ArmDivide(value, half) + half + 1;
    const auto result = FloorHalf(next);
    return WrapInt32(next < 0 ? -result : result);
}
inline std::int64_t SquaredMagnitude(RawVector3 v) noexcept {
    const auto square = [](std::int32_t x) {
        return static_cast<std::uint64_t>(static_cast<std::int64_t>(x) * x);
    };
    return Signed64(square(v.x) + square(v.y) + square(v.z));
}
inline std::int32_t Magnitude(RawVector3 v) noexcept { return SqrtLong(SquaredMagnitude(v)); }

// XVector3.get_normalized at 0x1936B4C. Preserves the original near-unit band,
// the small-vector precision shift, signed division and component rounding.
inline RawVector3 NormalizeNative(RawVector3 v) noexcept {
    const auto squared = SquaredMagnitude(v);
    if (squared == 0) return {};
    if (squared >= 0xFB065 && squared <= 0x104C7B) return v;
    const bool large = squared > 0x104C7B;
    const unsigned magnitude_shift = large ? 0 : 20;
    const unsigned component_shift = large ? 11 : 21;
    const auto denominator = SqrtLong(Signed64(static_cast<std::uint64_t>(squared) << magnitude_shift));
    const auto normalize = [component_shift, denominator](std::int32_t component) {
        const auto numerator = static_cast<std::int64_t>(component) * (1LL << component_shift);
        return football::core::WrapInt32(FloorHalf(ArmDivide(numerator, denominator) + 1));
    };
    return {normalize(v.x), normalize(v.y), normalize(v.z)};
}

inline RawVector3 ApplyVHorIncrease(RawVector3 v, std::int32_t parameter) noexcept {
    return ApplyVHorMagnitudeIncrease(NormalizeNative(v), Magnitude(v), parameter);
}
inline RawVector3 ApplyHeadDecrease(RawVector3 v, std::int32_t parameter) noexcept {
    return ApplyHeadMagnitudeDecrease(NormalizeNative(v), Magnitude(v), parameter);
}
}
