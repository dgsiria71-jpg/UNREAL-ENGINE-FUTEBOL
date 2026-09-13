#pragma once
#include <cstdint>
#include <stdexcept>
#include <limits>
#include <cmath>

namespace football::core {
constexpr std::int32_t kOne = 1024;
constexpr int kFractionBits = 10;

inline std::int32_t WrapInt32(std::int64_t value) noexcept {
    const auto u = static_cast<std::uint32_t>(static_cast<std::uint64_t>(value));
    return u <= 0x7FFFFFFFU ? static_cast<std::int32_t>(u)
        : static_cast<std::int32_t>(static_cast<std::int64_t>(u) - 0x100000000LL);
}
struct XNumber {
    std::int32_t raw{0};
    static constexpr XNumber FromRaw(std::int32_t value) noexcept { return {value}; }
    static XNumber FromFloat(double value) noexcept {
        return {WrapInt32(static_cast<std::int64_t>(value * kOne))};
    }
    constexpr double ToFloat() const noexcept { return static_cast<double>(raw) / kOne; }
};
inline XNumber Create(std::int32_t raw) noexcept { return XNumber::FromRaw(raw); }
inline XNumber Add(XNumber a, XNumber b) noexcept { return {WrapInt32(static_cast<std::int64_t>(a.raw) + b.raw)}; }
inline XNumber Subtract(XNumber a, XNumber b) noexcept { return {WrapInt32(static_cast<std::int64_t>(a.raw) - b.raw)}; }
inline XNumber Multiply(XNumber a, XNumber b) noexcept {
    // ARM64 XNumber.op_Multiply at 0x1B6B2B0 extracts bits [10, 41]
    // after adding 512. Unsigned extraction avoids signed-shift differences.
    // Negative half ties round toward positive infinity.
    const auto biased = static_cast<std::int64_t>(a.raw) * b.raw + kOne / 2;
    const auto bits = static_cast<std::uint64_t>(biased) >> kFractionBits;
    return {WrapInt32(static_cast<std::int64_t>(bits))};
}
inline XNumber Divide(XNumber a, XNumber b) {
    if (b.raw == 0) throw std::domain_error("XNumber divide by zero");
    // Nonzero path at 0x1B6B31C: q + trunc(2*r / denominator).
    // The exception above is a host guard, not recovered zero-divisor behavior.
    const auto numerator = static_cast<std::int64_t>(a.raw) * kOne;
    const auto quotient = numerator / b.raw;
    const auto remainder = numerator % b.raw;
    return {WrapInt32(quotient + (2 * remainder) / b.raw)};
}
inline XNumber Lerp(XNumber a, XNumber b, XNumber t) noexcept {
    return Add(a, Multiply(Subtract(b, a), t));
}
inline XNumber InverseLerp(XNumber a, XNumber b, XNumber value) {
    return Divide(Subtract(value, a), Subtract(b, a));
}
inline XNumber Clamp(XNumber value, XNumber lo, XNumber hi) noexcept {
    if (value.raw < lo.raw) return lo;
    if (value.raw > hi.raw) return hi;
    return value;
}
inline XNumber RemapClamped(XNumber in, XNumber inMin, XNumber inMax,
                            XNumber outMin, XNumber outMax) {
    // Native helper 0x126BF1C has an explicit equal-input-range return and
    // clamps the source value before constructing the fixed-point ratio.
    // Keep the comparison order byte-for-byte equivalent to the ARM64 dataflow
    // rather than relying on a generic clamp for potentially reversed bounds.
    if (inMin.raw == inMax.raw) return outMin;
    const XNumber bounded = in.raw < inMin.raw ? inMin
        : (in.raw > inMax.raw ? inMax : in);
    const XNumber numerator = Subtract(bounded, inMin);
    const XNumber denominator = Subtract(inMax, inMin);
    const XNumber ratio = numerator.raw == 0 ? Create(0) : Divide(numerator, denominator);
    return Lerp(outMin, outMax, Clamp(ratio, Create(0), Create(kOne)));
}
struct XVector2 {
    XNumber x{};
    XNumber y{};
};
inline XVector2 Normalize(XVector2 value) {
    const double x=value.x.ToFloat(), y=value.y.ToFloat();
    const double len=(x*x+y*y);
    if (len <= std::numeric_limits<double>::epsilon()) return {};
    const double inv=1.0/std::sqrt(len);
    return {XNumber::FromFloat(x*inv), XNumber::FromFloat(y*inv)};
}
}
