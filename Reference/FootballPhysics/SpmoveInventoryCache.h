#pragma once
#include "SpmoveSelection.h"
#include <optional>

namespace football::physics::recovered {

// Engine-independent cache adapter mirroring the native collector's proven
// invalidation boundary. The input snapshots are explicit because the native
// upstream inventory provider and eligibility/RNG semantics remain unresolved.
struct SpmoveInventorySnapshot {
    SpmoveInventory entries;
    const char* provenance{"unresolved_native_snapshot"};
};

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

