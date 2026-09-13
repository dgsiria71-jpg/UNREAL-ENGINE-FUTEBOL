cmake_minimum_required(VERSION 3.20)
project(FootballReference LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(FootballReferenceTests
    physics_reference_tests.cpp
    ../Reference/FootballCore/FixedPoint.cpp
    ../Reference/FootballSimulation/BallContact.cpp
    ../Reference/FootballSimulation/MatchSimulation.cpp
    ../Reference/FootballGameplay/PlayableMatch.cpp
)
target_include_directories(FootballReferenceTests PRIVATE ../Reference)

add_executable(RemapNativeSemanticsTest remap_native_semantics_test.cpp)
target_include_directories(RemapNativeSemanticsTest PRIVATE ../Reference)

add_executable(ShootSpeedVRateSemanticsTest shoot_speed_v_rate_semantics_test.cpp)
add_executable(ShootDisAndTimeSemanticsTest shoot_dis_and_time_semantics_test.cpp)
target_include_directories(ShootSpeedVRateSemanticsTest PRIVATE ../Reference)

add_executable(RecoveredKernelProbe recovered_kernel_probe.cpp)
add_executable(SpmoveBranchesProbe spmove_branches_probe.cpp)
if(MSVC)
    target_compile_options(FootballReferenceTests PRIVATE /UNDEBUG)
    target_compile_options(RemapNativeSemanticsTest PRIVATE /UNDEBUG)
    target_compile_options(ShootSpeedVRateSemanticsTest PRIVATE /UNDEBUG)
    target_compile_options(ShootDisAndTimeSemanticsTest PRIVATE /UNDEBUG)
else()
    target_compile_options(FootballReferenceTests PRIVATE -UNDEBUG)
    target_compile_options(RemapNativeSemanticsTest PRIVATE -UNDEBUG)
    target_compile_options(ShootSpeedVRateSemanticsTest PRIVATE -UNDEBUG)
    target_compile_options(ShootDisAndTimeSemanticsTest PRIVATE -UNDEBUG)
endif()
enable_testing()
add_test(NAME FootballReference COMMAND FootballReferenceTests)
add_test(NAME RemapNativeSemantics COMMAND RemapNativeSemanticsTest)
add_test(NAME ShootSpeedVRateSemantics COMMAND ShootSpeedVRateSemanticsTest)
add_test(NAME ShootDisAndTimeSemantics COMMAND ShootDisAndTimeSemanticsTest)

add_executable(SpmoveSelectionProbe spmove_selection_probe.cpp)

add_executable(SpmoveProducerProbe spmove_producer_probe.cpp)
target_compile_features(SpmoveProducerProbe PRIVATE cxx_std_17)
