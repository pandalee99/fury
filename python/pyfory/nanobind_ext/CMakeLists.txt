# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

cmake_minimum_required(VERSION 3.15...3.27)
project(pyfory_nanobind)

# Find required packages
find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

# Try to import nanobind through CMake or Python
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE NB_DIR
  RESULT_VARIABLE NB_RESULT)

if (NB_RESULT EQUAL 0)
  list(APPEND CMAKE_PREFIX_PATH "${NB_DIR}")
  find_package(nanobind CONFIG REQUIRED)
else()
  message(WARNING "nanobind not found, will not build nanobind extension")
  return()
endif()

# Create the nanobind extension
nanobind_add_module(pyfory_nb pyfory_nb.cpp)

# Set properties
target_compile_features(pyfory_nb PRIVATE cxx_std_17)

# Install the extension
install(TARGETS pyfory_nb DESTINATION .)
