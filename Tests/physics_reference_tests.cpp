#include "../Reference/FootballPhysics/SpmoveProducer.h"
#include "../Reference/FootballPhysics/SpmoveSelection.h"
#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballSimulation/BallContact.h"
#include "../Reference/FootballSimulation/MatchSimulation.h"
#include "../Reference/FootballGameplay/PlayableMatch.h"
#include "../Reference/FootballPhysics/SpmoveBranches.h"
#include "../Reference/FootballPhysics/SpmoveInventoryCache.h"
#ifdef NDEBUG
#error Reference tests require enabled assertions.
#endif
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>

using namespace football::core;
using namespace football::simulation;
using namespace football::gameplay;

static void test_fixed_math() {
    assert(Multiply(Create(2048), Create(512)).raw == 1024);
    assert(Divide(Create(1024), Create(2048)).raw == 512);
    assert(Lerp(Create(0), Create(10240), Create(512)).raw == 5120);
    assert(InverseLerp(Create(0), Create(10240), Create(5120)).raw == 512);
    assert(RemapClamped(Create(20480), Create(0), Create(10240), Create(0), Create(2048)).raw == 2048);
    assert(WrapInt32(static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max()) + 1) == std::numeric_limits<std::int32_t>::min());
}

static void test_contact_gate() {
    BallState state{};
    BallContact unresolved{};
    unresolved.authoritative = true;
    assert(!ApplyAuthoritativeContact(state, unresolved));

    FixedVector3 v{Create(1024), Create(2048), Create(-512)};
    BallContact complete{};
    complete.authoritative = true;
    complete.semantic_complete = true;
    complete.recovered_velocity = v;
    assert(ApplyAuthoritativeContact(state, complete));
    assert(state.kind == BallStateKind::Kicked);
    assert(state.velocity.y.raw == 2048);
}

static void test_unresolved_contact_cannot_move_ball() {
    MatchSimulation simulation;
    simulation.AddPlayer(1);

    BallContact unresolved{};
    unresolved.authoritative = true;
    MatchCommand command{};
    command.player_id = 1;
    command.ball_contact = unresolved;

    for (int i = 0; i < 4; ++i) {
        simulation.Tick(command);
    }

    assert(simulation.State().ball.position.x.raw == 0);
    assert(simulation.State().ball.kind == BallStateKind::Free);
}

static void test_resolved_contact_scores_and_resets() {
    MatchSimulation simulation;
    simulation.AddPlayer(1);

    BallContact contact{};
    contact.player_id = 1;
    contact.authoritative = true;
    contact.semantic_complete = true;
    contact.recovered_velocity = FixedVector3{Create(102400), Create(0), Create(0)};
    contact.kick_point = FixedVector3{Create(0), Create(0), Create(0)};

    MatchCommand command{};
    command.player_id = 1;
    command.ball_contact = contact;

    for (int i = 0; i < 140 && simulation.State().home_score == 0; ++i) {
        simulation.Tick(command);
        command.ball_contact.reset();
    }

    assert(simulation.State().home_score == 1);
    assert(simulation.State().restart_count == 1);
    assert(simulation.State().goal_scored_this_tick);
    assert(simulation.State().ball.kind == BallStateKind::DeadRestart);
    assert(simulation.State().ball.velocity.x.raw == 0);
}

static void test_movement_is_deterministic() {
    MatchSimulation a;
    MatchSimulation b;
    a.AddPlayer(7);
    b.AddPlayer(7);

    MatchCommand command{};
    command.player_id = 7;
    command.move = XVector2{Create(1024), Create(512)};

    for (int i = 0; i < 120; ++i) {
        a.Tick(command);
        b.Tick(command);
    }

    const PlayerState& pa = a.State().players.front();
    const PlayerState& pb = b.State().players.front();
    assert(pa.position.x.raw == pb.position.x.raw);
    assert(pa.position.y.raw == pb.position.y.raw);
    assert(a.State().ball.simulation_tick == b.State().ball.simulation_tick);
}


static const GameplayPlayerState& player(const PlayableMatch& match, std::uint32_t id) {
    for (const auto& candidate : match.State().players) {
        if (candidate.player_id == id) return candidate;
    }
    assert(false && "player not found");
    return match.State().players.front();
}

