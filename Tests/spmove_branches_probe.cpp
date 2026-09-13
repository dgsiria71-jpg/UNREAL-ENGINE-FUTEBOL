#include "../Reference/FootballPhysics/SpmoveBranches.h"
#include <iostream>
#include <string>

int main() {
    using namespace football::physics::recovered;
    std::string op;
    std::uint64_t flags{};
    unsigned present{};
    RawVector3 v{};
    std::int32_t first{}, long_kick{}, push{}, head{};
    while (std::cin >> op >> flags >> present >> v.x >> v.y >> v.z >> first >> long_kick >> push >> head) {
        SelectedSpmoveParameters selected;
        if (present & 1) selected.shoot_first = std::vector<std::int32_t>{first,0,0};
        if (present & 2) selected.long_kick = std::vector<std::int32_t>{0,long_kick,long_kick};
        if (present & 4) selected.shoot_push = std::vector<std::int32_t>{0,0,push};
        if (present & 8) selected.head = std::vector<std::int32_t>{0,0,head};
        if (op == "vhor_a" || op == "vhor_b") v = ApplyVHorSpmove(v,flags,selected);
        else if (op == "vver_ballistic") v = ApplyVVerBallisticSpmove(v,flags,selected);
        else if (op == "vver_head") v = ApplyVVerHeadSpmove(v,flags,selected);
        else return 2;
        std::cout << v.x << ' ' << v.y << ' ' << v.z << '\n';
    }
    return std::cin.eof() ? 0 : 3;
}
