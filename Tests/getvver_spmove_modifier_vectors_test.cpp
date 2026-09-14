#include "../Reference/FootballPhysics/GetVVerSpmoveRuntime.h"

#include <cassert>

using namespace football::core;
using namespace football::physics::recovered;

namespace {
void AssertVector(RecoveredXVector3 value, int x, int y, int z) {
    assert(value.x.raw == x);
    assert(value.y.raw == y);
    assert(value.z.raw == z);
}
}

int main() {
    // Explicit post-eligibility inventories: these are representative runtime
    // fixtures, not a claim that every player owns these exact children.
    SpmoveInventory inventory{
        {0x3FC, {{102001, 0}, {102003, 0}}},
        {0x41A, {{105001, 0}, {105002, 0}}},
    };
    SpmoveConfigMap configs{
        {102001, {102001, 1, 0, 0, 1, std::vector<std::int32_t>{0, 0, 900}}},
        {102003, {102003, 3, 0, 0, 1, std::vector<std::int32_t>{0, 0, 700}}},
        {105001, {105001, 1, 0, 0, 1, std::vector<std::int32_t>{0, 0, 900}}},
        {105002, {105002, 2, 0, 0, 1, std::vector<std::int32_t>{0, 0, 800}}},
    };
    const SpmoveSelector selector(inventory, configs);
    const RecoveredXVector3 base{Create(-3000), Create(1537), Create(777)};

    AssertVector(ApplyGetVVerSpmoveRuntime(base, 0, selector), -3000, 1537, 777);
    AssertVector(ApplyGetVVerSpmoveRuntime(base, 1ULL << 40, selector), -2051, 1051, 531);
    AssertVector(ApplyGetVVerSpmoveRuntime(base, 1ULL, selector), -2344, 1201, 607);
    AssertVector(ApplyGetVVerSpmoveRuntime(base, (1ULL << 40) | 1ULL, selector), -1602, 821, 415);

    // The first component proves that rounding occurs after each ordered
    // multiply: pre-combining 700 and 800 would produce -1603, not -1602.
    assert(Multiply(Create(-3000), Multiply(Create(700), Create(800))).raw == -1603);

    // A missing selected list and a sub-unit vector both preserve the input.
    SpmoveConfigMap missing_config;
    const SpmoveSelector missing_selector(inventory, missing_config);
    AssertVector(ApplyGetVVerSpmoveRuntime(base, ~0ULL, missing_selector), -3000, 1537, 777);
    const RecoveredXVector3 zero{};
    AssertVector(ApplyGetVVerSpmoveRuntime(zero, ~0ULL, selector), 0, 0, 0);
    return 0;
}
