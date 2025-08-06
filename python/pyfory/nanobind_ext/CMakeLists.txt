cmake_minimum_required(VERSION 3.15)
project(pyfory_nb)

# 查找Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# 查找nanobind - 使用正确的方式
execute_process(
  COMMAND "${Python_EXECUTABLE}" -c "import nanobind; print(nanobind.cmake_dir())"
  OUTPUT_VARIABLE _tmp_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE)

# 添加到CMAKE_PREFIX_PATH
list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")

# 查找nanobind配置
find_package(nanobind CONFIG REQUIRED)

# 创建nanobind模块 - 使用STABLE_ABI和NB_STATIC
nanobind_add_module(
    pyfory_nb 
    STABLE_ABI 
    NB_STATIC
    pyfory_nb.cpp 
    buffer.cpp
)

# 设置C++17
target_compile_features(pyfory_nb PRIVATE cxx_std_17)

# 优化标志
target_compile_options(pyfory_nb PRIVATE 
    $<$<CONFIG:Release>:-O3>
    $<$<CONFIG:Debug>:-g>
)