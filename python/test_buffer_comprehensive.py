#!/usr/bin/env python3
"""
Comprehensive test suite for nanobind Buffer implementation.

This test suite verifies:
1. Functional completeness compared to Cython implementation
2. Performance comparison between nanobind and Cython versions
3. Edge case handling and error conditions
4. Memory management and bounds checking
"""

import pytest
import time
import statistics
from typing import List, Callable
import tracemalloc

# Import both implementations for comparison
try:
    from pyfory.nanobind_ext import Buffer as NanobindBuffer
    NANOBIND_AVAILABLE = True
except ImportError:
    print("Warning: Nanobind Buffer not available, using fallback")
    NANOBIND_AVAILABLE = False

try:
    from pyfory._util import Buffer as CythonBuffer
    CYTHON_AVAILABLE = True
except ImportError:
    print("Warning: Cython Buffer not available")
    CYTHON_AVAILABLE = False


class TestFunctionalCompleteness:
    """Test functional completeness of nanobind Buffer implementation."""
    
    def setup_method(self):
        """Setup test data for each test method."""
        self.test_data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        self.large_data = bytes(range(256)) * 100  # 25.6KB test data
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_buffer_creation_and_properties(self):
        """Test buffer creation and basic properties."""
        # Test creation from bytes
        buffer = NanobindBuffer(self.test_data)
        assert buffer.size() == len(self.test_data)
        assert buffer.reader_index == 0
        assert buffer.writer_index == 0
        
        # Test creation with offset and length
        buffer_slice = NanobindBuffer(self.test_data, offset=4, length=8)
        assert buffer_slice.size() == 8
        
        # Test allocated buffer
        allocated = NanobindBuffer.allocate(1024)
        assert allocated.size() == 1024
        assert allocated.own_data() == True
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_bounds_checking(self):
        """Test bounds checking functionality."""
        buffer = NanobindBuffer(self.test_data)
        
        # Valid bounds should not raise
        buffer.check_bound(0, len(self.test_data))
        buffer.check_bound(5, 5)
        
        # Invalid bounds should raise
        with pytest.raises(Exception):  # Should be out_of_range
            buffer.check_bound(0, len(self.test_data) + 1)
        
        with pytest.raises(Exception):
            buffer.check_bound(-1, 5)
        
        with pytest.raises(Exception):
            buffer.check_bound(len(self.test_data), 1)
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_put_get_operations(self):
        """Test all put/get operations for different data types."""
        buffer = NanobindBuffer.allocate(1024)
        
        # Test boolean operations
        buffer.put_bool(0, True)
        buffer.put_bool(1, False)
        assert buffer.get_bool(0) == True
        assert buffer.get_bool(1) == False
        
        # Test 8-bit integers
        buffer.put_int8(2, 127)
        buffer.put_int8(3, -128)
        assert buffer.get_int8(2) == 127
        assert buffer.get_int8(3) == -128
        
        # Test 16-bit integers
        buffer.put_int16(4, 32767)
        buffer.put_int16(6, -32768)
        assert buffer.get_int16(4) == 32767
        assert buffer.get_int16(6) == -32768
        
        # Test 24-bit integers
        buffer.put_int24(8, 0x7FFFFF)
        buffer.put_int24(11, 0x800000)  # This should be interpreted correctly
        assert buffer.get_int24(8) == 0x7FFFFF
        
        # Test 32-bit integers
        buffer.put_int32(14, 2147483647)
        buffer.put_int32(18, -2147483648)
        assert buffer.get_int32(14) == 2147483647
        assert buffer.get_int32(18) == -2147483648
        
        # Test 64-bit integers
        buffer.put_int64(22, 9223372036854775807)
        buffer.put_int64(30, -9223372036854775808)
        assert buffer.get_int64(22) == 9223372036854775807
        assert buffer.get_int64(30) == -9223372036854775808
        
        # Test floating point
        buffer.put_float(38, 3.14159)
        buffer.put_double(42, 2.718281828459045)
        assert abs(buffer.get_float(38) - 3.14159) < 1e-6
        assert abs(buffer.get_double(42) - 2.718281828459045) < 1e-15
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_stream_operations(self):
        """Test stream-like read/write operations."""
        buffer = NanobindBuffer.allocate(1024)
        
        # Write different types in sequence
        buffer.write_bool(True)
        buffer.write_int8(42)
        buffer.write_int16(12345)
        buffer.write_int24(0x123456)
        buffer.write_int32(987654321)
        buffer.write_int64(123456789012345)
        buffer.write_float(3.14159)
        buffer.write_double(2.718281828459045)
        
        # Verify writer position advanced correctly
        expected_position = 1 + 1 + 2 + 3 + 4 + 8 + 4 + 8  # 31 bytes
        assert buffer.writer_index == expected_position
        
        # Reset reader to beginning and read back
        buffer.reader_index = 0
        assert buffer.read_bool() == True
        assert buffer.read_int8() == 42
        assert buffer.read_int16() == 12345
        assert buffer.read_int24() == 0x123456
        assert buffer.read_int32() == 987654321
        assert buffer.read_int64() == 123456789012345
        assert abs(buffer.read_float() - 3.14159) < 1e-6
        assert abs(buffer.read_double() - 2.718281828459045) < 1e-15
        
        # Verify reader position advanced correctly
        assert buffer.reader_index == expected_position
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_variable_length_integers(self):
        """Test variable-length integer encoding/decoding."""
        buffer = NanobindBuffer.allocate(1024)
        
        # Test various values that require different numbers of bytes
        test_values = [
            0, 1, 127, 128, 255, 256, 16383, 16384, 32767, 32768,
            2097151, 2097152, 268435455, 268435456, 2147483647, -1, -128, -32768
        ]
        
        # Test unsigned varints
        for value in [v for v in test_values if v >= 0]:
            buffer.writer_index = 0
            buffer.reader_index = 0
            bytes_written = buffer.write_varuint32(value)
            assert bytes_written > 0 and bytes_written <= 5
            read_value = buffer.read_varuint32()
            assert read_value == value, f"Failed for value {value}: got {read_value}"
        
        # Test signed varints (with ZigZag encoding)
        for value in test_values:
            buffer.writer_index = 0
            buffer.reader_index = 0
            bytes_written = buffer.write_varint32(value)
            assert bytes_written > 0 and bytes_written <= 5
            read_value = buffer.read_varint32()
            assert read_value == value, f"Failed for signed value {value}: got {read_value}"
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_bytes_operations(self):
        """Test byte array operations."""
        buffer = NanobindBuffer.allocate(1024)
        
        # Test bytes with size prefix
        test_bytes = b"Hello, World! This is a test string with special chars: \x00\x01\xff"
        buffer.write_bytes_and_size(test_bytes)
        
        buffer.reader_index = 0
        read_bytes = buffer.read_bytes_and_size()
        assert read_bytes == test_bytes
        
        # Test raw bytes operations
        buffer.writer_index = 0
        buffer.reader_index = 0
        buffer.write_bytes(test_bytes)
        read_bytes_raw = buffer.read_bytes(len(test_bytes))
        assert read_bytes_raw == test_bytes
        
        # Test get_bytes from specific offset
        buffer.put_int8(100, 0x42)
        buffer.put_int8(101, 0x43)
        buffer.put_int8(102, 0x44)
        retrieved = buffer.get_bytes(100, 3)
        assert retrieved == b"\x42\x43\x44"
        
        # Test read_bytes_as_int64
        buffer.writer_index = 200
        buffer.write_int64(0x0102030405060708)
        buffer.reader_index = 200
        int_value = buffer.read_bytes_as_int64(8)
        assert int_value == 0x0102030405060708
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_memory_management(self):
        """Test memory management and buffer growth."""
        buffer = NanobindBuffer.allocate(16)  # Small initial size
        
        # Write more data than initial capacity
        large_data = b"A" * 1000
        buffer.write_bytes(large_data)
        
        # Buffer should have grown automatically
        assert buffer.size() >= len(large_data)
        assert buffer.writer_index == len(large_data)
        
        # Test explicit reservation
        buffer.reserve(2048)
        assert buffer.size() >= 2048
        
        # Test ensure method
        buffer.ensure(4096)
        assert buffer.size() >= 4096


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_empty_buffer_operations(self):
        """Test operations on empty buffers."""
        empty_buffer = NanobindBuffer(b"")
        assert empty_buffer.size() == 0
        
        # Reading from empty buffer should fail
        with pytest.raises(Exception):
            empty_buffer.get_int8(0)
        
        # But allocating empty should work
        zero_alloc = NanobindBuffer.allocate(0)
        # Note: This might raise an exception depending on implementation
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_boundary_value_operations(self):
        """Test operations at data type boundaries."""
        buffer = NanobindBuffer.allocate(1024)
        
        # Test int8 boundaries
        buffer.put_int8(0, 127)   # Max positive
        buffer.put_int8(1, -128)  # Max negative
        assert buffer.get_int8(0) == 127
        assert buffer.get_int8(1) == -128
        
        # Test that overflow is handled correctly (or raises appropriate error)
        # Implementation might handle this differently
    
    @pytest.mark.skipif(not NANOBIND_AVAILABLE, reason="Nanobind not available")
    def test_large_buffer_operations(self):
        """Test operations on large buffers."""
        # Test with 1MB buffer
        large_size = 1024 * 1024
        buffer = NanobindBuffer.allocate(large_size)
        assert buffer.size() == large_size
        
        # Test writing at the end
        buffer.put_int32(large_size - 4, 0x12345678)
        assert buffer.get_int32(large_size - 4) == 0x12345678


