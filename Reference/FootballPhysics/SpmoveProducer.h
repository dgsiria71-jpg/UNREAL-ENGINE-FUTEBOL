#pragma once
#include "NativeVectorMath.h"
#include <array>

namespace football::physics::recovered {
// Boundary inputs for calSpmoveInUse: geometry/curve/property queries remain
// explicit dependencies, not invented recovered implementations.
struct SpmoveProducerContext {
    std::int32_t goal_type{}, first_byte{}, disturbed_raw{}, static_disturbed_raw{};
    std::uint32_t collection15{}, collection32{}, collection16{};
    std::int32_t ball_x{}, ball_z{}, center_x{}, center_z{};
    std::int32_t angle_raw{}, limit_170{}, limit_174{}, limit_178{}, curve_result_raw{};
    std::uint32_t successful_properties{}; // 417,41A,418,3FC,3FB,40B query results
};
struct SpmoveProducedFlags {
    std::array<std::uint8_t,7> bytes{};
    std::int32_t distance_raw{};
    std::uint32_t queries{};
};
inline std::int32_t NativeAbs32(std::int32_t x) noexcept {
    return x < 0 ? core::WrapInt32(-static_cast<std::int64_t>(x)) : x;
}
inline SpmoveProducedFlags ProduceSpmoveFlags(const SpmoveProducerContext& c) {
    SpmoveProducedFlags r;
    auto query = [&](unsigned index) {
        r.queries |= 1u << index;
        return static_cast<std::uint8_t>((c.successful_properties >> index) & 1);
    };
    r.bytes[3] = static_cast<std::uint8_t>(c.first_byte & 1);
    if (c.disturbed_raw != c.static_disturbed_raw && (c.collection15 & 1)) r.bytes[1]=query(0);
    if (c.collection32 & 1) r.bytes[0]=query(1);
    const auto dx=core::WrapInt32(static_cast<std::int64_t>(c.ball_x)-c.center_x);
    const auto dz=core::WrapInt32(static_cast<std::int64_t>(c.ball_z)-c.center_z);
    if (c.limit_170 > c.angle_raw && c.limit_174 > NativeAbs32(dx) &&
        c.limit_178 < NativeAbs32(c.ball_z)) r.bytes[2]=query(2);
    const auto square=static_cast<std::uint64_t>(static_cast<std::int64_t>(dx)*dx)+
                      static_cast<std::uint64_t>(static_cast<std::int64_t>(dz)*dz);
    // Native sqrt interprets the wrapping 64-bit sum as signed.
    const auto signed_square = square <= 0x7fffffffffffffffULL ? static_cast<std::int64_t>(square) :
        -1-static_cast<std::int64_t>(~square);
    r.distance_raw=SqrtLong(signed_square);
    if (c.curve_result_raw >= 1025 && (c.collection15 & 1)) r.bytes[5]=query(3);
    if (c.collection16 & 1) r.bytes[4]=query(4);
    if (c.goal_type==0x16B6 || c.goal_type==0x16B3) r.bytes[6]=query(5);
    return r;
}
}
