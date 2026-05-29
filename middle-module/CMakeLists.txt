cmake_minimum_required(VERSION 3.22)
project(SowaMiddleModule VERSION 0.9)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include(FetchContent)

FetchContent_Declare(
    cpr
    GIT_REPOSITORY https://github.com/libcpr/cpr.git
    GIT_TAG 1.10.5
)

FetchContent_MakeAvailable(cpr)

add_subdirectory(lib)

add_executable(main main.cpp)

target_link_libraries(main PRIVATE
    sowa-lib
    cpr::cpr
)