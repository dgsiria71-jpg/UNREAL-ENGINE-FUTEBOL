#pragma once
#include "NativeVectorMath.h"
#include <optional>
#include <vector>

namespace football::physics::recovered {
// The caller supplies already-selected native property records. Level/odds/
// eligibility resolution stays outside this recovered arithmetic boundary.
struct SelectedSpmoveParameters {
    std::optional<std::vector<std::int32_t>> shoot_first; // 0x3FE
    std::optional<std::vector<std::int32_t>> long_kick;   // 0x3FC
    std::optional<std::vector<std::int32_t>> shoot_push;  // 0x41A
    std::optional<std::vector<std::int32_t>> head;        // 0x3FB
};
inline bool SpmoveByte(std::uint64_t flags, unsigned byte) noexcept {
    return ((flags >> (byte * 8)) & 0xFF) != 0;
}
inline RawVector3 ApplyVHorSpmove(RawVector3 v, std::uint64_t flags,
                                const SelectedSpmoveParameters& selected) {
    if (SpmoveByte(flags, 3) && selected.shoot_first)
        v = ApplyVHorIncrease(v, selected.shoot_first->at(0));
    if (SpmoveByte(flags, 5) && selected.long_kick)
        v = ApplyVHorIncrease(v, selected.long_kick->at(1));
    return v;
}
// The GetVVer ballistic branch applies long kick then push. The magnitude
// guard is reevaluated after long kick, so a zero vector skips the next lookup.
inline RawVector3 ApplyVVerBallisticSpmove(RawVector3 v, std::uint64_t flags,
                                         const SelectedSpmoveParameters& selected) {
    if (SpmoveByte(flags, 5) && Magnitude(v) >= 1 && selected.long_kick)
        v = ApplyVVerScale(v, selected.long_kick->at(2));
    if (SpmoveByte(flags, 0) && Magnitude(v) >= 1 && selected.shoot_push)
        v = ApplyVVerScale(v, selected.shoot_push->at(2));
    return v;
}
// A different GetVVer base branch reaches Head; do not automatically append
// this operation to the ballistic branch above.
inline RawVector3 ApplyVVerHeadSpmove(RawVector3 v, std::uint64_t flags,
                                    const SelectedSpmoveParameters& selected) {
    if (SpmoveByte(flags, 4) && Magnitude(v) >= 1 && selected.head)
        v = ApplyHeadDecrease(v, selected.head->at(2));
    return v;
}
}
