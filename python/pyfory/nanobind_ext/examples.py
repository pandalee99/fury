#!/usr/bin/env python3
"""
PyFory Nanobind Buffer Usage Examples
====================================

This script demonstrates how to use the nanobind Buffer implementation
with comprehensive examples covering all major functionality.
"""

import sys
import time
import tracemalloc
from typing import List, Any

def example_basic_usage():
    """Basic Buffer creation and simple operations."""
    print("=" * 50)
    print("1. Basic Buffer Usage")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
        print("✅ Successfully imported nanobind Buffer")
    except ImportError as e:
        print(f"❌ Failed to import nanobind Buffer: {e}")
        print("   Using fallback implementation")
        return
    
    # Create buffer from bytes
    data = b'\x00\x01\x02\x03\x04\x05\x06\x07'
    buffer = Buffer(data)
    print(f"Created buffer from bytes, size: {buffer.size()}")
    
    # Allocate new buffer
    allocated = Buffer.allocate(1024)
    print(f"Allocated new buffer, size: {allocated.size()}")
    
    # Buffer with offset and length
    view = Buffer(data, offset=2, length=4)
    print(f"Created view buffer, size: {view.size()}")
    
    print()


def example_data_types():
    """Demonstrate all supported data types."""
    print("=" * 50)
    print("2. Data Type Operations")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping example")
        return
    
    buffer = Buffer.allocate(1024)
    
    # Test all data types
    test_data = [
        ("int8", 127, buffer.put_int8, buffer.get_int8, 1),
        ("int16", 32767, buffer.put_int16, buffer.get_int16, 2),
        ("int32", 2147483647, buffer.put_int32, buffer.get_int32, 4),
        ("int64", 9223372036854775807, buffer.put_int64, buffer.get_int64, 8),
        ("float", 3.14159, buffer.put_float, buffer.get_float, 4),
        ("double", 2.718281828459045, buffer.put_double, buffer.get_double, 8),
    ]
    
    offset = 0
    for type_name, value, put_func, get_func, size in test_data:
        put_func(offset, value)
        read_value = get_func(offset)
        status = "✅" if abs(read_value - value) < 1e-10 else "❌"
        print(f"{status} {type_name:6s}: wrote {value}, read {read_value}")
        offset += size
    
    print()


def example_stream_operations():
    """Demonstrate stream-like read/write operations."""
    print("=" * 50)
    print("3. Stream Operations")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping example")
        return
    
    buffer = Buffer.allocate(1024)
    
    # Write sequence
    test_values = [42, 12345, 987654321, 3.14159, 2.718281828459045]
    
    buffer.write_int8(test_values[0])
    buffer.write_int16(test_values[1])
    buffer.write_int32(test_values[2])
    buffer.write_float(test_values[3])
    buffer.write_double(test_values[4])
    
    print(f"Written {buffer.writer_index} bytes to buffer")
    
    # Read sequence
    buffer.reader_index = 0
    read_values = [
        buffer.read_int8(),
        buffer.read_int16(),
        buffer.read_int32(),
        buffer.read_float(),
        buffer.read_double()
    ]
    
    print(f"Read {buffer.reader_index} bytes from buffer")
    
    # Verify data integrity
    for i, (written, read) in enumerate(zip(test_values, read_values)):
        status = "✅" if abs(written - read) < 1e-10 else "❌"
        print(f"{status} Value {i}: {written} == {read}")
    
    print()


def example_varint_encoding():
    """Demonstrate variable-length integer encoding."""
    print("=" * 50)
    print("4. Variable-Length Integer Encoding")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping example")
        return
    
    buffer = Buffer.allocate(1024)
    
    # Test values that require different numbers of bytes
    test_values = [
        0, 1, 127, 128, 255, 256, 16383, 16384, 32767, 32768,
        2097151, 2097152, 268435455, 268435456, 2147483647,
        -1, -128, -32768
    ]
    
    print("Signed varint encoding (ZigZag):")
    for value in test_values:
        buffer.writer_index = 0
        buffer.reader_index = 0
        
        bytes_written = buffer.write_varint32(value)
        read_value = buffer.read_varint32()
        
        status = "✅" if read_value == value else "❌"
        print(f"{status} {value:>10d} -> {bytes_written} bytes -> {read_value:>10d}")
    
    print("\nUnsigned varint encoding:")
    for value in [v for v in test_values if v >= 0]:
        buffer.writer_index = 0
        buffer.reader_index = 0
        
        bytes_written = buffer.write_varuint32(value)
        read_value = buffer.read_varuint32()
        
        status = "✅" if read_value == value else "❌"
        print(f"{status} {value:>10d} -> {bytes_written} bytes -> {read_value:>10d}")
    
    print()


