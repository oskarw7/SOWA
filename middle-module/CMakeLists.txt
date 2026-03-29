cmake_minimum_required(VERSION 3.15)
project(NixOsSerialCpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
add_executable(main main.cpp)
target_link_libraries(main PRIVATE Python3::Python)