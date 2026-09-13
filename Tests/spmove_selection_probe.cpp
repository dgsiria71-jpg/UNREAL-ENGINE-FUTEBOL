#include "../Reference/FootballPhysics/SpmoveSelection.h"
#include <iostream>
#include <string>

int main() {
    using namespace football::physics::recovered;
    std::string op;
    std::int32_t query{};
    std::uint32_t no_ratio{}, show_father{};
    std::uint64_t flags{};
    RawVector3 v{};
    std::size_t buckets{};
    while (std::cin >> op >> query >> no_ratio >> show_father >> flags >> v.x >> v.y >> v.z >> buckets) {
        if (buckets > 10000) return 2;
        SpmoveInventory inventory;
        SpmoveConfigMap configs;
        for (std::size_t i=0; i<buckets; ++i) {
            std::int32_t logic{};
            std::size_t count{};
            if (!(std::cin >> logic >> count) || count > 10000) return 2;
            auto& bucket = inventory[logic];
            for (std::size_t j=0; j<count; ++j) {
                SpmoveIdCombine item;
                if (!(std::cin >> item.child_id >> item.father_id)) return 2;
                bucket.push_back(item);
            }
        }
        std::size_t records{};
        if (!(std::cin >> records) || records > 10000) return 2;
        for (std::size_t i=0; i<records; ++i) {
            SpmoveConfigRecord record;
            std::int32_t count{};
            if (!(std::cin >> record.id >> record.level >> record.order >> record.odds >> record.enabled >> count)
                || count < -1 || count > 10000) return 2;
            if (count >= 0) {
                record.runtime_parameters.emplace();
                for (std::int32_t j=0; j<count; ++j) {
                    std::int32_t raw{};
                    if (!(std::cin >> raw)) return 2;
                    record.runtime_parameters->push_back(raw);
                }
            }
            configs[record.id] = std::move(record);
        }
        const SpmoveSelector selector(inventory, configs);
        if (op == "max") {
            const auto found=inventory.find(query);
            if (found == inventory.end()) return 3;
            std::cout << MaxSpmoveId(found->second, show_father) << '\n';
        } else if (op == "config") {
            const auto* record=selector.Config(query);
            if (record) std::cout << record->id << '\n';
            else std::cout << "NULL\n";
        } else if (op == "params") {
            const auto* params=selector.Parameters(query, no_ratio);
            if (!params) std::cout << "NULL\n";
            else {
                std::cout << "P " << params->size();
                for (const auto raw:*params) std::cout << ' ' << raw;
                std::cout << '\n';
            }
        } else {
            if (op == "vhor_a" || op == "vhor_b") v=ApplyVHorWithSelector(v,flags,selector);
            else if (op == "vver_ballistic") v=ApplyVVerBallisticWithSelector(v,flags,selector);
            else if (op == "vver_head") v=ApplyVVerHeadWithSelector(v,flags,selector);
            else return 3;
            std::cout << v.x << ' ' << v.y << ' ' << v.z << '\n';
        }
    }
    return std::cin.eof() ? 0 : 2;
}
