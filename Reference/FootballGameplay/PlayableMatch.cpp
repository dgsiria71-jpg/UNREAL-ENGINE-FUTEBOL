#include "PlayableMatch.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace football::gameplay {

using football::core::Add;
using football::core::Clamp;
using football::core::Create;
using football::core::Multiply;
using football::core::Normalize;
using football::core::Subtract;
using football::core::XNumber;
using football::core::XVector2;
using football::simulation::BallStateKind;
using football::simulation::FixedVector3;

namespace {

std::int32_t Approach(std::int32_t current, std::int32_t target, std::int32_t delta) noexcept
{
    if (current < target) return std::min(current + delta, target);
    if (current > target) return std::max(current - delta, target);
    return current;
}

XNumber Raw(std::int32_t value) noexcept { return Create(value); }

std::int32_t DistanceSquared(const FixedVector3& a, const FixedVector3& b) noexcept
{
    const std::int64_t dx = static_cast<std::int64_t>(a.x.raw) - b.x.raw;
    const std::int64_t dy = static_cast<std::int64_t>(a.y.raw) - b.y.raw;
    return static_cast<std::int32_t>(std::min<std::int64_t>(
        dx * dx + dy * dy, std::numeric_limits<std::int32_t>::max()));
}

} // namespace

PlayableMatch::PlayableMatch(MatchMode mode, std::int32_t step_seconds_raw)
    : mode_(mode), step_seconds_raw_(step_seconds_raw)
{
    if (step_seconds_raw_ <= 0) {
        throw std::invalid_argument("simulation step must be positive");
    }
    state_.mode = mode_;
    BuildDefaultRoster();
}

std::uint32_t PlayableMatch::PlayersPerTeam(MatchMode mode) noexcept
{
    return static_cast<std::uint32_t>(mode);
}

void PlayableMatch::BuildDefaultRoster()
{
    state_.players.clear();
    state_.events.clear();
    state_.ball = {};
    state_.home_score = 0;
    state_.away_score = 0;
    state_.restart_count = 0;
    state_.goal_scored_this_tick = false;

    const std::uint32_t per_team = PlayersPerTeam(mode_);
    for (std::uint8_t team = 0; team < 2; ++team) {
        for (std::uint32_t slot = 0; slot < per_team; ++slot) {
            GameplayPlayerState player{};
            player.player_id = static_cast<std::uint32_t>(team) * 1000U + slot + 1U;
            player.team = team;
            player.role = slot == 0 ? PlayerRole::Goalkeeper : PlayerRole::Field;
            player.user_owned = slot == 1;
            const std::int32_t x = team == 0 ? -42000 : 42000;
            const std::int32_t y = static_cast<std::int32_t>(slot) * 7000 -
                                    static_cast<std::int32_t>(per_team - 1) * 3500;
            player.position = {Raw(x), Raw(y), {}};
            state_.players.push_back(player);
        }
    }
    // Give the first home field player the initial ball for immediate testing.
    if (GameplayPlayerState* player = FindPlayer(2)) {
        SetPossession(*player);
    }
}

bool PlayableMatch::SetServerPossession(std::uint32_t player_id)
{
    GameplayPlayerState* player = FindPlayer(player_id);
    if (player == nullptr) return false;
    SetPossession(*player);
    return true;
}

bool PlayableMatch::SetServerPlayerPosition(std::uint32_t player_id, FixedVector3 position)
{
    GameplayPlayerState* player = FindPlayer(player_id);
    if (player == nullptr) return false;
    player->position = position;
    if (player->has_ball) state_.ball.position = position;
    return true;
}

void PlayableMatch::SetServerBallState(FixedVector3 position, FixedVector3 velocity,
                                       BallStateKind kind)
{
    ReleasePossession();
    state_.ball.position = position;
    state_.ball.velocity = velocity;
    state_.ball.kind = kind;
}

GameplayPlayerState* PlayableMatch::FindPlayer(std::uint32_t id) noexcept
{
    for (GameplayPlayerState& player : state_.players) {
        if (player.player_id == id) return &player;
    }
    return nullptr;
}

const GameplayPlayerState* PlayableMatch::FindPlayer(std::uint32_t id) const noexcept
{
    for (const GameplayPlayerState& player : state_.players) {
        if (player.player_id == id) return &player;
    }
    return nullptr;
}

GameplayPlayerState* PlayableMatch::BallHolder() noexcept
{
    if (state_.ball.kind != BallStateKind::Controlled) return nullptr;
    for (GameplayPlayerState& player : state_.players) {
        if (player.has_ball) return &player;
    }
    return nullptr;
}

