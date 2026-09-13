#pragma once
#include "../FootballCore/FixedPoint.h"
#include <optional>
#include <cstdint>

namespace football::simulation {
using football::core::XNumber;
struct FixedVector3 { XNumber x{}, y{}, z{}; };
struct BallContact {
    std::uint32_t action_id{0};
    std::uint32_t player_id{0};
    std::int32_t contact_frame{0};
    FixedVector3 kick_point{};
    std::optional<FixedVector3> recovered_velocity{};
    bool authoritative{false};
    bool semantic_complete{false};
};
enum class BallStateKind { Free, Controlled, Kicked, Deflected, GoalkeeperControlled, DeadRestart };
struct BallState {
    FixedVector3 position{};
    FixedVector3 velocity{};
    BallStateKind kind{BallStateKind::Free};
    std::uint64_t simulation_tick{0};
};
inline bool ApplyAuthoritativeContact(BallState& state, const BallContact& contact) {
    if (!contact.authoritative || !contact.semantic_complete || !contact.recovered_velocity) return false;
    state.velocity = *contact.recovered_velocity;
    state.kind = BallStateKind::Kicked;
    return true;
}
}
