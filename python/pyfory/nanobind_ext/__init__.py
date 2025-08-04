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

try:
    from . import pyfory_nb
except ImportError as e:
    # Fallback to pure Python implementations if nanobind module is not available
    import warnings
    warnings.warn(f"Failed to import nanobind extension: {e}. Using fallback implementations.")
    
    class _FallbackModule:
        @staticmethod
        def add(a, b):
            return a + b
        
        @staticmethod
        def multiply(a, b):
            return a * b
        
        @staticmethod
        def create_buffer(size, fill_value=0):
            return [fill_value] * size
        
        @staticmethod
        def sum_buffer(buffer):
            return sum(buffer)
    
    pyfory_nb = _FallbackModule()

# Export the functions
add = pyfory_nb.add
multiply = pyfory_nb.multiply
create_buffer = pyfory_nb.create_buffer
sum_buffer = pyfory_nb.sum_buffer

__all__ = ['add', 'multiply', 'create_buffer', 'sum_buffer']