class TestPerformanceComparison:
    """Performance comparison between nanobind and Cython implementations."""
    
    def setup_method(self):
        """Setup performance test data."""
        self.test_sizes = [1000, 10000, 100000]
        self.iterations = 1000
        self.large_data = bytes(range(256)) * 1000  # 256KB
    
    def benchmark_function(self, func: Callable, *args, iterations: int = None) -> dict:
        """Benchmark a function and return timing statistics."""
        if iterations is None:
            iterations = self.iterations
        
        times = []
        tracemalloc.start()
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std': statistics.stdev(times) if len(times) > 1 else 0,
            'total_time': sum(times),
            'memory_current': current,
            'memory_peak': peak,
            'result': result  # Store last result for verification
        }
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for comparison")
    def test_buffer_creation_performance(self):
        """Compare buffer creation performance."""
        print("\n=== Buffer Creation Performance ===")
        
        for size in self.test_sizes:
            data = bytes(range(size % 256)) * (size // 256 + 1)
            data = data[:size]  # Trim to exact size
            
            # Benchmark nanobind
            nanobind_stats = self.benchmark_function(
                lambda: NanobindBuffer(data), iterations=100
            )
            
            # Benchmark Cython
            cython_stats = self.benchmark_function(
                lambda: CythonBuffer(data), iterations=100
            )
            
            speedup = cython_stats['mean'] / nanobind_stats['mean']
            print(f"Size {size:6d}: Nanobind={nanobind_stats['mean']*1000:.2f}ms, "
                  f"Cython={cython_stats['mean']*1000:.2f}ms, Speedup={speedup:.2f}x")
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for comparison")
    def test_write_operations_performance(self):
        """Compare write operations performance."""
        print("\n=== Write Operations Performance ===")
        
        def write_sequence_nanobind():
            buffer = NanobindBuffer.allocate(10000)
            for i in range(1000):
                buffer.write_int32(i)
                buffer.write_float(i * 3.14159)
            return buffer
        
        def write_sequence_cython():
            buffer = CythonBuffer.allocate(10000)
            for i in range(1000):
                buffer.write_int32(i)
                buffer.write_float(i * 3.14159)
            return buffer
        
        nanobind_stats = self.benchmark_function(write_sequence_nanobind, iterations=100)
        cython_stats = self.benchmark_function(write_sequence_cython, iterations=100)
        
        speedup = cython_stats['mean'] / nanobind_stats['mean']
        print(f"Write ops: Nanobind={nanobind_stats['mean']*1000:.2f}ms, "
              f"Cython={cython_stats['mean']*1000:.2f}ms, Speedup={speedup:.2f}x")
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for comparison")
    def test_read_operations_performance(self):
        """Compare read operations performance."""
        print("\n=== Read Operations Performance ===")
        
        # Setup test data
        setup_buffer = NanobindBuffer.allocate(10000)
        for i in range(1000):
            setup_buffer.write_int32(i)
            setup_buffer.write_float(i * 3.14159)
        test_data = setup_buffer.get_bytes(0, setup_buffer.writer_index)
        
        def read_sequence_nanobind():
            buffer = NanobindBuffer(test_data)
            results = []
            for i in range(1000):
                int_val = buffer.read_int32()
                float_val = buffer.read_float()
                results.append((int_val, float_val))
            return results
        
        def read_sequence_cython():
            buffer = CythonBuffer(test_data)
            results = []
            for i in range(1000):
                int_val = buffer.read_int32()
                float_val = buffer.read_float()
                results.append((int_val, float_val))
            return results
        
        nanobind_stats = self.benchmark_function(read_sequence_nanobind, iterations=100)
        cython_stats = self.benchmark_function(read_sequence_cython, iterations=100)
        
        speedup = cython_stats['mean'] / nanobind_stats['mean']
        print(f"Read ops:  Nanobind={nanobind_stats['mean']*1000:.2f}ms, "
              f"Cython={cython_stats['mean']*1000:.2f}ms, Speedup={speedup:.2f}x")
        
        # Verify results are identical
        assert nanobind_stats['result'] == cython_stats['result']
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for comparison")
    def test_varint_performance(self):
        """Compare variable-length integer performance."""
        print("\n=== Varint Operations Performance ===")
        
        test_values = list(range(0, 1000000, 1000))  # 1000 diverse values
        
        def varint_write_read_nanobind():
            buffer = NanobindBuffer.allocate(10000)
            # Write all values
            for value in test_values:
                buffer.write_varint32(value)
            
            # Read all values back
            buffer.reader_index = 0
            results = []
            for _ in test_values:
                results.append(buffer.read_varint32())
            return results
        
        def varint_write_read_cython():
            buffer = CythonBuffer.allocate(10000)
            # Write all values
            for value in test_values:
                buffer.write_varint32(value)
            
            # Read all values back
            buffer.reader_index = 0
            results = []
            for _ in test_values:
                results.append(buffer.read_varint32())
            return results
        
        nanobind_stats = self.benchmark_function(varint_write_read_nanobind, iterations=50)
        cython_stats = self.benchmark_function(varint_write_read_cython, iterations=50)
        
        speedup = cython_stats['mean'] / nanobind_stats['mean']
        print(f"Varint:    Nanobind={nanobind_stats['mean']*1000:.2f}ms, "
              f"Cython={cython_stats['mean']*1000:.2f}ms, Speedup={speedup:.2f}x")
        
        # Verify results are identical
        assert nanobind_stats['result'] == cython_stats['result']
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for comparison")
    def test_bytes_operations_performance(self):
        """Compare bytes operations performance."""
        print("\n=== Bytes Operations Performance ===")
        
        test_strings = [f"Test string {i} with some content" for i in range(100)]
        test_bytes = [s.encode('utf-8') for s in test_strings]
        
        def bytes_write_read_nanobind():
            buffer = NanobindBuffer.allocate(10000)
            # Write all byte arrays
            for byte_data in test_bytes:
                buffer.write_bytes_and_size(byte_data)
            
            # Read all byte arrays back
            buffer.reader_index = 0
            results = []
            for _ in test_bytes:
                results.append(buffer.read_bytes_and_size())
            return results
        
        def bytes_write_read_cython():
            buffer = CythonBuffer.allocate(10000)
            # Write all byte arrays
            for byte_data in test_bytes:
                buffer.write_bytes_and_size(byte_data)
            
            # Read all byte arrays back
            buffer.reader_index = 0
            results = []
            for _ in test_bytes:
                results.append(buffer.read_bytes_and_size())
            return results
        
        nanobind_stats = self.benchmark_function(bytes_write_read_nanobind, iterations=100)
        cython_stats = self.benchmark_function(bytes_write_read_cython, iterations=100)
        
        speedup = cython_stats['mean'] / nanobind_stats['mean']
        print(f"Bytes ops: Nanobind={nanobind_stats['mean']*1000:.2f}ms, "
              f"Cython={cython_stats['mean']*1000:.2f}ms, Speedup={speedup:.2f}x")
        
        # Verify results are identical
        assert nanobind_stats['result'] == cython_stats['result']
    
    def test_memory_usage_comparison(self):
        """Compare memory usage patterns."""
        print("\n=== Memory Usage Comparison ===")
        
        if not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE):
            pytest.skip("Both implementations needed for comparison")
        
        # Test memory usage for large buffer operations
        large_size = 1024 * 1024  # 1MB
        
        def create_large_nanobind():
            buffer = NanobindBuffer.allocate(large_size)
            # Fill with data
            for i in range(0, large_size, 8):
                if i + 8 <= large_size:
                    buffer.put_int64(i, i)
            return buffer
        
        def create_large_cython():
            buffer = CythonBuffer.allocate(large_size)
            # Fill with data
            for i in range(0, large_size, 8):
                if i + 8 <= large_size:
                    buffer.put_int64(i, i)
            return buffer
        
        nanobind_stats = self.benchmark_function(create_large_nanobind, iterations=10)
        cython_stats = self.benchmark_function(create_large_cython, iterations=10)
        
        print(f"Memory (1MB): Nanobind peak={nanobind_stats['memory_peak']/1024/1024:.1f}MB, "
              f"Cython peak={cython_stats['memory_peak']/1024/1024:.1f}MB")


