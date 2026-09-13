#include "../Reference/FootballPhysics/NativeVectorMath.h"
#include <cstdint>
#include <iostream>
#include <string>

int main() {
    using namespace football::core;
    using namespace football::physics::recovered;
    std::string op;
    std::int64_t a{}, b{}, x{}, y{}, z{};
    // Integer text protocol for differential tests; no JSON/engine dependency.
    while (std::cin >> op >> a >> b >> x >> y >> z) {
        const auto lhs = WrapInt32(a), rhs = WrapInt32(b);
        RawVector3 v{WrapInt32(x), WrapInt32(y), WrapInt32(z)}, result{};
        if (op == "sqrt_long") result.x = SqrtLong(a);
        else if (op == "normalize3") result = NormalizeNative(v);
        else if (op == "vhor_prepared") result = ApplyVHorIncrease(v, rhs);
        else if (op == "head_prepared") result = ApplyHeadDecrease(v, rhs);
        else if (op == "multiply") result.x = Multiply(Create(lhs), Create(rhs)).raw;
        else if (op == "divide" && rhs != 0) result.x = Divide(Create(lhs), Create(rhs)).raw;
        else if (op == "vhor_first" || op == "vhor_long") result = ApplyVHorMagnitudeIncrease(v, lhs, rhs);
        else if (op == "vver_long" || op == "vver_push") result = ApplyVVerScale(v, rhs);
        else if (op == "vver_head") result = ApplyHeadMagnitudeDecrease(v, lhs, rhs);
        else return 2;
        std::cout << result.x << ' ' << result.y << ' ' << result.z << '\n';
    }
    return std::cin.eof() ? 0 : 3;
}
