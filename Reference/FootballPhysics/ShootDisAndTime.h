#pragma once

#include "../FootballCore/FixedPoint.h"
#include "ShootRemap.h"
#include "ShootSpeedVRate.h"

#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace football::physics::recovered {

using ShootDisAndTimeTable = std::vector<std::vector<std::int32_t>>;

inline std::int32_t FloorNonnegativeRaw(football::core::XNumber value) {
    if (value.raw < 0) {
        throw std::invalid_argument("shootDisAndTime axes must be nonnegative");
    }
    return value.raw / football::core::kOne;
}

inline std::int32_t CeilingNonnegativeRaw(football::core::XNumber value) {
    if (value.raw < 0) {
        throw std::invalid_argument("shootDisAndTime axes must be nonnegative");
    }
    const std::int32_t biased = football::core::WrapInt32(
        static_cast<std::int64_t>(value.raw) + football::core::kOne - 1);
    return biased / football::core::kOne;
}

inline football::core::XNumber MillisecondsToSeconds(std::int32_t milliseconds) {
    using namespace football::core;
    const XNumber authored_ms = Create(WrapInt32(
        static_cast<std::int64_t>(milliseconds) * kOne));
    return Divide(authored_ms, Create(1000 * kOne));
}

inline football::core::XNumber SampleShootTimeRow(
    const std::vector<std::int32_t>& row,
    football::core::XNumber horizontal_distance) {
    using namespace football::core;
    if (horizontal_distance.raw < 0) {
        throw std::invalid_argument("shoot distance must be nonnegative");
    }

    // The native loop only accepts an interval [i, i+1]. A row with fewer
    // than two values, or a distance beyond its final interval, yields zero.
    for (std::size_t i = 0; i + 1 < row.size(); ++i) {
        const XNumber lower_axis = Create(WrapInt32(
            static_cast<std::int64_t>(i) * kOne));
        const XNumber upper_axis = Create(WrapInt32(
            static_cast<std::int64_t>(i + 1) * kOne));
        if (lower_axis.raw <= horizontal_distance.raw &&
            upper_axis.raw >= horizontal_distance.raw) {
            return ShootRemapClamped(
                horizontal_distance,
                lower_axis,
                upper_axis,
                MillisecondsToSeconds(row[i]),
                MillisecondsToSeconds(row[i + 1]));
        }
    }
    return Create(0);
}

inline football::core::XNumber LookupShootFlightTime(
    const ShootDisAndTimeTable& table,
    football::core::XNumber vhor_magnitude,
    football::core::XNumber horizontal_distance) {
    using namespace football::core;
    if (table.empty()) {
        throw std::invalid_argument("shootDisAndTime table must not be empty");
    }

    const std::int32_t max_row = static_cast<std::int32_t>(table.size() - 1);
    const std::int32_t lower_row = std::min(
        FloorNonnegativeRaw(vhor_magnitude), max_row);
    const std::int32_t upper_row = std::min(
        CeilingNonnegativeRaw(vhor_magnitude), max_row);

    const XNumber lower_time = SampleShootTimeRow(
        table[static_cast<std::size_t>(lower_row)], horizontal_distance);
    const XNumber upper_time = SampleShootTimeRow(
        table[static_cast<std::size_t>(upper_row)], horizontal_distance);

    // Native zero fallback at 0x016E99F4..0x016E9A9C.
    if (lower_time.raw == 0 || upper_time.raw == 0) {
        return lower_time.raw != 0 ? lower_time : upper_time;
    }

    return ShootRemapClamped(
        vhor_magnitude,
        Create(WrapInt32(static_cast<std::int64_t>(lower_row) * kOne)),
        Create(WrapInt32(static_cast<std::int64_t>(upper_row) * kOne)),
        lower_time,
        upper_time);
}

inline football::core::XNumber SolveVerticalSpeed(
    football::core::XNumber flight_time,
    football::core::XNumber vertical_delta,
    football::core::XNumber vertical_accel_raw) {
    using namespace football::core;
    if (flight_time.raw == 0) return Create(0);

    const XNumber accel_time = Multiply(flight_time, vertical_accel_raw);
    const XNumber accel_time_squared = Multiply(accel_time, flight_time);
    const XNumber half_accel_time_squared = DivideRawByInt(accel_time_squared, 2);
    return Divide(
        Subtract(vertical_delta, half_accel_time_squared),
        flight_time);
}

inline football::core::XNumber ClampVerticalSpeedNativeOrder(
    football::core::XNumber solved_y_speed,
    football::core::XNumber y_speed_min,
    football::core::XNumber y_speed_max) noexcept {
    const football::core::XNumber upper_selected =
        solved_y_speed.raw > y_speed_max.raw ? y_speed_max : solved_y_speed;
    return solved_y_speed.raw < y_speed_min.raw ? y_speed_min : upper_selected;
}

inline football::core::XNumber RecoverNewVVerY(
    const ShootDisAndTimeTable& table,
    football::core::XNumber vhor_magnitude,
    football::core::XNumber horizontal_distance,
    football::core::XNumber vertical_delta,
    football::core::XNumber vertical_accel_raw,
    football::core::XNumber y_speed_min,
    football::core::XNumber y_speed_max) {
    const football::core::XNumber flight_time = LookupShootFlightTime(
        table, vhor_magnitude, horizontal_distance);
    return ClampVerticalSpeedNativeOrder(
        SolveVerticalSpeed(flight_time, vertical_delta, vertical_accel_raw),
        y_speed_min,
        y_speed_max);
}

}  // namespace football::physics::recovered
