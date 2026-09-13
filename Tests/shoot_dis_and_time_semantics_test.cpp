#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/ShootDisAndTime.h"

#include <cassert>
#include <stdexcept>
#include <vector>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    assert(MillisecondsToSeconds(1327).raw == 1359);
    assert(MillisecondsToSeconds(2000).raw == 2048);
    assert(MillisecondsToSeconds(999).raw == 1023);

    ShootDisAndTimeTable bilinear = {
        {1000, 2000},
        {2000, 3000},
    };
    assert(SampleShootTimeRow(bilinear[0], Create(512)).raw == 1536);
    assert(LookupShootFlightTime(bilinear, Create(512), Create(512)).raw == 2048);

    ShootDisAndTimeTable zero_fallback = {
        {0, 0},
        {1000, 1000},
    };
    assert(LookupShootFlightTime(zero_fallback, Create(512), Create(512)).raw == 1024);
    assert(SampleShootTimeRow(bilinear[0], Create(2048)).raw == 0);

    ShootDisAndTimeTable canonical(21, std::vector<std::int32_t>(27, 1327));
    const XNumber flight = LookupShootFlightTime(
        canonical, Create(20 * kOne), Create(25 * kOne));
    assert(flight.raw == 1359);
    assert(SolveVerticalSpeed(flight, Create(1551), Create(-10035)).raw == 7828);
    assert(RecoverNewVVerY(
        canonical,
        Create(20 * kOne),
        Create(25 * kOne),
        Create(1551),
        Create(-10035),
        Create(0),
        Create(9216)).raw == 7828);

    assert(ClampVerticalSpeedNativeOrder(Create(10000), Create(100), Create(9000)).raw == 9000);
    assert(ClampVerticalSpeedNativeOrder(Create(-1), Create(100), Create(9000)).raw == 100);

    bool rejected = false;
    try {
        (void)LookupShootFlightTime({}, Create(0), Create(0));
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    assert(rejected);
    return 0;
}
