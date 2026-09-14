#pragma once

#include "../FootballCore/FixedPoint.h"

#include <cstdint>
#include <optional>
#include <utility>

namespace football::physics::recovered {

struct PropertyValueEntry {
    football::core::XNumber value{};
};

struct SpmovePropertyContext {
    bool has_enabled_config{false};
    bool logic_check_passes{false};
    std::int32_t buffer_property_id{0};
};

template <typename BufferResolver, typename BaseResolver>
football::core::XNumber ResolvePropertyValueWithSpmove(
    std::int32_t property_type,
    const SpmovePropertyContext& spmove,
    BufferResolver&& resolve_buffer,
    BaseResolver&& resolve_base) {
    if (spmove.has_enabled_config && spmove.logic_check_passes) {
        return std::forward<BufferResolver>(resolve_buffer)(
            property_type, spmove.buffer_property_id);
    }
    return std::forward<BaseResolver>(resolve_base)(property_type);
}

template <typename SpmoveResolver, typename BaseResolver>
football::core::XNumber ResolveShootPropertyWithSpmoveFallback(
    std::int32_t property_type,
    std::int32_t mapped_spmove_logic_id,
    SpmoveResolver&& resolve_spmove,
    BaseResolver&& resolve_base) {
    const auto value = std::forward<SpmoveResolver>(resolve_spmove)(
        property_type, mapped_spmove_logic_id);
    return value.raw > 0
        ? value
        : std::forward<BaseResolver>(resolve_base)(property_type);
}

}  // namespace football::physics::recovered
