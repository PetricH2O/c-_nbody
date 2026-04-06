cmake_minimum_required(VERSION 3.24)
project(nbody_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(PYBIND11_PYTHON_VERSION 3.9)

set(pybind11_DIR "D:/anaconda/c_nbody/Lib/site-packages/pybind11/share/cmake/pybind11")
set(PYTHON_EXECUTABLE "D:/anaconda/c_nbody/python.exe")

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(nbody_cpp
    cpp/bindings.cpp
    cpp/acceleration.cpp
    cpp/collision.cpp
)
add_custom_command(
    TARGET nbody_cpp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:nbody_cpp>
        ${CMAKE_SOURCE_DIR}
)