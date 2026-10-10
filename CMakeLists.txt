cmake_minimum_required(VERSION 3.21)
project(PCBL_Framework CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Discover and link native host OpenMP multi-threading libraries
find_package(OpenMP REQUIRED)

if(MSVC)
    add_compile_options(/O2 /Oi /Arch:AVX2)
else()
    add_compile_options(-O3 -march=native -funroll-loops -ffast-math -fopenmp)
endif()

include_directories(include)

# 1. Compile standard static library core
add_library(pcbl_static STATIC 
    src/engine.cpp 
    src/encoder.cpp 
    src/checkpoint.cpp
)
target_link_libraries(pcbl_static PRIVATE OpenMP::OpenMP_CXX)

# 2. Compile dynamic shared library (.dll) for Python cross-linkage
add_library(pcbl_shared SHARED 
    src/engine.cpp 
    src/encoder.cpp 
    src/checkpoint.cpp
)
target_link_libraries(pcbl_shared PRIVATE OpenMP::OpenMP_CXX)

# 3. Compile native standalone executable 
add_executable(pcbl_runtime examples/main.cpp)
target_link_libraries(pcbl_runtime PRIVATE pcbl_static OpenMP::OpenMP_CXX)
