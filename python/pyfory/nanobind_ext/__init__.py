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
PyFory nanobind extension module.
This module provides high-performance C++ functions using nanobind.
"""

# Try to import the compiled nanobind module
_pyfory_nb = None
try:
    # Try importing the compiled extension module directly
    from .pyfory_nb import add as _add, multiply as _multiply, create_buffer as _create_buffer, sum_buffer as _sum_buffer
    _pyfory_nb = True
except ImportError:
    # Fallback to pure Python implementations if nanobind module is not available
    _pyfory_nb = False

if _pyfory_nb:
    # Use the compiled nanobind functions
    add = _add
    multiply = _multiply
    create_buffer = _create_buffer
    sum_buffer = _sum_buffer
else:
    # Use pure Python fallback implementations
    def add(a, b):
        return a + b
    
    def multiply(a, b):
        return a * b
    
    def create_buffer(size, fill_value=0):
        return [fill_value] * size
    
    def sum_buffer(buffer):
        return sum(buffer)

__all__ = ['add', 'multiply', 'create_buffer', 'sum_buffer']