class TestCompatibility:
    """Test compatibility between nanobind and Cython implementations."""
    
    @pytest.mark.skipif(not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE), 
                       reason="Both implementations needed for compatibility test")
    def test_data_format_compatibility(self):
        """Test that data written by one implementation can be read by the other."""
        test_data = [
            (True, False),  # booleans
            (127, -128, 0),  # int8
            (32767, -32768, 0),  # int16
            (8388607, -8388608, 0),  # int24
            (2147483647, -2147483648, 0),  # int32
            (9223372036854775807, -9223372036854775808, 0),  # int64
            (3.14159, -2.71828, 0.0),  # float
            (2.718281828459045, -1.4142135623730951, 0.0),  # double
        ]
        
        # Write with nanobind, read with Cython
        nanobind_buffer = NanobindBuffer.allocate(1024)
        
        for values in test_data:
            for value in values:
                if isinstance(value, bool):
                    nanobind_buffer.write_bool(value)
                elif isinstance(value, int):
                    if -128 <= value <= 127:
                        nanobind_buffer.write_int8(value)
                    elif -32768 <= value <= 32767:
                        nanobind_buffer.write_int16(value)
                    elif -8388608 <= value <= 8388607:
                        nanobind_buffer.write_int24(value)
                    elif -2147483648 <= value <= 2147483647:
                        nanobind_buffer.write_int32(value)
                    else:
                        nanobind_buffer.write_int64(value)
                elif isinstance(value, float):
                    if abs(value) < 1e10:  # Use float for smaller values
                        nanobind_buffer.write_float(value)
                    else:
                        nanobind_buffer.write_double(value)
        
        # Get the raw data
        raw_data = nanobind_buffer.get_bytes(0, nanobind_buffer.writer_index)
        
        # Read with Cython
        cython_buffer = CythonBuffer(raw_data)
        
        for values in test_data:
            for value in values:
                if isinstance(value, bool):
                    read_value = cython_buffer.read_bool()
                    assert read_value == value
                elif isinstance(value, int):
                    if -128 <= value <= 127:
                        read_value = cython_buffer.read_int8()
                    elif -32768 <= value <= 32767:
                        read_value = cython_buffer.read_int16()
                    elif -8388608 <= value <= 8388607:
                        read_value = cython_buffer.read_int24()
                    elif -2147483648 <= value <= 2147483647:
                        read_value = cython_buffer.read_int32()
                    else:
                        read_value = cython_buffer.read_int64()
                    assert read_value == value
                elif isinstance(value, float):
                    if abs(value) < 1e10:
                        read_value = cython_buffer.read_float()
                        assert abs(read_value - value) < 1e-6
                    else:
                        read_value = cython_buffer.read_double()
                        assert abs(read_value - value) < 1e-15


def run_performance_summary():
    """Run a comprehensive performance summary."""
    if not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE):
        print("Both implementations are required for performance comparison")
        return
    
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    test_instance = TestPerformanceComparison()
    test_instance.setup_method()
    
    try:
        test_instance.test_buffer_creation_performance()
        test_instance.test_write_operations_performance()
        test_instance.test_read_operations_performance()
        test_instance.test_varint_performance()
        test_instance.test_bytes_operations_performance()
        test_instance.test_memory_usage_comparison()
    except Exception as e:
        print(f"Performance test failed: {e}")
    
    print("\n" + "="*60)
    print("If nanobind shows speedup > 1.0x, it's faster than Cython")
    print("If nanobind shows speedup < 1.0x, Cython is faster")
    print("="*60)


if __name__ == "__main__":
    # Run performance summary if called directly
    run_performance_summary()
