#pragma once
#include "SpmoveBranches.h"
#include <limits>
#include <unordered_map>

namespace football::physics::recovered {
struct SpmoveIdCombine {
    std::int32_t child_id{};
    std::int32_t father_id{};
};
struct SpmoveConfigRecord {
    std::int32_t id{}, level{}, order{}, odds{}, enabled{};
    // Runtime list is explicit: null and an initialized empty list differ.
    std::optional<std::vector<std::int32_t>> runtime_parameters;
};
using SpmoveInventory = std::unordered_map<std::int32_t, std::vector<SpmoveIdCombine>>;
using SpmoveConfigMap = std::unordered_map<std::int32_t, SpmoveConfigRecord>;

// Native 0x1B72FD4..0x1B730F8. The selector compares signed CHILD IDs,
// not config level/order/odds. Empty direct input returns the original sentinel.
inline std::int32_t MaxSpmoveId(const std::vector<SpmoveIdCombine>& candidates,
                              std::uint32_t show_father = 0) noexcept {
    auto highest = std::numeric_limits<std::int32_t>::min() + 1;
    SpmoveIdCombine selected{};
    const bool father = (show_father & 1) != 0;
    for (const auto& candidate : candidates) {
        if (candidate.child_id > highest) {
            highest = candidate.child_id;
            selected = candidate;
        } else if (father && candidate.child_id == highest && candidate.father_id >= 1) {
            selected = candidate;
        }
    }
    return father && selected.father_id > 0 ? selected.father_id : highest;
}

// The inventory is a snapshot AFTER getSpmoveIdDict has collected eligible
// children/buffs. Its construction/eligibility is not silently replaced here.
class SpmoveSelector {
public:
    SpmoveSelector(const SpmoveInventory& inventory, const SpmoveConfigMap& configs)
        : inventory_(inventory), configs_(configs) {}

    const SpmoveConfigRecord* Config(std::int32_t logic_id) const noexcept {
        const auto bucket = inventory_.find(logic_id);
        if (bucket == inventory_.end() || bucket->second.empty()) return nullptr;
        const auto found = configs_.find(MaxSpmoveId(bucket->second));
        return found == configs_.end() ? nullptr : &found->second;
    }
    const std::vector<std::int32_t>* Parameters(std::int32_t logic_id,
                                              std::uint32_t no_ratio) const noexcept {
        const auto* config = Config(logic_id); // native selection occurs first
        if (!config || (no_ratio & 1) == 0 || !config->runtime_parameters) return nullptr;
        return &*config->runtime_parameters;
    }
private:
    const SpmoveInventory& inventory_;
    const SpmoveConfigMap& configs_;
};

inline RawVector3 ApplyVHorWithSelector(RawVector3 v, std::uint64_t flags,
                                      const SpmoveSelector& selector) {
    if (SpmoveByte(flags, 3))
        if (const auto* p = selector.Parameters(0x3FE, 1)) v = ApplyVHorIncrease(v, p->at(0));
    if (SpmoveByte(flags, 5))
        if (const auto* p = selector.Parameters(0x3FC, 1)) v = ApplyVHorIncrease(v, p->at(1));
    return v;
}
inline RawVector3 ApplyVVerBallisticWithSelector(RawVector3 v, std::uint64_t flags,
                                               const SpmoveSelector& selector) {
    if (SpmoveByte(flags, 5) && Magnitude(v) >= 1)
        if (const auto* p = selector.Parameters(0x3FC, 1)) v = ApplyVVerScale(v, p->at(2));
    if (SpmoveByte(flags, 0) && Magnitude(v) >= 1)
        if (const auto* p = selector.Parameters(0x41A, 1)) v = ApplyVVerScale(v, p->at(2));
    return v;
}
inline RawVector3 ApplyVVerHeadWithSelector(RawVector3 v, std::uint64_t flags,
                                          const SpmoveSelector& selector) {
    if (SpmoveByte(flags, 4) && Magnitude(v) >= 1)
        if (const auto* p = selector.Parameters(0x3FB, 1)) v = ApplyHeadDecrease(v, p->at(2));
    return v;
}
}
