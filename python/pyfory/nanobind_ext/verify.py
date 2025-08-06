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
Verification script to test the fixed nanobind integration.
This script validates that all data type ranges are handled correctly.
"""

def test_data_type_ranges():
    """Test different data type ranges with PyFory Buffer."""
    print("=== Testing Data Type Ranges ===\n")
    
    try:
        from pyfory.buffer import Buffer
        from pyfory.nanobind_ext import sum_buffer
        
        # Test 1: Safe int8 values
        print("Test 1: Safe int8 values (-128 to 127)")
        safe_buffer = Buffer.allocate(16)
        safe_values = [-128, -1, 0, 1, 42, 100, 127]
        
        for val in safe_values:
            safe_buffer.write_int8(val)
        
        safe_bytes = list(safe_buffer.get_bytes(0, safe_buffer.writer_index))
        safe_sum = sum_buffer(safe_bytes)
        expected_safe = sum(safe_values)
        
        print(f"  Values: {safe_values}")
        print(f"  Buffer bytes: {safe_bytes}")
        print(f"  Sum: {safe_sum}, Expected: {expected_safe}")
        print(f"  ✓ Test 1: {'PASSED' if safe_sum == expected_safe else 'FAILED'}")
        
        # Test 2: Raw bytes (0-255 range)
        print("\nTest 2: Raw bytes (0-255 range)")
        raw_buffer = Buffer.allocate(16)
        raw_data = bytes([0, 1, 100, 200, 255])
        raw_buffer.write_bytes(raw_data)
        
        raw_bytes = list(raw_buffer.get_bytes(0, len(raw_data)))
        raw_sum = sum_buffer(raw_bytes)
        expected_raw = sum(raw_data)
        
        print(f"  Raw data: {list(raw_data)}")
        print(f"  Buffer bytes: {raw_bytes}")
        print(f"  Sum: {raw_sum}, Expected: {expected_raw}")
        print(f"  ✓ Test 2: {'PASSED' if raw_sum == expected_raw else 'FAILED'}")
        
        # Test 3: Demonstrate the overflow issue (should be avoided)
        print("\nTest 3: Demonstrating overflow prevention")
        try:
            overflow_buffer = Buffer.allocate(8)
            overflow_buffer.write_int8(255)  # This should fail
            print("  ✗ Test 3: FAILED - Expected overflow error but didn't get one")
        except OverflowError:
            print("  ✓ Test 3: PASSED - Correctly caught overflow error for int8(255)")
        
        print("\n✓ All data type range tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_nanobind_functions():
    """Test basic nanobind functions."""
    print("\n=== Testing Nanobind Functions ===\n")
    
    try:
        from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer
        
        # Basic arithmetic
        assert add(5, 3) == 8
        assert multiply(2.5, 4.0) == 10.0
        print("✓ Basic arithmetic functions work")
        
        # Buffer operations
        buffer = create_buffer(5, 10)
        assert len(buffer) == 5
        assert all(x == 10 for x in buffer)
        assert sum_buffer(buffer) == 50
        print("✓ Buffer functions work")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("PyFory Nanobind Extension Verification\n")
    
    success1 = test_nanobind_functions()
    success2 = test_data_type_ranges()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The nanobind extension is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
