#pragma once

#include "../FootballCore/FixedPoint.h"
#include "../FootballSimulation/BallContact.h"
#include <cstdint>
#include <optional>
#include <vector>

namespace football::gameplay {

enum class MatchMode : std::uint8_t { ThreeVThree = 3, FiveVFive = 5, ElevenVEleven = 11 };
enum class PlayerRole : std::uint8_t { Field, Goalkeeper };
enum class GameplayAction : std::uint8_t { None, Pass, Shoot, Dribble, Tackle, GoalkeeperSave };
enum class MatchEventType : std::uint8_t {
    CommandRejected,
    Pass,
    Shot,
    Dribble,
    TackleWon,
    TackleMissed,
    GoalkeeperSave,
    Goal,
    Restart,
};

enum class ContactProvenance : std::uint8_t {
    NewGameAuthored,
    MobileRecovered,
};

struct GameplayInput {
    std::uint32_t owner_player_id{0};
    football::core::XVector2 move{};
    football::core::XVector2 facing{football::core::Create(1024), {}};
    bool sprint{false};
    bool server_authoritative{false};
    GameplayAction action{GameplayAction::None};
    football::core::XNumber action_strength{};
    std::uint32_t target_player_id{0};
};

struct GameplayPlayerState {
    std::uint32_t player_id{0};
    std::uint8_t team{0};
    PlayerRole role{PlayerRole::Field};
    football::simulation::FixedVector3 position{};
    football::simulation::FixedVector3 velocity{};
    bool has_ball{false};
    bool user_owned{false};
};

struct GameplayEvent {
    std::uint64_t tick{0};
    MatchEventType type{MatchEventType::CommandRejected};
    std::uint32_t actor_player_id{0};
    std::uint32_t target_player_id{0};
    ContactProvenance provenance{ContactProvenance::NewGameAuthored};
};

struct PlayableMatchState {
    MatchMode mode{MatchMode::ThreeVThree};
    football::simulation::BallState ball{};
    std::vector<GameplayPlayerState> players{};
    std::vector<GameplayEvent> events{};
    std::uint32_t home_score{0};
    std::uint32_t away_score{0};
    std::uint32_t restart_count{0};
    bool goal_scored_this_tick{false};
};

/*
 * Engine-independent first playable match. It is a deterministic server-side
 * shell for validating controls and match flow before Unreal is available.
 * Its action velocity is explicitly new-game authored tuning; it is never
 * presented as recovered GetVHor/GetVVer/GetKickVelocity behavior.
 */
class PlayableMatch {
public:
    explicit PlayableMatch(MatchMode mode, std::int32_t step_seconds_raw = 8);

    static std::uint32_t PlayersPerTeam(MatchMode mode) noexcept;
    void BuildDefaultRoster();
    // Server setup hooks used by match setup/tests; clients never call these.
    bool SetServerPossession(std::uint32_t player_id);
    bool SetServerPlayerPosition(std::uint32_t player_id, football::simulation::FixedVector3 position);
    void SetServerBallState(football::simulation::FixedVector3 position,
                            football::simulation::FixedVector3 velocity,
                            football::simulation::BallStateKind kind);
    bool SubmitInput(const GameplayInput& input);
    void Tick();

    const PlayableMatchState& State() const noexcept { return state_; }
    std::int32_t StepSecondsRaw() const noexcept { return step_seconds_raw_; }

private:
    GameplayPlayerState* FindPlayer(std::uint32_t id) noexcept;
    const GameplayPlayerState* FindPlayer(std::uint32_t id) const noexcept;
    GameplayPlayerState* BallHolder() noexcept;
    void StepPlayer(GameplayPlayerState& player, const GameplayInput& input);
    void ResolveAction(const GameplayInput& input, GameplayPlayerState& player);
    void StepBall();
    void FollowControlledBall();
    void ResetAfterGoal(std::uint8_t scoring_team);
    void Emit(MatchEventType type, std::uint32_t actor, std::uint32_t target = 0,
              ContactProvenance provenance = ContactProvenance::NewGameAuthored);
    bool IsNearBall(const GameplayPlayerState& player) const noexcept;
    void SetPossession(GameplayPlayerState& player);
    void ReleasePossession();
    football::simulation::FixedVector3 AuthoredVelocity(const GameplayInput& input,
                                                        GameplayAction action) const;

    static constexpr std::int32_t kMaxSpeedRaw = 8192;
    static constexpr std::int32_t kSprintSpeedRaw = 10240;
    static constexpr std::int32_t kAccelerationRaw = 12288;
    static constexpr std::int32_t kDecelerationRaw = 16384;
    static constexpr std::int32_t kFieldHalfLengthRaw = 53248;
    static constexpr std::int32_t kFieldHalfWidthRaw = 34000;
    static constexpr std::int32_t kGoalLineRaw = 52000;
    static constexpr std::int32_t kGoalHalfWidthRaw = 7500;
    static constexpr std::int32_t kPossessionRadiusRaw = 2200;
    static constexpr std::int32_t kTackleRadiusRaw = 2600;
    static constexpr std::int32_t kBallFrictionRaw = 1023;
    static constexpr std::int32_t kAuthoredVerticalAccelRaw = -10000;

    MatchMode mode_;
    std::int32_t step_seconds_raw_;
    PlayableMatchState state_{};
    std::vector<GameplayInput> pending_inputs_{};
};

} // namespace football::gameplay
