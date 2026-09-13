#pragma once
#include "../FootballCore/FixedPoint.h"

namespace football::physics::recovered {
// Mobile raw component order x/y/z. Axis/unit conversion is a separate boundary.
struct RawVector3 {
    std::int32_t x{}, y{}, z{};
};

inline RawVector3 Scale(RawVector3 vector, std::int32_t factor) noexcept {
    using namespace football::core;
    return {Multiply(Create(vector.x), Create(factor)).raw,
            Multiply(Create(vector.y), Create(factor)).raw,
            Multiply(Create(vector.z), Create(factor)).raw};
}

// These are the arithmetic kernels AFTER native branch/property selection.
// Callers supply the native normalization/magnitude results. This API does not
// substitute floating-point normalization or claim GetVHor/GetVVer are final.
inline RawVector3 ApplyVHorMagnitudeIncrease(RawVector3 normalized_direction,
                                           std::int32_t magnitude_raw,
                                           std::int32_t parameter_raw) noexcept {
    using namespace football::core;
    return Scale(normalized_direction, Add(Create(magnitude_raw), Create(parameter_raw)).raw);
}

inline RawVector3 ApplyVVerScale(RawVector3 velocity, std::int32_t parameter_raw) noexcept {
    return Scale(velocity, parameter_raw);
}

inline RawVector3 ApplyHeadMagnitudeDecrease(RawVector3 normalized_direction,
                                            std::int32_t magnitude_raw,
                                            std::int32_t parameter_raw) noexcept {
    using namespace football::core;
    // 0x16EA4D8 subtracts the parameter. No clamp is present in this kernel;
    // a negative new magnitude reverses the supplied direction.
    return Scale(normalized_direction, Subtract(Create(magnitude_raw), Create(parameter_raw)).raw);
}
}