def example_bytes_operations():
    """Demonstrate byte array operations."""
    print("=" * 50)
    print("5. Bytes Operations")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping example")
        return
    
    buffer = Buffer.allocate(1024)
    
    # Test data with various byte values
    test_data = [
        b"Hello, World!",
        b"Binary data: \x00\x01\x02\xff\xfe\xfd",
        b"Unicode: \xe4\xb8\xad\xe6\x96\x87",  # UTF-8 中文
        b"",  # Empty bytes
        b"A" * 255,  # Large data
    ]
    
    print("Bytes with size prefix (self-describing):")
    for i, data in enumerate(test_data):
        buffer.writer_index = 0
        buffer.reader_index = 0
        
        buffer.write_bytes_and_size(data)
        read_data = buffer.read_bytes_and_size()
        
        status = "✅" if read_data == data else "❌"
        print(f"{status} Test {i}: {len(data)} bytes -> {len(read_data)} bytes")
        if len(data) <= 20:
            print(f"    Original: {data}")
            print(f"    Read:     {read_data}")
    
    print("\nRaw bytes operations:")
    buffer.writer_index = 0
    buffer.write_bytes(b"\x42\x43\x44\x45")
    
    # Get bytes from specific offset
    retrieved = buffer.get_bytes(1, 2)  # Get bytes at offset 1, length 2
    print(f"✅ Retrieved bytes [1:3]: {retrieved}")  # Should be b'\x43\x44'
    
    print()


def example_memory_management():
    """Demonstrate memory management features."""
    print("=" * 50)
    print("6. Memory Management")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping example")
        return
    
    # Start with small buffer
    buffer = Buffer.allocate(16)
    print(f"Initial buffer size: {buffer.size()}")
    
    # Write more data than initial capacity
    large_data = b"A" * 1000
    buffer.write_bytes(large_data)
    print(f"After writing 1000 bytes: {buffer.size()}")
    print(f"Writer position: {buffer.writer_index}")
    
    # Manual reservation
    buffer.reserve(2048)
    print(f"After reserve(2048): {buffer.size()}")
    
    # Ensure minimum capacity
    buffer.ensure(4096)
    print(f"After ensure(4096): {buffer.size()}")
    
    # Bounds checking
    try:
        buffer.check_bound(0, buffer.size())
        print("✅ Valid bounds check passed")
    except Exception as e:
        print(f"❌ Bounds check failed: {e}")
    
    try:
        buffer.check_bound(0, buffer.size() + 1)
        print("❌ Invalid bounds check should have failed")
    except Exception:
        print("✅ Invalid bounds check correctly failed")
    
    print()


def example_performance_comparison():
    """Compare performance with different implementations."""
    print("=" * 50)
    print("7. Performance Comparison")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer as NanobindBuffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping performance test")
        return
    
    try:
        from pyfory._util import Buffer as CythonBuffer
        cython_available = True
    except ImportError:
        print("⚠️  Cython Buffer not available, testing nanobind only")
        cython_available = False
    
    def benchmark_operations(buffer_class, iterations=10000):
        """Benchmark buffer operations."""
        buffer = buffer_class.allocate(iterations * 20)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            buffer.write_int32(i)
            buffer.write_float(i * 3.14159)
            buffer.write_varint32(i - 5000)  # Mix of positive/negative
        end_time = time.perf_counter()
        
        return end_time - start_time, buffer.writer_index
    
    iterations = 50000
    print(f"Benchmarking {iterations} operations...")
    
    # Benchmark nanobind
    nb_time, nb_bytes = benchmark_operations(NanobindBuffer, iterations)
    print(f"Nanobind: {nb_time:.3f}s, {nb_bytes} bytes written")
    
    # Benchmark Cython if available
    if cython_available:
        cy_time, cy_bytes = benchmark_operations(CythonBuffer, iterations)
        print(f"Cython:   {cy_time:.3f}s, {cy_bytes} bytes written")
        
        if cy_bytes == nb_bytes:
            speedup = cy_time / nb_time
            if speedup > 1.0:
                print(f"🚀 Nanobind is {speedup:.2f}x faster than Cython!")
            else:
                print(f"📊 Cython is {1/speedup:.2f}x faster than nanobind")
        else:
            print("⚠️  Different output sizes, cannot compare performance")
    
    print()


