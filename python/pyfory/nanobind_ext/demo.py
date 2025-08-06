#!/usr/bin/env python3
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
PyFory Nanobind Extension Demo

This script demonstrates the usage of the nanobind extension in PyFory.
"""

import sys
import time

def demo_nanobind():
    """Demonstrate nanobind functionality."""
    print("=== PyFory Nanobind Extension Demo ===\n")
    
    try:
        from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer
        print("✓ Nanobind extension loaded successfully!")
    except ImportError as e:
        print(f"✗ Failed to load nanobind extension: {e}")
        print("  This is expected if nanobind is not installed.")
        print("  The extension will use fallback Python implementations.")
        from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer
    
    print("\n1. Basic arithmetic operations:")
    print(f"   add(10, 20) = {add(10, 20)}")
    print(f"   add(-5, 15) = {add(-5, 15)}")
    print(f"   multiply(3.14, 2.0) = {multiply(3.14, 2.0)}")
    print(f"   multiply(-1.5, 4.0) = {multiply(-1.5, 4.0)}")
    
    print("\n2. Buffer operations:")
    
    # Create small buffer
    small_buffer = create_buffer(5, 10)
    print(f"   create_buffer(5, 10) = {small_buffer}")
    print(f"   sum_buffer(small_buffer) = {sum_buffer(small_buffer)}")
    
    # Create larger buffer and time the operation
    print("\n3. Performance test with large buffer:")
    buffer_size = 1000000
    fill_value = 1
    
    start_time = time.time()
    large_buffer = create_buffer(buffer_size, fill_value)
    create_time = time.time() - start_time
    
    start_time = time.time()
    total = sum_buffer(large_buffer)
    sum_time = time.time() - start_time
    
    print(f"   Buffer size: {buffer_size:,} elements")
    print(f"   Fill value: {fill_value}")
    print(f"   Creation time: {create_time:.4f} seconds")
    print(f"   Sum time: {sum_time:.4f} seconds")
    print(f"   Total sum: {total:,}")
    print(f"   Expected sum: {buffer_size * fill_value:,}")
    print(f"   ✓ Verification: {'PASSED' if total == buffer_size * fill_value else 'FAILED'}")

def demo_integration():
    """Demonstrate integration with PyFory Buffer."""
    print("\n=== Integration with PyFory Buffer ===\n")
    
    try:
        from pyfory.buffer import Buffer
        from pyfory.nanobind_ext import sum_buffer
        
        print("Creating PyFory Buffer with test data...")
        buffer = Buffer.allocate(32)
        
        # Write some test data (using int8 compatible values)
        test_values = [1, 2, 3, 4, 5, 10, 20, 30]
        for val in test_values:
            buffer.write_int8(val)
        
        # Get the raw bytes
        raw_bytes = buffer.get_bytes(0, buffer.writer_index)
        byte_list = list(raw_bytes)
        
        print(f"PyFory buffer contents: {byte_list}")
        print(f"Sum using nanobind: {sum_buffer(byte_list)}")
        print(f"Expected sum: {sum(test_values)}")
        
        # Verify the integration works
        expected = sum(test_values)
        actual = sum_buffer(byte_list)
        print(f"✓ Integration test: {'PASSED' if actual == expected else 'FAILED'}")
        
        # Additional test with raw bytes (can handle full 0-255 range)
        print("\nTesting with raw bytes (0-255 range)...")
        raw_buffer = Buffer.allocate(32)
        test_raw_data = bytes([100, 150, 200, 255, 0, 1, 2, 3])
        raw_buffer.write_bytes(test_raw_data)
        
        raw_bytes = raw_buffer.get_bytes(0, len(test_raw_data))
        raw_byte_list = list(raw_bytes)
        
        print(f"Raw buffer contents: {raw_byte_list}")
        print(f"Sum using nanobind: {sum_buffer(raw_byte_list)}")
        print(f"Expected sum: {sum(test_raw_data)}")
        
        raw_expected = sum(test_raw_data)
        raw_actual = sum_buffer(raw_byte_list)
        print(f"✓ Raw bytes test: {'PASSED' if raw_actual == raw_expected else 'FAILED'}")
        
    except ImportError as e:
        print(f"✗ PyFory Buffer not available: {e}")

def main():
    """Main demo function."""
    demo_nanobind()
    demo_integration()
    
    print("\n=== Demo Complete ===")
    print("\nTo install nanobind for better performance:")
    print("  pip install nanobind")
    print("\nTo build the C++ extension:")
    print("  cd python/pyfory/nanobind_ext")
    print("  python setup.py build_ext --inplace")

if __name__ == "__main__":
    main()
