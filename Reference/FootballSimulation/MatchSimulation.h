#pragma once

#include "BallContact.h"
#include <cstdint>
#include <optional>
#include <vector>

namespace football::simulation {

/*
 * Engine-independent, server-side match shell. The movement constants here
 * are provisional new-game tuning and are not claimed as recovered mobile
 * semantics. Ball release always passes through BallContact's resolved
 * velocity gate.
 */
struct MatchCommand
{
    std::uint32_t player_id{0};
    football::core::XVector2 move{};
    std::optional<BallContact> ball_contact{};
};

struct PlayerState
{
    std::uint32_t player_id{0};
    FixedVector3 position{};
    FixedVector3 velocity{};
};

struct MatchState
{
    BallState ball{};
    std::vector<PlayerState> players{};
    std::uint32_t home_score{0};
    std::uint32_t away_score{0};
    std::uint32_t restart_count{0};
    bool goal_scored_this_tick{false};
};

class MatchSimulation
{
public:
    explicit MatchSimulation(std::int32_t step_seconds_raw = 8);

    void AddPlayer(std::uint32_t player_id, FixedVector3 position = {});
    void Tick(const MatchCommand& command);

    const MatchState& State() const noexcept { return state_; }

private:
    PlayerState* FindPlayer(std::uint32_t player_id) noexcept;
    void StepPlayer(PlayerState& player, football::core::XVector2 input);
    void StepBall();
    void ResetAfterGoal();

    static constexpr std::int32_t kPlayerSpeedRaw = 4096; // provisional shell tuning
    static constexpr std::int32_t kGoalXRaw = 102400;      // 100 fixed units
    static constexpr std::int32_t kGoalHalfWidthRaw = 10240;
    static constexpr std::int32_t kBallStepLimit = 8;

    std::int32_t step_seconds_raw_{kBallStepLimit};
    MatchState state_{};
};

} // namespace football::simulation