def example_compatibility_test():
    """Test compatibility between nanobind and Cython implementations."""
    print("=" * 50)
    print("8. Compatibility Test")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer as NanobindBuffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping compatibility test")
        return
    
    try:
        from pyfory._util import Buffer as CythonBuffer
    except ImportError:
        print("❌ Cython Buffer not available, skipping compatibility test")
        return
    
    # Write data with nanobind
    nb_buffer = NanobindBuffer.allocate(1024)
    test_values = [12345, -67890, 3.14159, 2.718281828459045]
    
    nb_buffer.write_int32(test_values[0])
    nb_buffer.write_varint32(test_values[1])
    nb_buffer.write_float(test_values[2])
    nb_buffer.write_double(test_values[3])
    nb_buffer.write_bytes_and_size(b"compatibility test")
    
    # Get raw data
    raw_data = nb_buffer.get_bytes(0, nb_buffer.writer_index)
    print(f"Nanobind wrote {len(raw_data)} bytes")
    
    # Read with Cython
    cy_buffer = CythonBuffer(raw_data)
    read_values = [
        cy_buffer.read_int32(),
        cy_buffer.read_varint32(),
        cy_buffer.read_float(),
        cy_buffer.read_double(),
        cy_buffer.read_bytes_and_size()
    ]
    
    print("Compatibility test results:")
    checks = [
        ("int32", test_values[0], read_values[0]),
        ("varint32", test_values[1], read_values[1]),
        ("float", test_values[2], read_values[2]),
        ("double", test_values[3], read_values[3]),
        ("bytes", b"compatibility test", read_values[4])
    ]
    
    all_passed = True
    for name, expected, actual in checks:
        if isinstance(expected, float):
            passed = abs(expected - actual) < 1e-10
        else:
            passed = expected == actual
        
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {expected} == {actual}")
        
        if not passed:
            all_passed = False
    
    if all_passed:
        print("🎉 All compatibility tests passed!")
    else:
        print("❌ Some compatibility tests failed")
    
    print()


def example_error_handling():
    """Demonstrate error handling and edge cases."""
    print("=" * 50)
    print("9. Error Handling")
    print("=" * 50)
    
    try:
        from pyfory.nanobind_ext import Buffer
    except ImportError:
        print("❌ Nanobind Buffer not available, skipping error handling test")
        return
    
    # Test various error conditions
    error_tests = [
        ("Invalid buffer size", lambda: Buffer.allocate(-1)),
        ("Out of bounds read", lambda: Buffer(b"test").get_int64(0)),
        ("Out of bounds write", lambda: Buffer(b"test").put_int64(0, 12345)),
        ("Invalid offset", lambda: Buffer(b"test", offset=-1)),
        ("Invalid length", lambda: Buffer(b"test", length=10)),
    ]
    
    for test_name, test_func in error_tests:
        try:
            test_func()
            print(f"❌ {test_name}: Should have raised an exception")
        except Exception as e:
            print(f"✅ {test_name}: Correctly raised {type(e).__name__}")
    
    print()


def main():
    """Run all examples."""
    print("PyFory Nanobind Buffer - Comprehensive Examples")
    print("=" * 60)
    print()
    
    # Track memory usage
    tracemalloc.start()
    
    examples = [
        example_basic_usage,
        example_data_types,
        example_stream_operations,
        example_varint_encoding,
        example_bytes_operations,
        example_memory_management,
        example_performance_comparison,
        example_compatibility_test,
        example_error_handling,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    # Show memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print("=" * 60)
    print(f"Memory usage: Current={current/1024/1024:.1f}MB, Peak={peak/1024/1024:.1f}MB")
    print("All examples completed!")


if __name__ == "__main__":
    main()
