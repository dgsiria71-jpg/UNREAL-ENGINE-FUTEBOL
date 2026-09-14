#pragma once

#include "GetVVerNewPath.h"
#include "SpmoveSelection.h"

namespace football::physics::recovered {

// Adapter from the recovered GetVVer XNumber vector into the already validated
// runtime selector boundary. Inventory construction/eligibility remains an
// explicit upstream responsibility of the caller.
inline RecoveredXVector3 ApplyGetVVerSpmoveRuntime(
    RecoveredXVector3 value,
    std::uint64_t flags,
    const SpmoveSelector& selector) {
    const RawVector3 raw{value.x.raw, value.y.raw, value.z.raw};
    const RawVector3 modified = ApplyVVerBallisticWithSelector(raw, flags, selector);
    return {
        football::core::Create(modified.x),
        football::core::Create(modified.y),
        football::core::Create(modified.z),
    };
}

}  // namespace football::physics::recovered
