#include "MatchSimulation.h"

#include <cmath>
#include <stdexcept>

namespace football::simulation {

using football::core::Add;
using football::core::Create;
using football::core::Multiply;
using football::core::Normalize;
using football::core::XNumber;
using football::core::XVector2;

MatchSimulation::MatchSimulation(std::int32_t step_seconds_raw)
    : step_seconds_raw_(step_seconds_raw)
{
    if (step_seconds_raw_ <= 0) {
        throw std::invalid_argument("simulation step must be positive");
    }
}

void MatchSimulation::AddPlayer(std::uint32_t player_id, FixedVector3 position)
{
    if (FindPlayer(player_id) != nullptr) {
        return;
    }
    state_.players.push_back(PlayerState{player_id, position, {}});
}

PlayerState* MatchSimulation::FindPlayer(std::uint32_t player_id) noexcept
{
    for (PlayerState& player : state_.players) {
        if (player.player_id == player_id) {
            return &player;
        }
    }
    return nullptr;
}

void MatchSimulation::StepPlayer(PlayerState& player, XVector2 input)
{
    const XVector2 direction = Normalize(input);
    const XNumber speed = Create(kPlayerSpeedRaw);
    const XNumber step = Create(step_seconds_raw_);

    player.velocity.x = Multiply(direction.x, speed);
    player.velocity.y = Multiply(direction.y, speed);
    player.position.x = Add(player.position.x, Multiply(player.velocity.x, step));
    player.position.y = Add(player.position.y, Multiply(player.velocity.y, step));
}

void MatchSimulation::StepBall()
{
    if (state_.ball.kind == BallStateKind::DeadRestart) {
        return;
    }

    const XNumber step = Create(step_seconds_raw_);
    state_.ball.position.x = Add(
        state_.ball.position.x,
        Multiply(state_.ball.velocity.x, step));
    state_.ball.position.y = Add(
        state_.ball.position.y,
        Multiply(state_.ball.velocity.y, step));
    state_.ball.position.z = Add(
        state_.ball.position.z,
        Multiply(state_.ball.velocity.z, step));

    if (state_.ball.position.x.raw >= kGoalXRaw &&
        std::abs(state_.ball.position.y.raw) <= kGoalHalfWidthRaw) {
        ++state_.home_score;
        ResetAfterGoal();
    }
}

void MatchSimulation::ResetAfterGoal()
{
    state_.ball.position = {};
    state_.ball.velocity = {};
    state_.ball.kind = BallStateKind::DeadRestart;
    ++state_.restart_count;
    state_.goal_scored_this_tick = true;
}

void MatchSimulation::Tick(const MatchCommand& command)
{
    state_.goal_scored_this_tick = false;

    if (PlayerState* player = FindPlayer(command.player_id)) {
        StepPlayer(*player, command.move);
    }

    if (command.ball_contact.has_value()) {
        BallState candidate = state_.ball;
        if (ApplyAuthoritativeContact(candidate, *command.ball_contact)) {
            candidate.position = command.ball_contact->kick_point;
            state_.ball = candidate;
        }
    }

    StepBall();
    ++state_.ball.simulation_tick;
}

} // namespace football::simulation
