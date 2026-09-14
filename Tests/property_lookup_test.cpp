#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/PropertyLookup.h"

#include <cassert>
#include <cstdint>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    int buffer_calls = 0;
    int base_calls = 0;
    auto buffer = [&](std::int32_t property, std::int32_t buffer_id) {
        ++buffer_calls;
        assert(property == 0x10);
        assert(buffer_id == 0x2A);
        return Create(1400);
    };
    auto base = [&](std::int32_t property) {
        ++base_calls;
        assert(property == 0x10);
        return Create(900);
    };

    SpmovePropertyContext active{true, true, 0x2A};
    assert(ResolvePropertyValueWithSpmove(0x10, active, buffer, base).raw == 1400);
    assert(buffer_calls == 1 && base_calls == 0);

    SpmovePropertyContext missing{false, true, 0x2A};
    assert(ResolvePropertyValueWithSpmove(0x10, missing, buffer, base).raw == 900);
    assert(buffer_calls == 1 && base_calls == 1);

    SpmovePropertyContext rejected{true, false, 0x2A};
    assert(ResolvePropertyValueWithSpmove(0x10, rejected, buffer, base).raw == 900);
    assert(buffer_calls == 1 && base_calls == 2);

    auto positive = [](std::int32_t, std::int32_t) { return Create(250); };
    assert(ResolveShootPropertyWithSpmoveFallback(0x10, 0x3FC, positive, base).raw == 250);
    assert(base_calls == 2);

    auto zero = [](std::int32_t, std::int32_t) { return Create(0); };
    assert(ResolveShootPropertyWithSpmoveFallback(0x10, 0x3FC, zero, base).raw == 900);
    auto negative = [](std::int32_t, std::int32_t) { return Create(-1); };
    assert(ResolveShootPropertyWithSpmoveFallback(0x10, 0x3FC, negative, base).raw == 900);
    assert(base_calls == 4);
    return 0;
}
