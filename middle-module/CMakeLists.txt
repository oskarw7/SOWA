cmake_minimum_required(VERSION 3.23)
project(SowaMiddleModule VERSION 0.9)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(lib)
add_executable(main main.cpp)
target_link_libraries(main PRIVATE sowa-lib)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
target_link_libraries(main PRIVATE Python3::Python)