static void test_playable_match_modes_and_rosters() {
    PlayableMatch three(MatchMode::ThreeVThree);
    PlayableMatch five(MatchMode::FiveVFive);
    PlayableMatch eleven(MatchMode::ElevenVEleven);
    assert(three.State().players.size() == 6);
    assert(five.State().players.size() == 10);
    assert(eleven.State().players.size() == 22);
    for (const PlayableMatch* match : {&three, &five, &eleven}) {
        int goalkeepers = 0;
        for (const auto& p : match->State().players) {
            if (p.role == PlayerRole::Goalkeeper) ++goalkeepers;
        }
        assert(goalkeepers == 2);
    }
}

static void test_input_ownership_is_server_authoritative() {
    PlayableMatch match(MatchMode::ThreeVThree);
    GameplayInput rejected{};
    rejected.owner_player_id = 1003; // AI player; client cannot own it.
    assert(!match.SubmitInput(rejected));
    GameplayInput accepted{};
    accepted.owner_player_id = 2; // explicitly marked user-owned in setup.
    assert(match.SubmitInput(accepted));
    GameplayInput server_command{};
    server_command.owner_player_id = 1002;
    server_command.server_authoritative = true;
    assert(match.SubmitInput(server_command));
}

static void test_acceleration_and_braking_are_deterministic() {
    PlayableMatch a(MatchMode::ThreeVThree);
    PlayableMatch b(MatchMode::ThreeVThree);
    GameplayInput move{};
    move.owner_player_id = 2;
    move.move = XVector2{Create(1024), Create(0)};
    for (int i = 0; i < 120; ++i) {
        assert(a.SubmitInput(move));
        assert(b.SubmitInput(move));
        a.Tick();
        b.Tick();
    }
    assert(player(a, 2).position.x.raw == player(b, 2).position.x.raw);
    assert(player(a, 2).velocity.x.raw > 0);
    const std::int32_t running_speed = player(a, 2).velocity.x.raw;
    move.move = {};
    for (int i = 0; i < 30; ++i) {
        assert(a.SubmitInput(move));
        a.Tick();
    }
    assert(player(a, 2).velocity.x.raw < running_speed);
}

static void test_pass_releases_control_and_moves_ball() {
    PlayableMatch match(MatchMode::ThreeVThree);
    GameplayInput pass{};
    pass.owner_player_id = 2;
    pass.facing = XVector2{Create(1024), Create(0)};
    pass.action = GameplayAction::Pass;
    pass.action_strength = Create(1024);
    pass.target_player_id = 3;
    assert(match.SubmitInput(pass));
    match.Tick();
    assert(match.State().ball.kind == BallStateKind::Kicked);
    assert(!player(match, 2).has_ball);
    assert(match.State().ball.velocity.x.raw > 0);
    const std::int32_t x0 = match.State().ball.position.x.raw;
    for (int i = 0; i < 10; ++i) match.Tick();
    assert(match.State().ball.position.x.raw > x0);
    assert(match.State().events.size() >= 1);
    assert(match.State().events.front().type == MatchEventType::Pass);
}

static void test_dribble_keeps_controlled_ball_with_holder() {
    PlayableMatch match(MatchMode::ThreeVThree);
    GameplayInput dribble{};
    dribble.owner_player_id = 2;
    dribble.move = XVector2{Create(1024), Create(0)};
    dribble.action = GameplayAction::Dribble;
    assert(match.SubmitInput(dribble));
    match.Tick();
    assert(match.State().ball.kind == BallStateKind::Controlled);
    assert(player(match, 2).has_ball);
    assert(match.State().ball.position.z.raw == 900);
    assert(match.State().events.back().type == MatchEventType::Dribble);
}

