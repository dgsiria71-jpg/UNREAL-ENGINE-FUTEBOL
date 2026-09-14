#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/PlayerPropertySelector.h"

#include <cassert>
#include <cstdint>
#include <utility>
#include <vector>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    std::vector<std::pair<std::int32_t, std::int32_t>> calls;
    auto resolver = [&](std::int32_t property_id, std::int32_t action_id) {
        calls.emplace_back(property_id, action_id);
        switch (property_id) {
            case 15: return Create(500);
            case 16: return Create(1000);
            case 17: return Create(2000);
            case 20: return Create(3000);
            case 21: return Create(4000);
            case 22: return Create(5000);
            default: return Create(-1);
        }
    };

    PlayerPropertyInputs input{};
    input.action_id = 5811;
    assert(ResolvePlayerProperty(input, resolver).raw == 4000);
    assert(calls.back().first == 21);
    assert(calls.back().second == 5811);

    calls.clear();
    input = {};
    input.action_id = 8901;
    assert(ResolvePlayerProperty(input, resolver).raw == 5000);
    assert(calls.back().first == 22);
    assert(calls.back().second == 8901);

    calls.clear();
    input = {};
    input.action_id = 4660;
    input.in_collection = true;
    input.collection_bonus_enabled = true;
    input.collection_bonus = Create(250);
    assert(ResolvePlayerProperty(input, resolver).raw == 3250);
    assert(calls.size() == 1);
    assert(calls[0].first == 20);
    assert(calls[0].second == 4660);

    calls.clear();
    input = {};
    input.action_id = 4660;
    input.distance = Create(3500);
    input.upper_threshold = Create(3000);
    input.lower_threshold = Create(1000);
    assert(ResolvePlayerProperty(input, resolver).raw == 1000);
    assert(calls.size() == 1);
    assert(calls[0].first == 16);
    assert(calls[0].second == 4660);

    calls.clear();
    input.distance = Create(500);
    input.position_y = Create(800);
    input.position_threshold = Create(1000);
    assert(ResolvePlayerProperty(input, resolver).raw == 500);
    assert(calls.size() == 1);
    assert(calls[0].first == 15);

    calls.clear();
    input.position_y = Create(1200);
    assert(ResolvePlayerProperty(input, resolver).raw == 2000);
    assert(calls.size() == 1);
    assert(calls[0].first == 17);

    calls.clear();
    input.distance = Create(2000);
    input.upper_threshold = Create(3000);
    input.lower_threshold = Create(1000);
    input.position_y = Create(1200);
    input.position_threshold = Create(1000);
    assert(ComputePlayerPropertyBlendRatio(input.distance,
                                           input.upper_threshold,
                                           input.lower_threshold).raw == 512);
    assert(ResolvePlayerProperty(input, resolver).raw == 1500);
    assert(calls.size() == 2);
    assert(calls[0].first == 17);
    assert(calls[0].second == 4660);
    assert(calls[1].first == 16);
    assert(calls[1].second == 4660);

    assert(ComputePlayerPropertyBlendRatio(Create(3000), Create(3000), Create(1000)).raw == 0);
    assert(ComputePlayerPropertyBlendRatio(Create(2000), Create(3000), Create(3000)).raw == 0);

    return 0;
}
