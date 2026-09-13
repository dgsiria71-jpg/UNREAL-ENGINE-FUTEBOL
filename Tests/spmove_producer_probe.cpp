#include "../Reference/FootballPhysics/SpmoveProducer.h"
#include <iostream>
int main() {
    using namespace football::physics::recovered;
    SpmoveProducerContext c;
    while(std::cin >> c.goal_type >> c.first_byte >> c.disturbed_raw >> c.static_disturbed_raw
          >> c.collection15 >> c.collection32 >> c.collection16 >> c.ball_x >> c.ball_z
          >> c.center_x >> c.center_z >> c.angle_raw >> c.limit_170 >> c.limit_174
          >> c.limit_178 >> c.curve_result_raw >> c.successful_properties) {
        const auto r=ProduceSpmoveFlags(c);
        for(auto b:r.bytes)std::cout << static_cast<unsigned>(b) << ' ';
        std::cout << r.distance_raw << ' ' << r.queries << '\n';
    }
    return std::cin.eof()?0:2;
}