static void test_tackle_wins_possession_from_nearby_opponent() {
    PlayableMatch match(MatchMode::ThreeVThree);
    assert(match.SetServerPossession(1002));
    assert(match.SetServerPlayerPosition(1002, FixedVector3{Create(-42000), Create(0), {}}));
    assert(match.SetServerPlayerPosition(2, FixedVector3{Create(-40000), Create(0), {}}));
    GameplayInput tackle{};
    tackle.owner_player_id = 2;
    tackle.action = GameplayAction::Tackle;
    assert(match.SubmitInput(tackle));
    match.Tick();
    assert(player(match, 2).has_ball);
    assert(!player(match, 1002).has_ball);
    assert(match.State().events.back().type == MatchEventType::TackleWon);
}

static void test_goalkeeper_save_captures_nearby_ball() {
    PlayableMatch match(MatchMode::ThreeVThree);
    const auto& keeper = player(match, 1);
    match.SetServerBallState(keeper.position, FixedVector3{Create(-1000), {}, {}}, BallStateKind::Kicked);
    GameplayInput save{};
    save.owner_player_id = 1;
    save.server_authoritative = true;
    save.action = GameplayAction::GoalkeeperSave;
    assert(match.SubmitInput(save));
    match.Tick();
    assert(match.State().ball.kind == BallStateKind::Controlled);
    assert(player(match, 1).has_ball);
    assert(match.State().events.back().type == MatchEventType::GoalkeeperSave);
}

static void test_goal_and_restart_are_deterministic() {
    PlayableMatch match(MatchMode::ThreeVThree);
    match.SetServerBallState(FixedVector3{Create(51000), {}, {}},
                             FixedVector3{Create(30000), {}, {}}, BallStateKind::Kicked);
    for (int i = 0; i < 20 && match.State().home_score == 0; ++i) match.Tick();
    assert(match.State().home_score == 1);
    assert(match.State().restart_count == 1);
    assert(match.State().goal_scored_this_tick);
    assert(match.State().ball.kind == BallStateKind::DeadRestart);
    assert(match.State().events.size() >= 2);
    assert(match.State().events[match.State().events.size() - 2].type == MatchEventType::Goal);
    assert(match.State().events.back().type == MatchEventType::Restart);
}


static void test_recovered_fractional_rounding() {
    // These cases fail the former truncating implementation.
    assert(Multiply(Create(1), Create(512)).raw == 1);
    assert(Multiply(Create(-1), Create(512)).raw == 0);
    assert(Multiply(Create(-3), Create(512)).raw == -1);
    assert(Divide(Create(2), Create(3)).raw == 683);
    assert(Divide(Create(-2), Create(3)).raw == -683);
    assert(Divide(Create(2), Create(-3)).raw == -683);
    bool guarded = false;
    try { (void)Divide(Create(1), Create(0)); }
    catch (const std::domain_error&) { guarded = true; }
    assert(guarded); // explicit host policy; native zero fallback still excluded
}

static void test_recovered_vector_math_is_not_floating_sqrt() {
    using namespace football::physics::recovered;
    assert(SqrtLong(255) == 15);
    assert(SqrtLong(256) == 17); // original lookup behavior, not floor(sqrt)
    assert(SqrtLong(65536) == 256);
    assert(SqrtLong(-1) == 0);
    const auto unit = NormalizeNative({1023,0,0});
    assert(unit.x == 1023); // preserve near-unit band instead of forcing 1024
    const auto tiny = NormalizeNative({1,-1,1});
    assert(tiny.x == 591 && tiny.y == -591 && tiny.z == 591);
}

static void test_selected_spmove_guards_and_sequence() {
    using namespace football::physics::recovered;
    SelectedSpmoveParameters selected;
    const RawVector3 v{0,24000,0};
    auto out = ApplyVHorSpmove(v, 0xFFFFFFFFFFFFFFULL, selected);
    assert(out.x == 0 && out.y == 24000 && out.z == 0); // null lookup preserves base
    selected.long_kick = std::vector<std::int32_t>{0,4000,0};
    selected.shoot_push = std::vector<std::int32_t>{};
    // Long-kick zero factor cancels velocity; then the magnitude guard skips
    // push, even though its present list is malformed. No premature lookup.
    out = ApplyVVerBallisticSpmove(v, (1ULL<<40)|1, selected);
    assert(out.x == 0 && out.y == 0 && out.z == 0);
    selected.head = std::vector<std::int32_t>{0,0,1500};
    out = ApplyVVerHeadSpmove({0,1024,0}, 1ULL<<32, selected);
    assert(out.y == -476); // subtract magnitude without an invented zero clamp
    selected.shoot_first = std::vector<std::int32_t>{};
    bool rejected = false;
    try { (void)ApplyVHorSpmove(v, 1ULL<<24, selected); }
    catch (const std::out_of_range&) { rejected = true; }
    assert(rejected); // malformed selected data must not become zero tuning
}

