#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/ShootRemap.h"

#include <cassert>
#include <stdexcept>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    // Preserve the older generic helper and its existing evidence boundary.
    bool generic_guarded = false;
    try {
        (void)RemapClamped(Create(123), Create(500), Create(500), Create(700), Create(900));
    } catch (const std::domain_error&) {
        generic_guarded = true;
    }
    assert(generic_guarded);

    // Native shoot helper 0x126BF1C returns outMin when inMin == inMax.
    assert(ShootRemapClamped(Create(123), Create(500), Create(500), Create(700), Create(900)).raw == 700);

    // Normal source clamp and 10-bit fixed interpolation remain recovered behavior.
    assert(ShootRemapClamped(Create(-50), Create(0), Create(1024), Create(100), Create(2100)).raw == 100);
    assert(ShootRemapClamped(Create(2048), Create(0), Create(1024), Create(100), Create(2100)).raw == 2100);
    assert(ShootRemapClamped(Create(512), Create(0), Create(1024), Create(100), Create(2100)).raw == 1100);
    return 0;
}
