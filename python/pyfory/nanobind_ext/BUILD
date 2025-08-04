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

load("@rules_python//python:defs.bzl", "py_library")

# Python library for the nanobind extension
py_library(
    name = "nanobind_ext",
    srcs = ["__init__.py"],
    visibility = ["//python/pyfory:__subpackages__"],
    deps = [
        ":pyfory_nb_so",  # The compiled nanobind extension
    ],
)

# Note: The actual compilation of the nanobind extension would require
# additional Bazel rules for nanobind, which are not included here.
# For now, this serves as a placeholder for the Python module structure.

# If nanobind Bazel rules are available, the compilation target would look like:
# 
# nanobind_extension(
#     name = "pyfory_nb",
#     srcs = ["pyfory_nb.cpp"],
#     deps = [
#         # Additional C++ dependencies if needed
#     ],
# )

# Placeholder for the compiled extension
filegroup(
    name = "pyfory_nb_so",
    srcs = [],  # This would be populated with the actual .so file after compilation
)