bool PlayableMatch::SubmitInput(const GameplayInput& input)
{
    GameplayPlayerState* owner = FindPlayer(input.owner_player_id);
    if (input.owner_player_id == 0 || owner == nullptr ||
        (!owner->user_owned && !input.server_authoritative)) {
        Emit(MatchEventType::CommandRejected, input.owner_player_id);
        return false;
    }
    pending_inputs_.push_back(input);
    return true;
}

void PlayableMatch::Emit(MatchEventType type, std::uint32_t actor, std::uint32_t target,
                         ContactProvenance provenance)
{
    state_.events.push_back(GameplayEvent{state_.ball.simulation_tick, type, actor, target, provenance});
}

void PlayableMatch::SetPossession(GameplayPlayerState& player)
{
    for (GameplayPlayerState& candidate : state_.players) candidate.has_ball = false;
    player.has_ball = true;
    state_.ball.kind = BallStateKind::Controlled;
    state_.ball.position = player.position;
    state_.ball.velocity = {};
}

void PlayableMatch::ReleasePossession()
{
    for (GameplayPlayerState& player : state_.players) player.has_ball = false;
    if (state_.ball.kind == BallStateKind::Controlled) state_.ball.kind = BallStateKind::Free;
}

bool PlayableMatch::IsNearBall(const GameplayPlayerState& player) const noexcept
{
    return DistanceSquared(player.position, state_.ball.position) <=
           kPossessionRadiusRaw * kPossessionRadiusRaw;
}

void PlayableMatch::StepPlayer(GameplayPlayerState& player, const GameplayInput& input)
{
    const XVector2 direction = Normalize(input.move);
    const std::int32_t max_speed = input.sprint ? kSprintSpeedRaw : kMaxSpeedRaw;
    const XNumber speed = Raw(max_speed);
    const XNumber step = Raw(step_seconds_raw_);
    const XNumber desired_x = Multiply(direction.x, speed);
    const XNumber desired_y = Multiply(direction.y, speed);
    const bool moving = direction.x.raw != 0 || direction.y.raw != 0;
    const std::int32_t accel_delta = static_cast<std::int32_t>(
        (static_cast<std::int64_t>(moving ? kAccelerationRaw : kDecelerationRaw) * step_seconds_raw_) >> 10);

    player.velocity.x.raw = Approach(player.velocity.x.raw, desired_x.raw, accel_delta);
    player.velocity.y.raw = Approach(player.velocity.y.raw, desired_y.raw, accel_delta);
    player.position.x = Add(player.position.x, Multiply(player.velocity.x, step));
    player.position.y = Add(player.position.y, Multiply(player.velocity.y, step));
    player.position.x.raw = std::clamp(player.position.x.raw, -kFieldHalfLengthRaw, kFieldHalfLengthRaw);
    player.position.y.raw = std::clamp(player.position.y.raw, -kFieldHalfWidthRaw, kFieldHalfWidthRaw);
}

FixedVector3 PlayableMatch::AuthoredVelocity(const GameplayInput& input, GameplayAction action) const
{
    const XVector2 direction = Normalize(input.facing);
    const std::int32_t strength = std::clamp(input.action_strength.raw, 0, 1024);
    const std::int32_t base = action == GameplayAction::Shoot ? 18000 : 10500;
    const std::int32_t range = action == GameplayAction::Shoot ? 22000 : 8500;
    const std::int32_t horizontal = base + static_cast<std::int32_t>(
        (static_cast<std::int64_t>(range) * strength) >> 10);
    const std::int32_t lift = action == GameplayAction::Shoot
        ? 1800 + static_cast<std::int32_t>((static_cast<std::int64_t>(9000) * strength) >> 10)
        : 350;
    return {Multiply(direction.x, Raw(horizontal)),
            Multiply(direction.y, Raw(horizontal)), Raw(lift)};
}

