cmake_minimum_required(VERSION 3.15)
project(pyfory_nb)

# 查找Python和nanobind
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# 找到nanobind的CMake配置
execute_process(
  COMMAND "${Python_EXECUTABLE}" -c "import nanobind; print(nanobind.cmake_dir())"
  OUTPUT_VARIABLE _tmp_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE)
list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
find_package(nanobind CONFIG REQUIRED)

# 创建nanobind模块
nanobind_add_module(pyfory_nb pyfory_nb.cpp buffer.cpp)

# 设置C++17标准
target_compile_features(pyfory_nb PRIVATE cxx_std_17)

# 优化选项
target_compile_options(pyfory_nb PRIVATE -O3)