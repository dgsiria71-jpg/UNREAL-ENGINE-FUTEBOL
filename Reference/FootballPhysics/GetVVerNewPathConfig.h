#pragma once

#include "../FootballCore/FixedPoint.h"
#include "ShootRemap.h"

#include <cstddef>
#include <stdexcept>
#include <vector>

namespace football::physics::recovered {

// Exact metadata names from canonical build 1-221-5 ShootSpeedConfigItem.
// This bounded view contains only the raw maps consumed by the new GetVVer
// producer chain recovered at 0x016E8630..0x016E8FA8.
struct ShootSpeedNewMethodMaps {
    std::vector<football::core::XNumber> shootDisMap;            // +0xE8
    std::vector<football::core::XNumber> outEnergyMaxMap;        // +0x100
    std::vector<football::core::XNumber> energyMapNew;           // +0xB8
    std::vector<football::core::XNumber> ySpeedMax;               // +0xA0
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

}  // namespace football::physics::recovered
