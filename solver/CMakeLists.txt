cmake_minimum_required(VERSION 3.21)
project(engine_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(spdlog REQUIRED)
find_package(nlohmann_json REQUIRED)

# Solver logic as a library so both the CLI and the test binary can link it
# without duplicating compilation or getting a second main().
add_library(solver_lib STATIC
    src/engine_cycle.cpp
    src/atmosphere.cpp
)

target_include_directories(solver_lib PUBLIC src)

target_link_libraries(solver_lib PUBLIC
    spdlog::spdlog
    nlohmann_json::nlohmann_json
)

add_executable(solver main.cpp)
target_link_libraries(solver PRIVATE solver_lib)

# ── CTest / unit tests ────────────────────────────────────────────────────────
include(CTest)

if(BUILD_TESTING)
    find_package(Catch2 REQUIRED)
    include(Catch)

    add_executable(test_solver tests/test_solver.cpp)
    target_link_libraries(test_solver PRIVATE solver_lib Catch2::Catch2WithMain)

    catch_discover_tests(test_solver)
endif()
