cmake_minimum_required(VERSION 3.22)
project(SowaMiddleModule VERSION 0.9)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(lib)
add_executable(main main.cpp)
target_link_libraries(main PRIVATE sowa-lib)

find_package(cpr REQUIRED)
target_link_libraries(main PRIVATE cpr::cpr)