#!/bin/bash
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

# Build script for PyFory nanobind extension

set -e

echo "=== PyFory Nanobind Extension Build Script ==="

# Check if we're in the right directory
if [ ! -f "pyfory_nb.cpp" ]; then
    echo "Error: This script must be run from the nanobind_ext directory"
    echo "Usage: cd python/pyfory/nanobind_ext && ./build.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not available"
    exit 1
fi

# Check if nanobind is installed
echo "Checking for nanobind..."
if python3 -c "import nanobind" 2>/dev/null; then
    echo "✓ nanobind is available"
else
    echo "Installing nanobind..."
    pip install nanobind
fi

# Check if setuptools is available
echo "Checking for setuptools..."
if python3 -c "import setuptools" 2>/dev/null; then
    echo "✓ setuptools is available"
else
    echo "Installing setuptools..."
    pip install setuptools wheel
fi

# Build the extension
echo "Building nanobind extension..."
python3 setup.py build_ext --inplace

# Check if the build was successful
if [ -f "pyfory_nb*.so" ] || [ -f "pyfory_nb*.pyd" ]; then
    echo "✓ Build successful!"
    echo ""
    echo "You can now test the extension by running:"
    echo "  python3 demo.py"
    echo ""
    echo "Or run the tests:"
    echo "  cd .. && python3 -m pytest tests/test_buffer.py::test_nanobind_extension -v"
else
    echo "✗ Build failed - extension module not found"
    exit 1
fi
