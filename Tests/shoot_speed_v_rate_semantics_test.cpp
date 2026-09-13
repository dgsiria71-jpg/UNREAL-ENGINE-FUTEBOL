#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/ShootSpeedVRate.h"

#include <cassert>
#include <stdexcept>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    assert(DivideRawByInt(Create(102400), 100).raw == 1024);
    assert(DivideRawByInt(Create(50), 100).raw == 1);
    assert(DivideRawByInt(Create(-50), 100).raw == -1);
    assert(DivideRawByInt(Create(123), 0).raw == 0);

    assert(XRandomRangeAtSample(Create(100), Create(1100), 0).raw == 100);
    assert(XRandomRangeAtSample(Create(100), Create(1100), 500).raw == 600);
    assert(XRandomRangeAtSample(Create(100), Create(1100), 1000).raw == 1100);

    bool rejected = false;
    try {
        (void)XRandomRangeAtSample(Create(0), Create(1), 1001);
    } catch (const std::out_of_range&) {
        rejected = true;
    }
    assert(rejected);

    // F=0 leaves base at one. Positive c ranges from one to c.
    assert(GetShootSpeedVRateAtSample(Create(999), Create(0), Create(2048), 0, 0).raw == 1024);
    assert(GetShootSpeedVRateAtSample(Create(999), Create(0), Create(2048), 0, 500).raw == 1536);
    assert(GetShootSpeedVRateAtSample(Create(999), Create(0), Create(2048), 0, 1000).raw == 2048);

    // F=50 becomes raw 512 and is applied twice. A negative shoot rate
    // produces a positive-c bound below one: 1 + (-1 * 1 * .5 * .5) = .75.
    assert(GetShootSpeedVRateAtSample(Create(-1024), Create(51200), Create(1024), 0, 0).raw == 768);

    // Negative c selects max(one, base-disArea) before interpolation to c.
    assert(GetShootSpeedVRateAtSample(Create(-512), Create(102400), Create(-1024), 100, 0).raw == 1436);
    assert(GetShootSpeedVRateAtSample(Create(-512), Create(102400), Create(-1024), 100, 500).raw == 206);
    assert(GetShootSpeedVRateAtSample(Create(-512), Create(102400), Create(-1024), 100, 1000).raw == -1024);
    return 0;
}
