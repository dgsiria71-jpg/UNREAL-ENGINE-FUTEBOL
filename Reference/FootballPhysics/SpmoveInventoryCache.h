#pragma once
#include "SpmoveSelection.h"
#include <cstdint>
#include <optional>
#include <vector>

namespace football::physics::recovered {

// Engine-independent cache adapter mirroring the native collector's proven
// invalidation boundary. The input snapshots are explicit because later
// eligibility/RNG semantics remain unresolved.
struct SpmoveInventorySnapshot {
    SpmoveInventory entries;
    const char* provenance{"unresolved_native_snapshot"};
};

enum class SpmoveCollectionStatus {
    Complete,
    MissingAllConfigRoot,
    MissingChildConfig,
};

struct SpmoveCollectionResult {
    SpmoveInventory entries;
    SpmoveCollectionStatus status{SpmoveCollectionStatus::Complete};
    std::int32_t missing_config_id{};

    bool complete() const noexcept {
        return status == SpmoveCollectionStatus::Complete;
    }
};

namespace detail {
inline bool ExpandSpmoveRoot(const SpmoveConfigRecord& root,
                             const SpmoveConfigMap& configs,
                             SpmoveCollectionResult& result) {
    // The native method creates the root logic bucket before expanding children.
    result.entries.try_emplace(root.logic_id);
    if (root.child_spmove_ids) {
        for (const auto child_id : *root.child_spmove_ids) {
            const auto child = configs.find(child_id);
            if (child == configs.end() || child->second.enabled == 0) {
                result.status = SpmoveCollectionStatus::MissingChildConfig;
                result.missing_config_id = child_id;
                return false;
            }
            result.entries[child->second.logic_id].push_back({child_id, root.id});
        }
    }
    // SpmoveIDCombine::.ctor zeroes fatherId; only child expansions overwrite it.
    result.entries[root.logic_id].push_back({root.id, 0});
    return true;
}
} // namespace detail

// Native open-all path enumerates configuration objects. The explicit order
// avoids claiming a stable order for managed Dictionary.Values enumeration.
inline SpmoveCollectionResult CollectAllSpmoves(
    const SpmoveConfigMap& configs,
    const std::vector<std::int32_t>& config_order) {
    SpmoveCollectionResult result;
    for (const auto config_id : config_order) {
        const auto root = configs.find(config_id);
        if (root == configs.end()) {
            result.status = SpmoveCollectionStatus::MissingAllConfigRoot;
            result.missing_config_id = config_id;
            break;
        }
        if (root->second.enabled == 0) continue;
        if (!detail::ExpandSpmoveRoot(root->second, configs, result)) break;
    }
    return result;
}

// Native player path skips missing root IDs but requires every referenced child
// configuration to resolve before the collected snapshot is considered complete.
inline SpmoveCollectionResult CollectPlayerSpmoves(
    const SpmoveConfigMap& configs,
    const std::vector<std::int32_t>& player_spmove_ids) {
    SpmoveCollectionResult result;
    for (const auto config_id : player_spmove_ids) {
        const auto root = configs.find(config_id);
        if (root == configs.end() || root->second.enabled == 0) continue;
        if (!detail::ExpandSpmoveRoot(root->second, configs, result)) break;
    }
    return result;
}

inline SpmoveCollectionResult CollectSpmovesForManager(
    bool open_all,
    std::int32_t matchrule_skill,
    const SpmoveConfigMap& configs,
    const std::vector<std::int32_t>& all_config_order,
    const std::vector<std::int32_t>& player_spmove_ids) {
    if (open_all || matchrule_skill == 1) {
        return CollectAllSpmoves(configs, all_config_order);
    }
    if (matchrule_skill == -1) {
        return CollectPlayerSpmoves(configs, player_spmove_ids);
    }
    return {};
}

class SpmoveInventoryCache {
public:
    // Returns true only when the dictionary was rebuilt. A same-state call is
    // a native-shaped cache hit and deliberately ignores a replacement source.
    bool Refresh(bool open_all, const SpmoveInventorySnapshot* source) {
        if (initialized_ && open_all_ == open_all) return false;
        entries_.clear();
        initialized_ = true;
        open_all_ = open_all;
        if (source) entries_ = source->entries;
        return true;
    }

    void Invalidate() noexcept {
        entries_.clear();
        initialized_ = false;
    }

    bool initialized() const noexcept { return initialized_; }
    bool open_all() const noexcept { return open_all_; }
    const SpmoveInventory& entries() const noexcept { return entries_; }

private:
    SpmoveInventory entries_;
    bool initialized_{false};
    bool open_all_{false};
};

} // namespace football::physics::recovered
