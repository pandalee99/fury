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

"""
Setup script for building the nanobind extension.
This is a standalone setup for the nanobind module.
"""

import os
import sys

# Check if nanobind is available
try:
    import nanobind
    from nanobind.setup_helpers import build_ext
    # Use nanobind's extension class directly
    from nanobind import Extension as NanobindExtension
    NANOBIND_AVAILABLE = True
    print("✓ nanobind is available")
except ImportError:
    NANOBIND_AVAILABLE = False
    print("✗ nanobind not available, extension will not be built")
    print("  To install nanobind: pip install nanobind")

try:
    from setuptools import setup
except ImportError:
    print("Error: setuptools not available")
    sys.exit(1)

# Define extension modules
ext_modules = []

if NANOBIND_AVAILABLE:
    # Use nanobind to create the extension
    ext_modules = [
        NanobindExtension(
            "pyfory_nb",  # Module name (will be pyfory.nanobind_ext.pyfory_nb)
            ["pyfory_nb.cpp", "buffer.cpp"],  # Include both source files
            include_dirs=[
                nanobind.include_dir(),
                ".",  # Include current directory for buffer.h
            ],
            language="c++",
            cxx_std=17,
        ),
    ]
    print(f"✓ Configured nanobind extension: {ext_modules[0].name}")

setup(
    name="pyfory-nanobind-ext",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext} if NANOBIND_AVAILABLE else {},
    zip_safe=False,
    python_requires=">=3.8",
)
