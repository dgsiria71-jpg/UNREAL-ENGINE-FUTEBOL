#include "../Reference/FootballCore/FixedPoint.h"

#include <cassert>

using namespace football::core;

int main() {
    // Native helper 0x126BF1C returns outMin immediately when inMin == inMax.
    // The historical host helper divided by zero instead.
    assert(RemapClamped(Create(123), Create(500), Create(500), Create(700), Create(900)).raw == 700);
    return 0;
}
