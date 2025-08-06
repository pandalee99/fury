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

from pyfory.buffer import Buffer
from pyfory.tests.core import require_pyarrow
from pyfory.util import lazy_import

# Import nanobind extension for testing
try:
    from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer
    NANOBIND_AVAILABLE = True
except ImportError:
    NANOBIND_AVAILABLE = False

pa = lazy_import("pyarrow")


def test_buffer():
    buffer = Buffer.allocate(8)
    buffer.write_bool(True)
    buffer.write_int8(-1)
    buffer.write_int8(2**7 - 1)
    buffer.write_int8(-(2**7))
    buffer.write_int16(2**15 - 1)
    buffer.write_int16(-(2**15))
    buffer.write_int32(2**31 - 1)
    buffer.write_int32(-(2**31))
    buffer.write_int64(2**63 - 1)
    buffer.write_int64(-(2**63))
    buffer.write_float(1.0)
    buffer.write_float(-1.0)
    buffer.write_double(1.0)
    buffer.write_double(-1.0)
    buffer.write_bytes(b"")  # write empty buffer
    buffer.write_buffer(b"")  # write empty buffer
    binary = b"b" * 100
    buffer.write_bytes(binary)
    buffer.write_bytes_and_size(binary)
    print(f"buffer size {buffer.size()}, writer_index {buffer.writer_index}")
    new_buffer = Buffer(buffer.get_bytes(0, buffer.writer_index))
    assert new_buffer.read_bool() is True
    assert new_buffer.read_int8() == -1
    assert new_buffer.read_int8() == 2**7 - 1
    assert new_buffer.read_int8() == -(2**7)
    assert new_buffer.read_int16() == 2**15 - 1
    assert new_buffer.read_int16() == -(2**15)
    assert new_buffer.read_int32() == 2**31 - 1
    assert new_buffer.read_int32() == -(2**31)
    assert new_buffer.read_int64() == 2**63 - 1
    assert new_buffer.read_int64() == -(2**63)
    assert new_buffer.read_float() == 1.0
    assert new_buffer.read_float() == -1.0
    assert new_buffer.read_double() == 1.0
    assert new_buffer.read_double() == -1.0
    assert new_buffer.read_bytes(0) == b""
    assert new_buffer.read_bytes(0) == b""
    assert new_buffer.read_bytes(len(binary)) == binary
    assert new_buffer.read_bytes_and_size() == binary
    assert new_buffer.hex() == new_buffer.to_pybytes().hex()
    assert new_buffer[:10].to_pybytes() == new_buffer.to_pybytes()[:10]
    assert new_buffer[5:30].to_pybytes() == new_buffer.to_pybytes()[5:30]
    assert new_buffer[-30:].to_pybytes() == new_buffer.to_pybytes()[-30:]
    for i in range(len(new_buffer)):
        assert new_buffer[i] == new_buffer.to_pybytes()[i]
        assert new_buffer[-i + 1] == new_buffer.to_pybytes()[-i + 1]


def test_empty_buffer():
    writable_buffer = Buffer.allocate(8)
    for buffer in [
        Buffer.allocate(0),
        Buffer(b""),
        Buffer.allocate(8).slice(8),
        Buffer(b"1").slice(1),
    ]:
        assert buffer.to_bytes() == b""
        assert buffer.to_pybytes() == b""
        assert buffer.slice().to_bytes() == b""
        assert buffer.hex() == ""
        writable_buffer.put_int32(0, 10)
        writable_buffer.put_buffer(0, buffer, 0, 0)
        writable_buffer.write_buffer(buffer)
        assert writable_buffer.get_int32(0) == 10


def test_write_varint32():
    buf = Buffer.allocate(32)
    for i in range(1):
        for j in range(i):
            buf.write_int8(1)
            buf.read_int8()
        check_varuint32(buf, 1, 1)
        check_varuint32(buf, 1 << 6, 1)
        check_varuint32(buf, 1 << 7, 2)
        check_varuint32(buf, 1 << 13, 2)
        check_varuint32(buf, 1 << 14, 3)
        check_varuint32(buf, 1 << 20, 3)
        check_varuint32(buf, 1 << 21, 4)
        check_varuint32(buf, 1 << 27, 4)
        check_varuint32(buf, 1 << 28, 5)
        check_varuint32(buf, 1 << 30, 5)

        check_varint32(buf, -1)
        check_varint32(buf, -1 << 6)
        check_varint32(buf, -1 << 7)
        check_varint32(buf, -1 << 13)
        check_varint32(buf, -1 << 14)
        check_varint32(buf, -1 << 20)
        check_varint32(buf, -1 << 21)
        check_varint32(buf, -1 << 27)
        check_varint32(buf, -1 << 28)
        check_varint32(buf, -1 << 30)


