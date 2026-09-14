#pragma once

#include "../FootballCore/FixedPoint.h"
#include "GetVVerNewPath.h"
#include "PlayerPropertySelector.h"
#include "ShootRemap.h"

#include <cstddef>
#include <stdexcept>
#include <utility>
#include <vector>

namespace football::physics::recovered {

// Exact metadata names from canonical build 1-221-5 ShootSpeedConfigItem.
// This bounded view contains only the raw maps consumed by the new GetVVer
// producer chain recovered at 0x016E8630..0x016E8FA8.
struct ShootSpeedNewMethodMaps {
    std::vector<football::core::XNumber> shootDisMap;            // +0xE8
    std::vector<football::core::XNumber> outEnergyMaxMap;        // +0x100
    std::vector<football::core::XNumber> energyMapNew;           // +0xB8
    std::vector<football::core::XNumber> ySpeedMax;              // +0xA0
    std::vector<football::core::XNumber> shootPointHUpMap;       // +0xF8
    std::vector<football::core::XNumber> shootPointHDownMap;     // +0xF0
    std::vector<football::core::XNumber> shootPropertyMapNew;    // +0xD8
    std::vector<football::core::XNumber> energyToleranceMap;     // +0xE0
};

struct ResolvedNewGetVVerMapOutputs {
    football::core::XNumber out_energy{};
    football::core::XNumber y_speed_max{};
    football::core::XNumber point_up_rate{};
    football::core::XNumber point_down_rate{};
    football::core::XNumber energy_tolerance{};
};

struct ShootSpeedNewMethodConfig {
    ShootSpeedNewMethodMaps maps{};
    football::core::XNumber energyNeedProtect{};                 // +0x94
    football::core::XNumber ySpeedMin{};                         // +0x98
    football::core::XNumber shootPointHMin{};                    // +0xB0 low32
    football::core::XNumber shootPointHMax{};                    // +0xB0 high32 / +0xB4
    ShootDisAndTimeTable shootDisAndTime{};                      // +0x108
};

inline football::core::XNumber RemapPairedShootMapCanonical(
    football::core::XNumber input,
    const std::vector<football::core::XNumber>& axis,
    const std::vector<football::core::XNumber>& values) {
    // These are host-side guards for the canonical recovered data contract.
    // They are deliberately NOT claims about malformed/null native exception
    // behavior, which remains outside the recovered semantic boundary.
    if (axis.size() != values.size() || axis.size() < 2) {
        throw std::invalid_argument("paired shoot maps must have equal size >= 2");
    }
    for (std::size_t i = 1; i < axis.size(); ++i) {
        if (axis[i - 1].raw > axis[i].raw) {
            throw std::invalid_argument("canonical paired shoot-map axis must be ascending");
        }
    }

    for (std::size_t i = 0; i + 1 < axis.size(); ++i) {
        if (axis[i].raw <= input.raw && input.raw <= axis[i + 1].raw) {
            return ShootRemapClamped(input, axis[i], axis[i + 1], values[i], values[i + 1]);
        }
    }
    throw std::out_of_range("input is outside canonical paired shoot-map coverage");
}

inline ResolvedNewGetVVerMapOutputs ResolveNewGetVVerMapOutputs(
    const ShootSpeedNewMethodMaps& config,
    football::core::XNumber horizontal_distance,
    football::core::XNumber current_energy,
    football::core::XNumber shoot_property_input) {
    return {
        RemapPairedShootMapCanonical(horizontal_distance, config.shootDisMap, config.outEnergyMaxMap),
        RemapPairedShootMapCanonical(current_energy, config.energyMapNew, config.ySpeedMax),
        RemapPairedShootMapCanonical(horizontal_distance, config.shootDisMap, config.shootPointHUpMap),
        RemapPairedShootMapCanonical(horizontal_distance, config.shootDisMap, config.shootPointHDownMap),
        RemapPairedShootMapCanonical(shoot_property_input, config.shootPropertyMapNew, config.energyToleranceMap),
    };
}

inline RecoveredXVector3 ComposeNewGetVVerFromRawMaps(
    const ShootSpeedNewMethodConfig& config,
    football::core::XNumber vhor_magnitude,
    football::core::XNumber horizontal_distance,
    football::core::XNumber current_energy,
    football::core::XNumber shoot_property_input,
    football::core::XNumber goal_door_height,
    football::core::XNumber reference_y,
    football::core::XNumber vertical_accel_raw,
    RecoveredXVector3 vertical_direction,
    bool apply_spmove_3fc,
    football::core::XNumber spmove_3fc_ratio,
    bool apply_spmove_41a,
    football::core::XNumber spmove_41a_ratio) {
    const ResolvedNewGetVVerMapOutputs resolved = ResolveNewGetVVerMapOutputs(
        config.maps,
        horizontal_distance,
        current_energy,
        shoot_property_input);

    return ComposeNewGetVVerFromResolvedScalars(
        config.shootDisAndTime,
        vhor_magnitude,
        horizontal_distance,
        resolved.out_energy,
        current_energy,
        resolved.energy_tolerance,
        config.energyNeedProtect,
        resolved.point_up_rate,
        resolved.point_down_rate,
        goal_door_height,
        config.shootPointHMin,
        config.shootPointHMax,
        reference_y,
        vertical_accel_raw,
        config.ySpeedMin,
        resolved.y_speed_max,
        vertical_direction,
        apply_spmove_3fc,
        spmove_3fc_ratio,
        apply_spmove_41a,
        spmove_41a_ratio);
}

template <typename Resolver>
inline RecoveredXVector3 ComposeNewGetVVerFromPlayerProperty(
    const ShootSpeedNewMethodConfig& config,
    football::core::XNumber vhor_magnitude,
    football::core::XNumber horizontal_distance,
    football::core::XNumber current_energy,
    const PlayerPropertyInputs& property_inputs,
    Resolver&& property_resolver,
    football::core::XNumber goal_door_height,
    football::core::XNumber reference_y,
    football::core::XNumber vertical_accel_raw,
    RecoveredXVector3 vertical_direction,
    bool apply_spmove_3fc,
    football::core::XNumber spmove_3fc_ratio,
    bool apply_spmove_41a,
    football::core::XNumber spmove_41a_ratio) {
    const football::core::XNumber property_input = ResolvePlayerProperty(
        property_inputs,
        std::forward<Resolver>(property_resolver));

    return ComposeNewGetVVerFromRawMaps(
        config,
        vhor_magnitude,
        horizontal_distance,
        current_energy,
        property_input,
        goal_door_height,
        reference_y,
        vertical_accel_raw,
        vertical_direction,
        apply_spmove_3fc,
        spmove_3fc_ratio,
        apply_spmove_41a,
        spmove_41a_ratio);
}

}  // namespace football::physics::recovered
