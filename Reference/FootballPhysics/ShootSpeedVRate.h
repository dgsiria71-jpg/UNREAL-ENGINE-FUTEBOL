#pragma once

#include "../FootballCore/FixedPoint.h"

#include <cstdint>
#include <stdexcept>

namespace football::physics::recovered {

inline football::core::XNumber DivideRawByInt(
    football::core::XNumber lhs,
    std::int32_t rhs) noexcept {
    using namespace football::core;
    // Canonical XNumber.op_Division(XNumber,int) at 0x01B6B37C.
    // The original returns XNumber.zero when either operand is zero.
    if (lhs.raw == 0 || rhs == 0) return Create(0);
    const std::int64_t lhs_wide = lhs.raw;
    const std::int64_t rhs_wide = rhs;
    const std::int64_t quotient = lhs_wide / rhs_wide;
    const std::int64_t remainder = lhs_wide - quotient * rhs_wide;
    return Create(WrapInt32(quotient + (2 * remainder) / rhs_wide));
}

inline football::core::XNumber XRandomRangeAtSample(
    football::core::XNumber from,
    football::core::XNumber to,
    std::int32_t sample) {
    using namespace football::core;
    if (sample < 0 || sample > 1000) {
        throw std::out_of_range("XRandom.Range sample must be in [0,1000]");
    }
    // XRandom.Range at 0x0192A0C4 uses NextInt(1001), a wrapped 32-bit
    // product, division by integer 1000, then adds the first endpoint.
    const XNumber delta = Subtract(to, from);
    const XNumber scaled = Create(WrapInt32(
        static_cast<std::int64_t>(sample) * delta.raw));
    return Add(from, DivideRawByInt(scaled, 1000));
}

inline football::core::XNumber GetShootSpeedVRateAtSample(
    football::core::XNumber shoot_ver_rate,
    football::core::XNumber F,
    football::core::XNumber c,
    std::int32_t dis_area_raw,
    std::int32_t sample) {
    using namespace football::core;

    const XNumber force_ratio = DivideRawByInt(F, 100);
    const XNumber force_scaled = Multiply(
        Multiply(Multiply(shoot_ver_rate, c), force_ratio),
        force_ratio);
    const XNumber base = Add(Create(kOne), force_scaled);

    const XNumber delta = Create(dis_area_raw);
    const XNumber candidate = c.raw >= 0 ? Add(base, delta) : Subtract(base, delta);
    const XNumber sign_selected_bound = c.raw >= 0
        ? (candidate.raw < kOne ? candidate : Create(kOne))
        : (candidate.raw > kOne ? candidate : Create(kOne));

    return XRandomRangeAtSample(sign_selected_bound, c, sample);
}

}  // namespace football::physics::recovered
