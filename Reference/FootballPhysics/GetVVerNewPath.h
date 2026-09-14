#pragma once

#include "../FootballCore/FixedPoint.h"
#include "ShootDisAndTime.h"

#include <algorithm>
#include <cstdint>

namespace football::physics::recovered {

struct RecoveredXVector3 {
    football::core::XNumber x{};
    football::core::XNumber y{};
    football::core::XNumber z{};
};

inline football::core::XNumber SelectProtectedEnergy(
    football::core::XNumber out_energy,
    football::core::XNumber current_energy,
    football::core::XNumber energy_tolerance,
    football::core::XNumber energy_need_protect) noexcept {
    using namespace football::core;

    const XNumber protected_floor = Subtract(out_energy, energy_need_protect);
    if (protected_floor.raw >= current_energy.raw) {
        return current_energy;
    }

    const XNumber upper_guard = Add(out_energy, energy_tolerance);
    if (current_energy.raw >= upper_guard.raw) {
        return current_energy;
    }

    const XNumber tolerance_floor = Subtract(current_energy, energy_tolerance);
    return tolerance_floor.raw > protected_floor.raw ? tolerance_floor : protected_floor;
}

inline football::core::XNumber GetVVerDownwardBias() noexcept {
    // Canonical 1-221-5 caller 0x016E9188..0x016E9198 invokes the exact
    // XNumber$$create helper with (0, 100). Its exact ARM64 body returns raw
    // 102 for this observed call. Keep this bounded constant here instead of
    // claiming a complete generic XNumber.create implementation.
    return football::core::Create(102);
}

inline football::core::XNumber ComputePointHeightAdjustment(
    football::core::XNumber selected_energy,
    football::core::XNumber out_energy,
    football::core::XNumber point_up_rate,
    football::core::XNumber point_down_rate) noexcept {
    using namespace football::core;

    const XNumber delta = Subtract(selected_energy, out_energy);
    if (delta.raw > 0) {
        return Multiply(delta, point_up_rate);
    }

    const XNumber magnitude = Create(WrapInt32(-static_cast<std::int64_t>(delta.raw)));
    const XNumber authored_down = Multiply(magnitude, point_down_rate);
    const XNumber native_bias = GetVVerDownwardBias();
    return Create(WrapInt32(
        -static_cast<std::int64_t>(authored_down.raw) - native_bias.raw));
}

inline football::core::XNumber ComputeVerticalDelta(
    football::core::XNumber base_target_height,
    football::core::XNumber height_adjustment,
    football::core::XNumber point_h_min,
    football::core::XNumber point_h_max,
    football::core::XNumber reference_y) noexcept {
    using namespace football::core;

    const XNumber target = Add(base_target_height, height_adjustment);
    const XNumber upper_selected =
        point_h_max.raw < target.raw ? point_h_max : target;
    const XNumber clamped =
        point_h_min.raw > target.raw ? point_h_min : upper_selected;
    return Subtract(clamped, reference_y);
}

inline RecoveredXVector3 BuildVerticalVector(
    RecoveredXVector3 vertical_direction,
    football::core::XNumber solved_y_speed) noexcept {
    using namespace football::core;
    return {
        Multiply(vertical_direction.x, solved_y_speed),
        Multiply(vertical_direction.y, solved_y_speed),
        Multiply(vertical_direction.z, solved_y_speed),
    };
}

inline RecoveredXVector3 ApplyGetVVerModifier(
    RecoveredXVector3 value,
    football::core::XNumber ratio) noexcept {
    using namespace football::core;
    return {
        Multiply(value.x, ratio),
        Multiply(value.y, ratio),
        Multiply(value.z, ratio),
    };
}

inline RecoveredXVector3 ComposeNewGetVVerFromResolvedScalars(
    const ShootDisAndTimeTable& shoot_dis_and_time,
    football::core::XNumber vhor_magnitude,
    football::core::XNumber horizontal_distance,
    football::core::XNumber out_energy,
    football::core::XNumber current_energy,
    football::core::XNumber energy_tolerance,
    football::core::XNumber energy_need_protect,
    football::core::XNumber point_up_rate,
    football::core::XNumber point_down_rate,
    football::core::XNumber base_target_height,
    football::core::XNumber point_h_min,
    football::core::XNumber point_h_max,
    football::core::XNumber reference_y,
    football::core::XNumber vertical_accel_raw,
    football::core::XNumber y_speed_min,
    football::core::XNumber y_speed_max,
    RecoveredXVector3 vertical_direction,
    bool apply_spmove_3fc,
    football::core::XNumber spmove_3fc_ratio,
    bool apply_spmove_41a,
    football::core::XNumber spmove_41a_ratio) {
    const football::core::XNumber selected_energy = SelectProtectedEnergy(
        out_energy, current_energy, energy_tolerance, energy_need_protect);
    const football::core::XNumber height_adjustment = ComputePointHeightAdjustment(
        selected_energy,
        out_energy,
        point_up_rate,
        point_down_rate);
    const football::core::XNumber vertical_delta = ComputeVerticalDelta(
        base_target_height,
        height_adjustment,
        point_h_min,
        point_h_max,
        reference_y);
    const football::core::XNumber solved_y_speed = RecoverNewVVerY(
        shoot_dis_and_time,
        vhor_magnitude,
        horizontal_distance,
        vertical_delta,
        vertical_accel_raw,
        y_speed_min,
        y_speed_max);

    RecoveredXVector3 result = BuildVerticalVector(vertical_direction, solved_y_speed);
    if (apply_spmove_3fc) {
        result = ApplyGetVVerModifier(result, spmove_3fc_ratio);
    }
    if (apply_spmove_41a) {
        result = ApplyGetVVerModifier(result, spmove_41a_ratio);
    }
    return result;
}

}  // namespace football::physics::recovered
