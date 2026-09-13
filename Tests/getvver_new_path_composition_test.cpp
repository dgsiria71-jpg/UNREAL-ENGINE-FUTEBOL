#include "../Reference/FootballCore/FixedPoint.h"
#include "../Reference/FootballPhysics/GetVVerNewPath.h"

#include <cassert>

using namespace football::core;
using namespace football::physics::recovered;

int main() {
    // Protected-energy selection: early-out current-energy branches.
    assert(SelectProtectedEnergy(Create(4000), Create(2500), Create(600), Create(1800)).raw == 2500);
    assert(SelectProtectedEnergy(Create(4000), Create(5000), Create(600), Create(1800)).raw == 5000);

    // Transitional branch: max(current-tolerance, out-protect).
    assert(SelectProtectedEnergy(Create(4000), Create(3900), Create(600), Create(1800)).raw == 3300);

    // Positive energy delta uses the up rate.
    assert(ComputePointHeightAdjustment(
        Create(5000), Create(4000), Create(512), Create(256), 77).raw == 500);

    // Zero/nonpositive delta takes the down branch and preserves the caller-supplied random raw offset.
    assert(ComputePointHeightAdjustment(
        Create(4000), Create(4000), Create(512), Create(256), 37).raw == -37);
    assert(ComputePointHeightAdjustment(
        Create(3000), Create(4000), Create(512), Create(256), 10).raw == -260);

    // Native clamp order and final reference subtraction.
    assert(ComputeVerticalDelta(
        Create(3000), Create(500), Create(2500), Create(3500), Create(1200)).raw == 1800);
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

    return 0;
}
