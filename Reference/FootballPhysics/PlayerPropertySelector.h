#pragma once

#include "../FootballCore/FixedPoint.h"

#include <cstdint>
#include <utility>

namespace football::physics::recovered {

struct PlayerPropertyInputs {
    std::int32_t action_id{0};
    football::core::XNumber distance{};
    football::core::XNumber upper_threshold{};
    football::core::XNumber lower_threshold{};
    football::core::XNumber position_y{};
    football::core::XNumber position_threshold{};
    bool in_collection{false};
    bool collection_bonus_enabled{false};
    football::core::XNumber collection_bonus{};
};

inline football::core::XNumber ComputePlayerPropertyBlendRatio(
    football::core::XNumber distance,
    football::core::XNumber upper_threshold,
    football::core::XNumber lower_threshold) noexcept {
    const std::int32_t numerator = football::core::WrapInt32(
        static_cast<std::int64_t>(upper_threshold.raw) - distance.raw);
    const std::int32_t denominator = football::core::WrapInt32(
        static_cast<std::int64_t>(upper_threshold.raw) - lower_threshold.raw);

    if (numerator == 0 || denominator == 0) {
        return football::core::Create(0);
    }

    const std::int64_t scaled = static_cast<std::int64_t>(numerator) * football::core::kOne;
    const std::int64_t quotient = scaled / denominator;
    const std::int64_t remainder = scaled - quotient * denominator;
    const std::int64_t rounded = quotient + (2 * remainder) / denominator;
    return football::core::Create(football::core::WrapInt32(rounded));
}

inline std::int32_t SelectPositionPropertyId(
    football::core::XNumber position_y,
    football::core::XNumber position_threshold) noexcept {
    return position_threshold.raw >= position_y.raw ? 0x0F : 0x11;
}

template <typename Resolver>
football::core::XNumber ResolvePlayerProperty(
    const PlayerPropertyInputs& input,
    Resolver&& resolve_with_action) {
    if (input.action_id == 0x16B3) {
        return std::forward<Resolver>(resolve_with_action)(0x15, input.action_id);
    }
    if (input.action_id == 0x22C5) {
        return std::forward<Resolver>(resolve_with_action)(0x16, input.action_id);
    }

    if (input.in_collection) {
        const auto base = std::forward<Resolver>(resolve_with_action)(0x14, input.action_id);
        return input.collection_bonus_enabled
            ? football::core::Add(base, input.collection_bonus)
            : base;
    }

    if (input.distance.raw > input.upper_threshold.raw) {
        return std::forward<Resolver>(resolve_with_action)(0x10, input.action_id);
    }

    const std::int32_t near_property = SelectPositionPropertyId(
        input.position_y,
        input.position_threshold);

    if (input.distance.raw < input.lower_threshold.raw) {
        return std::forward<Resolver>(resolve_with_action)(near_property, input.action_id);
    }

    const auto ratio = ComputePlayerPropertyBlendRatio(
        input.distance,
        input.upper_threshold,
        input.lower_threshold);
    const auto near_value = std::forward<Resolver>(resolve_with_action)(near_property, input.action_id);
    const auto far_value = std::forward<Resolver>(resolve_with_action)(0x10, input.action_id);
    const auto complement = football::core::Create(
        football::core::WrapInt32(
            static_cast<std::int64_t>(football::core::kOne) - ratio.raw));

    return football::core::Add(
        football::core::Multiply(near_value, ratio),
        football::core::Multiply(far_value, complement));
}

}  // namespace football::physics::recovered
