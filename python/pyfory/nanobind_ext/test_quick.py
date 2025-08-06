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
Quick test script to verify nanobind extension functionality.
"""

import sys
import os

# Add the parent directory to the path so we can import pyfory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_nanobind_functions():
    """Test the nanobind extension functions."""
    print("Testing nanobind extension functions...")
    
    try:
        from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer
        print("✓ Successfully imported nanobind extension functions")
    except ImportError as e:
        print(f"✗ Failed to import nanobind extension: {e}")
        return False
    
    # Test basic functions
    try:
        result = add(2, 3)
        assert result == 5, f"Expected 5, got {result}"
        print(f"✓ add(2, 3) = {result}")
        
        result = multiply(2.5, 4.0)
        assert result == 10.0, f"Expected 10.0, got {result}"
        print(f"✓ multiply(2.5, 4.0) = {result}")
        
        buffer = create_buffer(5, 42)
        assert len(buffer) == 5, f"Expected length 5, got {len(buffer)}"
        assert all(x == 42 for x in buffer), f"Expected all values to be 42, got {buffer}"
        print(f"✓ create_buffer(5, 42) = {buffer}")
        
        total = sum_buffer(buffer)
        assert total == 210, f"Expected 210, got {total}"
        print(f"✓ sum_buffer(buffer) = {total}")
        
        print("✓ All nanobind extension tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_nanobind_functions()
    sys.exit(0 if success else 1)
