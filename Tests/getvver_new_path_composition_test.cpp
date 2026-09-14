#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/GetVVerNewPath.h"
#include "../Reference/FootballPhysics/GetVVerNewPathConfig.h"

#include <cassert>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    // Protected-energy selection: early-out current-energy branches.
    assert(SelectProtectedEnergy(Create(4000), Create(2000), Create(600), Create(1800)).raw == 2000);
    assert(SelectProtectedEnergy(Create(4000), Create(5000), Create(600), Create(1800)).raw == 5000);

    // Transitional branch: max(current-tolerance, out-protect).
    assert(SelectProtectedEnergy(Create(4000), Create(3900), Create(600), Create(1800)).raw == 3300);

    // Canonical 1-221-5 GetVVer uses XNumber.create(0, 100) as a fixed downward bias.
    assert(GetVVerDownwardBias().raw == 102);

    // Positive energy delta uses the up rate and does not consume the downward bias.
    assert(ComputePointHeightAdjustment(
        Create(5000), Create(4000), Create(512), Create(256)).raw == 500);

    // Zero/nonpositive delta uses point-down rate plus the fixed native 0.1 bias.
    assert(ComputePointHeightAdjustment(
        Create(4000), Create(4000), Create(512), Create(256)).raw == -102);
    assert(ComputePointHeightAdjustment(
        Create(3000), Create(4000), Create(512), Create(256)).raw == -352);

    // Native clamp order and final reference subtraction.
    assert(ComputeVerticalDelta(
        Create(2500), Create(500), Create(2500), Create(3500), Create(1200)).raw == 1800);
    assert(ComputeVerticalDelta(
        Create(5000), Create(500), Create(2500), Create(3500), Create(1200)).raw == 2300);

    RecoveredXVector3 direction{Create(1024), Create(512), Create(-1024)};
    RecoveredXVector3 base = BuildVerticalVector(direction, Create(2048));
    assert(base.x.raw == 2048);
    assert(base.y.raw == 1024);
    assert(base.z.raw == -2048);

    RecoveredXVector3 after_3fc = ApplyGetVVerModifier(base, Create(512));
    assert(after_3fc.x.raw == 1024);
    assert(after_3fc.y.raw == 512);
    assert(after_3fc.z.raw == -1024);

    RecoveredXVector3 after_41a = ApplyGetVVerModifier(after_3fc, Create(2048));
    assert(after_41a.x.raw == 2048);
    assert(after_41a.y.raw == 1024);
    assert(after_41a.z.raw == -2048);

    // Raw new-method maps must be paired exactly as the native GetVVer dataflow:
    // distance -> outEnergyMax/point-up/point-down,
    // current-energy -> ySpeedMax, shoot-property -> energyTolerance.
    ShootSpeedNewMethodMaps maps{
        /* shootDisMap */ {Create(1000), Create(2000)},
        /* outEnergyMaxMap */ {Create(2000), Create(4000)},
        /* energyMapNew */ {Create(1000), Create(3000)},
        /* ySpeedMax */ {Create(5000), Create(7000)},
        /* shootPointHUpMap */ {Create(100), Create(300)},
        /* shootPointHDownMap */ {Create(400), Create(800)},
        /* shootPropertyMapNew */ {Create(0), Create(1024)},
        /* energyToleranceMap */ {Create(100), Create(500)},
    };
    const ResolvedNewGetVVerMapOutputs resolved = ResolveNewGetVVerMapOutputs(
        maps, Create(1500), Create(2000), Create(512));
    assert(resolved.out_energy.raw == 3000);
    assert(resolved.y_speed_max.raw == 6000);
    assert(resolved.point_up_rate.raw == 200);
    assert(resolved.point_down_rate.raw == 600);
    assert(resolved.energy_tolerance.raw == 300);

    ShootDisAndTimeTable one_second = {
        {1000, 1000},
        {1000, 1000},
    };
    RecoveredXVector3 composed = ComposeNewGetVVerFromResolvedScalars(
        one_second,
        Create(512), Create(512),
        Create(4000), Create(5000), Create(600), Create(1800),
        Create(512), Create(256),
        Create(3000), Create(2500), Create(5000), Create(1200),
        Create(0), Create(0), Create(10000),
        RecoveredXVector3{Create(1024), Create(0), Create(0)},
        true, Create(512),
        true, Create(2048));
    assert(composed.x.raw == 2300);
    assert(composed.y.raw == 0);
    assert(composed.z.raw == 0);

    return 0;
}