def check_varuint32(buf: Buffer, value: int, bytes_written: int):
    assert buf.writer_index == buf.reader_index
    actual_bytes_written = buf.write_varuint32(value)
    assert actual_bytes_written == bytes_written
    varint = buf.read_varuint32()
    assert buf.writer_index == buf.reader_index
    assert value == varint


def check_varint32(buf: Buffer, value: int):
    assert buf.writer_index == buf.reader_index
    buf.write_varint32(value)
    varint = buf.read_varint32()
    assert buf.writer_index == buf.reader_index
    assert value == varint


@require_pyarrow
def test_buffer_protocol():
    buffer = Buffer.allocate(32)
    binary = b"b" * 100
    buffer.write_bytes_and_size(binary)
    assert bytes(buffer) == bytes(pa.py_buffer(buffer))
    assert buffer.to_bytes() == bytes(pa.py_buffer(buffer))


def test_grow():
    binary = b"a" * 10
    buffer = Buffer(binary)
    assert not buffer.own_data()
    buffer.write_bytes(binary)
    assert not buffer.own_data()
    buffer.write_bytes(binary)
    assert buffer.own_data()


def test_write_varuint64():
    buf = Buffer.allocate(32)
    check_varuint64(buf, -1, 9)
    for i in range(32):
        for j in range(i):
            buf.write_int8(1)
            buf.read_int8()
        check_varuint64(buf, -1, 9)
        check_varuint64(buf, 1, 1)
        check_varuint64(buf, 1 << 6, 1)
        check_varuint64(buf, 1 << 7, 2)
        check_varuint64(buf, -(2**6), 9)
        check_varuint64(buf, -(2**7), 9)
        check_varuint64(buf, 1 << 13, 2)
        check_varuint64(buf, 1 << 14, 3)
        check_varuint64(buf, -(2**13), 9)
        check_varuint64(buf, -(2**14), 9)
        check_varuint64(buf, 1 << 20, 3)
        check_varuint64(buf, 1 << 21, 4)
        check_varuint64(buf, -(2**20), 9)
        check_varuint64(buf, -(2**21), 9)
        check_varuint64(buf, 1 << 27, 4)
        check_varuint64(buf, 1 << 28, 5)
        check_varuint64(buf, -(2**27), 9)
        check_varuint64(buf, -(2**28), 9)
        check_varuint64(buf, 1 << 30, 5)
        check_varuint64(buf, -(2**30), 9)
        check_varuint64(buf, 1 << 31, 5)
        check_varuint64(buf, -(2**31), 9)
        check_varuint64(buf, 1 << 32, 5)
        check_varuint64(buf, -(2**32), 9)
        check_varuint64(buf, 1 << 34, 5)
        check_varuint64(buf, -(2**34), 9)
        check_varuint64(buf, 1 << 35, 6)
        check_varuint64(buf, -(2**35), 9)
        check_varuint64(buf, 1 << 41, 6)
        check_varuint64(buf, -(2**41), 9)
        check_varuint64(buf, 1 << 42, 7)
        check_varuint64(buf, -(2**42), 9)
        check_varuint64(buf, 1 << 48, 7)
        check_varuint64(buf, -(2**48), 9)
        check_varuint64(buf, 1 << 49, 8)
        check_varuint64(buf, -(2**49), 9)
        check_varuint64(buf, 1 << 55, 8)
        check_varuint64(buf, -(2**55), 9)
        check_varuint64(buf, 1 << 56, 9)
        check_varuint64(buf, -(2**56), 9)
        check_varuint64(buf, 1 << 62, 9)
        check_varuint64(buf, -(2**62), 9)
        check_varuint64(buf, 1 << 63 - 1, 9)
        check_varuint64(buf, -(2**63), 9)


def check_varuint64(buf: Buffer, value: int, bytes_written: int):
    reader_index = buf.reader_index
    assert buf.writer_index == buf.reader_index
    actual_bytes_written = buf.write_varuint64(value)
    assert actual_bytes_written == bytes_written
    varint = buf.read_varuint64()
    assert buf.writer_index == buf.reader_index
    assert value == varint
    # test slow read branch in `read_varint64`
    assert (
        buf.slice(reader_index, buf.reader_index - reader_index).read_varuint64()
        == value
    )