void PlayableMatch::ResolveAction(const GameplayInput& input, GameplayPlayerState& player)
{
    if (input.action == GameplayAction::None) return;

    if (input.action == GameplayAction::Tackle) {
        GameplayPlayerState* nearest = nullptr;
        std::int32_t nearest_distance = std::numeric_limits<std::int32_t>::max();
        for (GameplayPlayerState& candidate : state_.players) {
            if (candidate.team == player.team || !candidate.has_ball) continue;
            const std::int32_t distance = DistanceSquared(player.position, candidate.position);
            if (distance <= kTackleRadiusRaw * kTackleRadiusRaw && distance < nearest_distance) {
                nearest = &candidate;
                nearest_distance = distance;
            }
        }
        if (nearest != nullptr) {
            SetPossession(player);
            Emit(MatchEventType::TackleWon, player.player_id, nearest->player_id);
        } else {
            Emit(MatchEventType::TackleMissed, player.player_id);
        }
        return;
    }

    if (input.action == GameplayAction::GoalkeeperSave && player.role == PlayerRole::Goalkeeper) {
        if (state_.ball.kind != BallStateKind::Controlled && IsNearBall(player)) {
            SetPossession(player);
            Emit(MatchEventType::GoalkeeperSave, player.player_id);
        }
        return;
    }

    if (!player.has_ball || !IsNearBall(player)) return;

    if (input.action == GameplayAction::Dribble) {
        Emit(MatchEventType::Dribble, player.player_id);
        return;
    }

    if (input.action == GameplayAction::Pass || input.action == GameplayAction::Shoot) {
        state_.ball.position = player.position;
        state_.ball.velocity = AuthoredVelocity(input, input.action);
        state_.ball.kind = BallStateKind::Kicked;
        ReleasePossession();
        Emit(input.action == GameplayAction::Pass ? MatchEventType::Pass : MatchEventType::Shot,
             player.player_id, input.target_player_id, ContactProvenance::NewGameAuthored);
    }
}

void PlayableMatch::FollowControlledBall()
{
    if (GameplayPlayerState* holder = BallHolder()) {
        state_.ball.position = holder->position;
        state_.ball.position.z = Raw(900);
        state_.ball.velocity = holder->velocity;
    }
}

void PlayableMatch::StepBall()
{
    if (state_.ball.kind == BallStateKind::DeadRestart ||
        state_.ball.kind == BallStateKind::Controlled) {
        return;
    }

    const XNumber step = Raw(step_seconds_raw_);
    state_.ball.position.x = Add(state_.ball.position.x, Multiply(state_.ball.velocity.x, step));
    state_.ball.position.y = Add(state_.ball.position.y, Multiply(state_.ball.velocity.y, step));
    state_.ball.position.z = Add(state_.ball.position.z, Multiply(state_.ball.velocity.z, step));
    state_.ball.velocity.z = Add(state_.ball.velocity.z,
                                 Multiply(Raw(kAuthoredVerticalAccelRaw), step));
    state_.ball.velocity.x = Multiply(state_.ball.velocity.x, Raw(kBallFrictionRaw));
    state_.ball.velocity.y = Multiply(state_.ball.velocity.y, Raw(kBallFrictionRaw));

    if (state_.ball.position.z.raw < 0) {
        state_.ball.position.z = {};
        if (std::abs(state_.ball.velocity.z.raw) > 500) {
            state_.ball.velocity.z.raw = -state_.ball.velocity.z.raw / 2;
        } else {
            state_.ball.velocity.z = {};
        }
    }

    if (state_.ball.position.x.raw >= kGoalLineRaw &&
        std::abs(state_.ball.position.y.raw) <= kGoalHalfWidthRaw) {
        ++state_.home_score;
        ResetAfterGoal(0);
    } else if (state_.ball.position.x.raw <= -kGoalLineRaw &&
               std::abs(state_.ball.position.y.raw) <= kGoalHalfWidthRaw) {
        ++state_.away_score;
        ResetAfterGoal(1);
    }
}

void PlayableMatch::ResetAfterGoal(std::uint8_t scoring_team)
{
    ReleasePossession();
    state_.ball.position = {};
    state_.ball.velocity = {};
    state_.ball.kind = BallStateKind::DeadRestart;
    state_.goal_scored_this_tick = true;
    ++state_.restart_count;
    Emit(MatchEventType::Goal, scoring_team == 0 ? 2 : 1002);
    Emit(MatchEventType::Restart, 0);
}

void PlayableMatch::Tick()
{
    state_.goal_scored_this_tick = false;

    // One command per owner per fixed tick: the last command is authoritative.
    std::vector<GameplayInput> commands;
    commands.swap(pending_inputs_);
    for (const GameplayInput& input : commands) {
        if (GameplayPlayerState* player = FindPlayer(input.owner_player_id)) {
            StepPlayer(*player, input);
            ResolveAction(input, *player);
        }
    }
    FollowControlledBall();
    StepBall();
    ++state_.ball.simulation_tick;
}

} // namespace football::gameplay