static void test_spmove_selection_preserves_native_priority_and_nulls() {
    using namespace football::physics::recovered;
    SpmoveInventory inventory{{0x3FE, {{100, 700}, {200, 800}, {200, 900}}}};
    SpmoveConfigMap configs{{100, {100, 99, 999, 100, 1, std::vector<std::int32_t>{1500}}},
                            {200, {200, 1, 0, 0, 0, std::vector<std::int32_t>{3000}}}};
    SpmoveSelector selector(inventory, configs);
    assert(selector.Config(0x3FE)->id == 200); // signed child ID wins, not metadata
    assert(MaxSpmoveId(inventory.at(0x3FE), 1) == 900); // positive father on tie
    assert(MaxSpmoveId(inventory.at(0x3FE), 2) == 200); // only low bit
    assert(selector.Parameters(0x3FE, 2) == nullptr);
    assert(selector.Parameters(0x3FE, 3)->at(0) == 3000);
    configs.erase(200);
    assert(selector.Config(0x3FE) == nullptr); // missing winner cannot fall back
    configs.emplace(200, SpmoveConfigRecord{200,0,0,0,0,std::vector<std::int32_t>{}});
    assert(selector.Parameters(0x3FE,1) && selector.Parameters(0x3FE,1)->empty());
    configs.at(200).runtime_parameters.reset();
    assert(selector.Parameters(0x3FE,1) == nullptr);
    assert(selector.Config(12345) == nullptr);
}

static football::physics::recovered::SpmoveConfigMap collector_configs() {
    using namespace football::physics::recovered;
    SpmoveConfigMap configs;
    configs.emplace(10, SpmoveConfigRecord{10, 1, 0, 0, 1, std::nullopt,
                                            100, std::vector<std::int32_t>{20}});
    configs.emplace(20, SpmoveConfigRecord{20, 2, 0, 0, 1, std::nullopt,
                                            200, std::vector<std::int32_t>{}});
    configs.emplace(30, SpmoveConfigRecord{30, 1, 0, 0, 1, std::nullopt,
                                            100, std::nullopt});
    configs.emplace(40, SpmoveConfigRecord{40, 1, 0, 0, 0, std::nullopt,
                                            300, std::nullopt});
    return configs;
}

static void test_spmove_inventory_collector_expands_native_shape() {
    using namespace football::physics::recovered;
    const auto configs = collector_configs();
    const auto result = CollectAllSpmoves(configs, {10, 20, 30, 40});
    assert(result.complete());
    assert(result.entries.at(100).size() == 2);
    assert(result.entries.at(100)[0].child_id == 10);
    assert(result.entries.at(100)[0].father_id == 0);
    assert(result.entries.at(100)[1].child_id == 30);
    assert(result.entries.at(200).size() == 2);
    assert(result.entries.at(200)[0].child_id == 20);
    assert(result.entries.at(200)[0].father_id == 10);
    assert(result.entries.at(200)[1].child_id == 20);
    assert(result.entries.at(200)[1].father_id == 0);
    assert(result.entries.find(300) == result.entries.end());
}