def test_write_buffer():
    buf = Buffer.allocate(32)
    buf.write(b"")
    buf.write(b"123")
    buf.write(Buffer.allocate(32))
    assert buf.writer_index == 35
    assert buf.read(0) == b""
    assert buf.read(3) == b"123"


def test_read_bytes_as_int64():
    # test small buffer whose length < 8
    buf = Buffer(b"1234")
    assert buf.read_bytes_as_int64(0) == 0
    assert buf.read_bytes_as_int64(1) == 49

    # test big buffer whose length > 8
    buf = Buffer(b"12345678901234")
    assert buf.read_bytes_as_int64(0) == 0
    assert buf.read_bytes_as_int64(1) == 49
    assert buf.read_bytes_as_int64(8) == 4123106164818064178

    # test fix for `OverflowError: Python int too large to convert to C long`
    buf = Buffer(b"\xa6IOr\x9ch)\x80\x12\x02")
    buf.read_bytes_as_int64(8)


def test_nanobind_extension():
    """Test nanobind extension module functionality."""
    if not NANOBIND_AVAILABLE:
        print("Nanobind extension not available, skipping tests")
        return
    
    # Test basic arithmetic functions
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    
    # Test floating point multiplication
    assert multiply(2.5, 4.0) == 10.0
    assert multiply(-1.5, 2.0) == -3.0
    assert multiply(0.0, 100.0) == 0.0
    
    # Test buffer operations
    buffer = create_buffer(10, 42)
    assert len(buffer) == 10
    assert all(val == 42 for val in buffer)
    
    # Test sum_buffer
    assert sum_buffer(buffer) == 420  # 10 * 42
    
    # Test with empty buffer
    empty_buffer = create_buffer(0)
    assert len(empty_buffer) == 0
    assert sum_buffer(empty_buffer) == 0
    
    # Test with different values
    varied_buffer = create_buffer(5, 1)
    assert sum_buffer(varied_buffer) == 5
    
    print("All nanobind extension tests passed!")


def test_nanobind_with_fury_buffer():
    """Test integration between nanobind extension and Fury Buffer."""
    if not NANOBIND_AVAILABLE:
        print("Nanobind extension not available, skipping integration tests")
        return
    
    # Create a Fury buffer
    fury_buffer = Buffer.allocate(16)
    fury_buffer.write_int32(10)
    fury_buffer.write_int32(20)
    fury_buffer.write_int32(30)
    fury_buffer.write_int32(40)
    
    # Get bytes from fury buffer
    buffer_bytes = fury_buffer.get_bytes(0, fury_buffer.writer_index)
    
    # Convert to list for nanobind processing
    byte_list = list(buffer_bytes)
    
    # Use nanobind to sum the bytes
    total = sum_buffer(byte_list)
    print(f"Buffer bytes sum: {total}")
    
    # Test creating a buffer with nanobind and comparing with Fury operations
    # Use smaller values that fit in int8 range (-128 to 127)
    test_value = 42
    nb_buffer = create_buffer(8, test_value)
    fury_test_buffer = Buffer.allocate(8)
    for _ in range(8):
        fury_test_buffer.write_int8(test_value)
    
    fury_bytes = list(fury_test_buffer.get_bytes(0, fury_test_buffer.writer_index))
    
    # Both should have the same content
    assert nb_buffer == fury_bytes
    assert sum_buffer(nb_buffer) == sum_buffer(fury_bytes)
    
    # Additional test with raw bytes (can handle 0-255 range)
    raw_test_data = bytes([1, 2, 3, 4, 255, 254, 253, 252])
    fury_raw_buffer = Buffer.allocate(16)
    fury_raw_buffer.write_bytes(raw_test_data)
    
    raw_bytes = list(fury_raw_buffer.get_bytes(0, len(raw_test_data)))
    raw_sum = sum_buffer(raw_bytes)
    expected_sum = sum(raw_test_data)
    
    assert raw_sum == expected_sum
    print(f"Raw bytes test: sum={raw_sum}, expected={expected_sum}")
    
    print("Nanobind-Fury Buffer integration tests passed!")


if __name__ == "__main__":
    test_grow()
    test_nanobind_extension()
    test_nanobind_with_fury_buffer()
