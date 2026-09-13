"""Emit the engine-independent contract for the first playable match.

This file is deliberately authored new-game tuning. It is a deterministic
integration contract for the future Unreal adapter and never claims to be a
recovered mobile physics equation.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Recovery" / "Normalized" / "playable_match_contract.json"


def main() -> int:
    contract = {
        "schema_version": "football.gameplay.playable_match_contract.v1",
        "engine_target": "Unreal Engine 5.x",
        "domain_runtime": "engine_independent_reference_then_unreal_adapter",
        "authority": "server_authoritative",
        "provenance": {
            "kind": "new_game_authored",
            "version": "playable_match_tuning_v0",
            "mobile_recovery_semantics": "blocked_until_physics_v0_3_gate",
        },
        "simulation": {
            "fixed_step_hz": 120,
            "fixed_step_seconds": 1.0 / 120.0,
            "render_interpolation": True,
            "simulation_quality_independent_of_render_quality": True,
            "ball_impulse_fallback": False,
        },
        "modes": [
            {"id": "3v3", "players_per_team": 3, "goalkeepers": 2},
            {"id": "5v5", "players_per_team": 5, "goalkeepers": 2},
            {"id": "11v11", "players_per_team": 11, "goalkeepers": 2},
        ],
        "actions": [
            {"id": "pass", "requires_possession": True, "emits": "authored_ball_launch"},
            {"id": "shoot", "requires_possession": True, "emits": "authored_ball_launch"},
            {"id": "dribble", "requires_possession": True, "emits": "controlled_ball"},
            {"id": "tackle", "requires_possession": False, "emits": "possession_transition"},
            {"id": "goalkeeper_save", "requires_possession": False, "emits": "goalkeeper_control"},
        ],
        "ball_states": [
            "free",
            "controlled",
            "kicked",
            "deflected",
            "goalkeeper_controlled",
            "dead_restart",
        ],
        "required_events": [
            "pass",
            "shot",
            "dribble",
            "tackle_won",
            "tackle_missed",
            "goalkeeper_save",
            "goal",
            "restart",
        ],
        "performance": {
            "target_fps": 120,
            "frame_budget_ms": 8.3333333333,
            "measurement_status": "not_measured_on_this_machine",
            "scenarios": ["3v3", "5v5", "11v11", "broadcast_camera", "player_career_camera"],
        },
        "unreal_mapping": {
            "game_mode": "AFootballGameMode",
            "player_actor": "AFootballPlayerCharacter",
            "simulation": "UFootballSimulationSubsystem",
            "ball_actor": "AFootballBallActor",
            "input": "Enhanced Input -> FFootballInputIntent -> FFootballGameplayCommand",
            "presentation": "Animation Blueprint / Pose Search / Motion Matching / IK Rig / Control Rig",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"PLAYABLE_MATCH_CONTRACT: GREEN modes=3 actions=5 output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
