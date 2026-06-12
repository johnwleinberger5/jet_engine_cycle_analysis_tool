cmake_minimum_required(VERSION 3.21)
project(engine_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(spdlog REQUIRED)
find_package(nlohmann_json REQUIRED)

add_executable(solver
    main.cpp
    src/engine_cycle.cpp
    src/atmosphere.cpp
)

target_include_directories(solver PRIVATE src)

target_link_libraries(solver PRIVATE
    spdlog::spdlog
    nlohmann_json::nlohmann_json
)