static void test_spmove_inventory_collector_preserves_manager_paths() {
    using namespace football::physics::recovered;
    auto configs = collector_configs();
    auto result = CollectSpmovesForManager(false, -1, configs, {}, {999, 10});
    assert(result.complete()); // missing player roots are skipped by the native path
    assert(result.entries.at(100).size() == 1);
    assert(result.entries.at(200).size() == 1);
    assert(result.entries.at(200)[0].father_id == 10);

    result = CollectSpmovesForManager(false, 0, configs, {10, 20, 30}, {10});
    assert(result.complete() && result.entries.empty());

    result = CollectPlayerSpmoves(configs, {40});
    assert(result.complete() && result.entries.empty());

    configs.at(10).child_spmove_ids = std::vector<std::int32_t>{40};
    result = CollectPlayerSpmoves(configs, {10});
    assert(!result.complete());
    assert(result.status == SpmoveCollectionStatus::MissingChildConfig);
    assert(result.missing_config_id == 40);

    configs.at(10).child_spmove_ids = std::vector<std::int32_t>{404};
    result = CollectPlayerSpmoves(configs, {10});
    assert(!result.complete());
    assert(result.status == SpmoveCollectionStatus::MissingChildConfig);
    assert(result.missing_config_id == 404);

    result = CollectAllSpmoves(configs, {777});
    assert(!result.complete());
    assert(result.status == SpmoveCollectionStatus::MissingAllConfigRoot);
    assert(result.missing_config_id == 777);
}

static void test_spmove_inventory_cache_boundary() {
    using namespace football::physics::recovered;
    SpmoveInventoryCache cache;
    SpmoveInventorySnapshot player{{{0x3FE, {{11, 0}}}}, "player_snapshot"};
    SpmoveInventorySnapshot all{{{0x3FE, {{99, 0}}}}, "all_config_snapshot"};
    assert(cache.Refresh(false, &player));
    assert(cache.initialized() && !cache.open_all());
    assert(cache.entries().at(0x3FE).front().child_id == 11);
    assert(!cache.Refresh(false, &all));
    assert(cache.entries().at(0x3FE).front().child_id == 11);
    assert(cache.Refresh(true, &all));
    assert(cache.open_all());
    assert(cache.entries().at(0x3FE).front().child_id == 99);
    cache.Invalidate();
    assert(!cache.initialized() && cache.entries().empty());
}

static void test_spmove_producer_strict_boundaries_and_reset() {
    using namespace football::physics::recovered;
    SpmoveProducerContext c;
    c.goal_type=0x16B3; c.first_byte=254;
    c.collection15=1; c.collection32=1; c.collection16=1;
    c.ball_x=3072; c.ball_z=4096; c.angle_raw=100;
    c.limit_170=101; c.limit_174=3073; c.limit_178=4095;
    c.successful_properties=63; c.curve_result_raw=1024;
    auto r=ProduceSpmoveFlags(c);
    assert(r.bytes[3]==0 && r.bytes[1]==0 && r.bytes[2]==1 && r.bytes[5]==0);
    assert(r.distance_raw==5120);
    c.limit_170=100; c.curve_result_raw=1025; c.first_byte=255;
    r=ProduceSpmoveFlags(c);
    assert(r.bytes[2]==0 && r.bytes[5]==1 && r.bytes[3]==1);
    assert(r.bytes[6]==1 && r.bytes[4]==1 && r.bytes[0]==1);
    c.successful_properties=0;
    r=ProduceSpmoveFlags(c);
    assert(r.bytes[3]==1 && r.bytes[6]==0 && r.bytes[4]==0 && r.bytes[0]==0);
}

int main() {
    test_spmove_producer_strict_boundaries_and_reset();
    test_spmove_inventory_collector_preserves_manager_paths();
    test_spmove_inventory_collector_expands_native_shape();
    test_spmove_inventory_cache_boundary();
    test_spmove_selection_preserves_native_priority_and_nulls();
    test_recovered_fractional_rounding();
    test_recovered_vector_math_is_not_floating_sqrt();
    test_selected_spmove_guards_and_sequence();
    test_fixed_math();
    test_contact_gate();
    test_unresolved_contact_cannot_move_ball();
    test_resolved_contact_scores_and_resets();
    test_movement_is_deterministic();
    test_playable_match_modes_and_rosters();
    test_input_ownership_is_server_authoritative();
    test_acceleration_and_braking_are_deterministic();
    test_pass_releases_control_and_moves_ball();
    test_dribble_keeps_controlled_ball_with_holder();
    test_tackle_wins_possession_from_nearby_opponent();
    test_goalkeeper_save_captures_nearby_ball();
    test_goal_and_restart_are_deterministic();
    std::cout << "FOOTBALL_REFERENCE_TESTS: 21/21 GREEN\n";
}
