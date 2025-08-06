// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

/**
 * @file pyfory_nb.cpp
 * @brief Nanobind implementation of PyFory Buffer class
 * 
 * This file provides a high-performance Python Buffer implementation using nanobind,
 * designed to match the functionality of the Cython-based Buffer in _util.pyx.
 * The Buffer class supports efficient binary data manipulation, serialization,
 * and various data type operations with optimal performance characteristics.
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/optional.h>
#include <nanobind/ndarray.h>
#include "buffer.h"
#include <memory>
#include <string>
#include <vector>
#include <stdexcept>

namespace nb = nanobind;
using namespace nb::literals;

/**
 * @class PyBuffer
 * @brief Python Buffer wrapper class that mirrors the Cython implementation
 * 
 * This class provides a complete implementation of buffer operations including:
 * - Memory management and allocation
 * - Type-safe put/get operations for primitive types
 * - Variable-length integer encoding/decoding
 * - Stream-like read/write operations with position tracking
 * - Buffer growth and bounds checking
 */
class PyBuffer {
public:
    /**
     * @brief Constructor for PyBuffer
     * @param data Binary data as Python bytes object
     * @param offset Starting offset within the data (default: 0)
     * @param length Length of the buffer view (default: entire remaining data)
     */
    PyBuffer(nb::bytes data, int32_t offset = 0, std::optional<int32_t> length = std::nullopt) {
        // Extract bytes data properly using nanobind API
        nb::str data_str = nb::cast<nb::str>(data);
        std::string cpp_str = nb::cast<std::string>(data_str);
        int32_t data_size = static_cast<int32_t>(cpp_str.size());
        
        // Calculate actual length for the buffer view
        int32_t actual_length = length.has_value() ? length.value() : (data_size - offset);
        
        // Validate bounds to prevent buffer overflows
        if (offset < 0 || offset + actual_length > data_size) {
            throw std::invalid_argument(
                "Wrong offset " + std::to_string(offset) + 
                " or length " + std::to_string(actual_length) + 
                " for buffer with size " + std::to_string(data_size)
            );
        }
        
        // Copy data and create underlying C++ buffer
        buffer_data_ = std::vector<uint8_t>(cpp_str.begin() + offset, cpp_str.begin() + offset + actual_length);
        buffer_ = std::make_shared<pyfory_nb::Buffer>(buffer_data_.data(), actual_length, false);
        
        // Initialize stream positions for read/write operations
        reader_index = 0;
        writer_index = 0;
    }

    /**
     * @brief Factory method to create an allocated buffer
     * @param size Size of the buffer to allocate in bytes
     * @return Shared pointer to newly allocated PyBuffer
     */
    static std::shared_ptr<PyBuffer> allocate(int32_t size) {
        if (size <= 0) {
            throw std::invalid_argument("Buffer size must be positive");
        }
        
        auto buffer = std::make_shared<PyBuffer>();
        buffer->buffer_data_ = std::vector<uint8_t>(size, 0);
        buffer->buffer_ = std::make_shared<pyfory_nb::Buffer>(buffer->buffer_data_.data(), size, false);
        buffer->reader_index = 0;
        buffer->writer_index = 0;
        return buffer;
    }

    /**
     * @brief Get the total size of the buffer
     * @return Size in bytes
     */
    int32_t size() const {
        return buffer_->size();
    }

    /**
     * @brief Check if this buffer owns its data
     * @return True if buffer manages its own memory
     */
    bool own_data() const {
        return !buffer_data_.empty();
    }

    // ========== Bounds Checking ==========
    
    /**
     * @brief Check if the specified range is within buffer bounds
     * @param offset Starting offset
     * @param length Length of the range
     * @throws std::out_of_range if access would exceed buffer bounds
     */
    void check_bound(int32_t offset, int32_t length) const {
        int32_t buffer_size = buffer_->size();
        // Use bitwise OR trick for efficient bounds checking (matches Cython implementation)
        if (offset | length | (offset + length) | (buffer_size - (offset + length)) < 0) {
            throw std::out_of_range(
                "Address range [" + std::to_string(offset) + ", " + 
                std::to_string(offset + length) + ") out of bound [0, " + 
                std::to_string(buffer_size) + ")"
            );
        }
    }

    // ========== Memory Management ==========
    
    /**
     * @brief Reserve space for buffer growth
     * @param new_size New minimum size for the buffer
     */
    void reserve(int32_t new_size) {
        if (new_size <= 0 || new_size >= (1LL << 31)) {
            throw std::invalid_argument("Invalid buffer size");
        }
        
        if (new_size > static_cast<int32_t>(buffer_data_.size())) {
            buffer_data_.resize(new_size, 0);
            buffer_ = std::make_shared<pyfory_nb::Buffer>(buffer_data_.data(), new_size, false);
        }
    }

    /**
     * @brief Ensure buffer has enough space for additional data
     * @param needed_size Additional bytes needed beyond current writer position
     */
    void grow(int32_t needed_size) {
        int32_t required_size = writer_index + needed_size;
        if (required_size > buffer_->size()) {
            reserve(required_size * 2);  // Double the size for amortized O(1) growth
        }
    }

    // ========== Direct Put Operations ==========
    
    void put_int8(uint32_t offset, int8_t value) {
        check_bound(offset, 1);
        buffer_->UnsafePutByte(offset, value);
    }

    void put_int16(uint32_t offset, int16_t value) {
        check_bound(offset, 2);
        buffer_->UnsafePut(offset, value);
    }

    void put_int32(uint32_t offset, int32_t value) {
        check_bound(offset, 4);
        buffer_->UnsafePut(offset, value);
    }

    void put_int64(uint32_t offset, int64_t value) {
        check_bound(offset, 8);
        buffer_->UnsafePut(offset, value);
    }

    void put_float(uint32_t offset, float value) {
        check_bound(offset, 4);
        buffer_->UnsafePut(offset, value);
    }

    void put_double(uint32_t offset, double value) {
        check_bound(offset, 8);
        buffer_->UnsafePut(offset, value);
    }

    // ========== Direct Get Operations ==========
    
    int8_t get_int8(uint32_t offset) const {
        check_bound(offset, 1);
        return buffer_->GetInt8(offset);
    }

    int16_t get_int16(uint32_t offset) const {
        check_bound(offset, 2);
        return buffer_->GetInt16(offset);
    }

    int32_t get_int32(uint32_t offset) const {
        check_bound(offset, 4);
        return buffer_->GetInt32(offset);
    }

    int64_t get_int64(uint32_t offset) const {
        check_bound(offset, 8);
        return buffer_->GetInt64(offset);
    }

    float get_float(uint32_t offset) const {
        check_bound(offset, 4);
        return buffer_->GetFloat(offset);
    }

    double get_double(uint32_t offset) const {
        check_bound(offset, 8);
        return buffer_->GetDouble(offset);
    }

    // ========== Stream Write Operations ==========
    
    void write_int8(int8_t value) {
        grow(1);
        buffer_->UnsafePutByte(writer_index, value);
        writer_index += 1;
    }

    void write_int16(int16_t value) {
        grow(2);
        buffer_->UnsafePut(writer_index, value);
        writer_index += 2;
    }

    void write_int32(int32_t value) {
        grow(4);
        buffer_->UnsafePut(writer_index, value);
        writer_index += 4;
    }

    void write_int64(int64_t value) {
        grow(8);
        buffer_->UnsafePut(writer_index, value);
        writer_index += 8;
    }

    void write_float(float value) {
        grow(4);
        buffer_->UnsafePut(writer_index, value);
        writer_index += 4;
    }

    void write_double(double value) {
        grow(8);
        buffer_->UnsafePut(writer_index, value);
        writer_index += 8;
    }

    // ========== Stream Read Operations ==========
    
    int8_t read_int8() {
        check_bound(reader_index, 1);
        int8_t value = buffer_->GetInt8(reader_index);
        reader_index += 1;
        return value;
    }

    int16_t read_int16() {
        int16_t value = get_int16(reader_index);
        reader_index += 2;
        return value;
    }

    int32_t read_int32() {
        int32_t value = get_int32(reader_index);
        reader_index += 4;
        return value;
    }

    int64_t read_int64() {
        int64_t value = get_int64(reader_index);
        reader_index += 8;
        return value;
    }

    float read_float() {
        float value = get_float(reader_index);
        reader_index += 4;
        return value;
    }

    double read_double() {
        double value = get_double(reader_index);
        reader_index += 8;
        return value;
    }

    // ========== Variable-Length Integer Operations ==========
    
    int32_t write_varint32(int32_t value) {
        // ZigZag encoding: maps signed to unsigned efficiently
        return write_varuint32((value << 1) ^ (value >> 31));
    }

    int32_t write_varuint32(int32_t value) {
        grow(5);  // Maximum 5 bytes for 32-bit varint
        int32_t bytes_written = buffer_->PutVarUint32(writer_index, value);
        writer_index += bytes_written;
        return bytes_written;
    }

    int32_t read_varint32() {
        uint32_t v = read_varuint32();
        return (v >> 1) ^ -(v & 1);  // ZigZag decoding
    }

    int32_t read_varuint32() {
        uint32_t read_length = 0;
        
        // Fast path: enough bytes remaining for complete varint
        if (buffer_->size() - reader_index > 5) {
            int32_t result = buffer_->GetVarUint32(reader_index, &read_length);
            reader_index += read_length;
            return result;
        } else {
            // Slow path: manual byte-by-byte reading near buffer end
            int8_t b = read_int8();
            int32_t result = b & 0x7F;
            if ((b & 0x80) != 0) {
                b = read_int8();
                result |= (b & 0x7F) << 7;
                if ((b & 0x80) != 0) {
                    b = read_int8();
                    result |= (b & 0x7F) << 14;
                    if ((b & 0x80) != 0) {
                        b = read_int8();
                        result |= (b & 0x7F) << 21;
                        if ((b & 0x80) != 0) {
                            b = read_int8();
                            result |= (b & 0x7F) << 28;
                        }
                    }
                }
            }
            return result;
        }
    }

    // ========== Byte Array Operations ==========
    
    void write_bytes_and_size(nb::bytes value) {
        nb::str data_str = nb::cast<nb::str>(value);
        std::string cpp_str = nb::cast<std::string>(data_str);
        int32_t length = static_cast<int32_t>(cpp_str.size());
        write_varuint32(length);
        if (length > 0) {
            grow(length);
            buffer_->CopyFrom(writer_index, 
                             reinterpret_cast<const uint8_t*>(cpp_str.data()), 
                             0, length);
            writer_index += length;
        }
    }

    nb::bytes read_bytes_and_size() {
        int32_t length = read_varuint32();
        nb::bytes value = get_bytes(reader_index, length);
        reader_index += length;
        return value;
    }

    nb::bytes get_bytes(uint32_t offset, uint32_t nbytes) const {
        if (nbytes == 0) {
            return nb::bytes("");
        }
        check_bound(offset, nbytes);
        const uint8_t* data = buffer_->data() + offset;
        return nb::bytes(reinterpret_cast<const char*>(data), nbytes);
    }

    // ========== Simple arithmetic functions (for testing) ==========
    
    static int add(int a, int b) {
        return a + b;
    }

    static int multiply(int a, int b) {
        return a * b;
    }

    // ========== Public member variables ==========
    
    int32_t reader_index;  ///< Current read position in the buffer
    int32_t writer_index;  ///< Current write position in the buffer

public:
    /**
     * @brief Default constructor for factory methods
     */
    PyBuffer() : reader_index(0), writer_index(0) {}

private:

    std::shared_ptr<pyfory_nb::Buffer> buffer_;  ///< Underlying C++ buffer
    std::vector<uint8_t> buffer_data_;           ///< Managed buffer data (if owned)
};

// ========== Factory Functions ==========

std::vector<int> create_buffer(int size, int fill_value = 0) {
    return std::vector<int>(size, fill_value);
}

int sum_buffer(const std::vector<int>& buffer) {
    int sum = 0;
    for (int val : buffer) {
        sum += val;
    }
    return sum;
}

// ========== Nanobind Module Definition ==========

NB_MODULE(pyfory_nb, m) {
    m.doc() = "PyFory nanobind extension - High-performance buffer operations";

    // Simple utility functions for testing nanobind integration
    m.def("add", &PyBuffer::add, "Add two integers");
    m.def("multiply", &PyBuffer::multiply, "Multiply two integers");
    m.def("create_buffer", &create_buffer, "Create a buffer", 
          "size"_a, "fill_value"_a = 0);
    m.def("sum_buffer", &sum_buffer, "Sum all elements in buffer");

    // Main Buffer class with comprehensive functionality
    nb::class_<PyBuffer>(m, "Buffer", 
        "High-performance buffer for binary data manipulation and serialization")
        
        // Constructors and factory methods
        .def(nb::init<nb::bytes, int32_t, std::optional<int32_t>>(), 
             "data"_a, "offset"_a = 0, "length"_a = nb::none(),
             "Create buffer from bytes data")
        .def_static("allocate", &PyBuffer::allocate, "size"_a,
                   "Allocate a new buffer with specified size")
        
        // Properties and basic info
        .def("size", &PyBuffer::size, "Get buffer size")
        .def("own_data", &PyBuffer::own_data, "Check if buffer owns its data")
        .def_rw("reader_index", &PyBuffer::reader_index, "Current read position")
        .def_rw("writer_index", &PyBuffer::writer_index, "Current write position")
        
        // Memory management
        .def("reserve", &PyBuffer::reserve, "new_size"_a, "Reserve buffer space")
        .def("grow", &PyBuffer::grow, "needed_size"_a, "Grow buffer if needed")
        .def("check_bound", &PyBuffer::check_bound, "offset"_a, "length"_a, 
             "Check if range is within bounds")
        
        // Direct put operations (with offset)
        .def("put_int8", &PyBuffer::put_int8, "offset"_a, "value"_a, 
             "Write int8 at offset")
        .def("put_int16", &PyBuffer::put_int16, "offset"_a, "value"_a, 
             "Write int16 at offset")
        .def("put_int32", &PyBuffer::put_int32, "offset"_a, "value"_a, 
             "Write int32 at offset")
        .def("put_int64", &PyBuffer::put_int64, "offset"_a, "value"_a, 
             "Write int64 at offset")
        .def("put_float", &PyBuffer::put_float, "offset"_a, "value"_a, 
             "Write float at offset")
        .def("put_double", &PyBuffer::put_double, "offset"_a, "value"_a, 
             "Write double at offset")
        
        // Direct get operations (from offset)
        .def("get_int8", &PyBuffer::get_int8, "offset"_a, 
             "Read int8 from offset")
        .def("get_int16", &PyBuffer::get_int16, "offset"_a, 
             "Read int16 from offset")
        .def("get_int32", &PyBuffer::get_int32, "offset"_a, 
             "Read int32 from offset")
        .def("get_int64", &PyBuffer::get_int64, "offset"_a, 
             "Read int64 from offset")
        .def("get_float", &PyBuffer::get_float, "offset"_a, 
             "Read float from offset")
        .def("get_double", &PyBuffer::get_double, "offset"_a, 
             "Read double from offset")
        
        // Stream write operations (auto-advance writer_index)
        .def("write_int8", &PyBuffer::write_int8, "value"_a, 
             "Write int8 and advance position")
        .def("write_int16", &PyBuffer::write_int16, "value"_a, 
             "Write int16 and advance position")
        .def("write_int32", &PyBuffer::write_int32, "value"_a, 
             "Write int32 and advance position")
        .def("write_int64", &PyBuffer::write_int64, "value"_a, 
             "Write int64 and advance position")
        .def("write_float", &PyBuffer::write_float, "value"_a, 
             "Write float and advance position")
        .def("write_double", &PyBuffer::write_double, "value"_a, 
             "Write double and advance position")
        
        // Stream read operations (auto-advance reader_index)
        .def("read_int8", &PyBuffer::read_int8, 
             "Read int8 and advance position")
        .def("read_int16", &PyBuffer::read_int16, 
             "Read int16 and advance position")
        .def("read_int32", &PyBuffer::read_int32, 
             "Read int32 and advance position")
        .def("read_int64", &PyBuffer::read_int64, 
             "Read int64 and advance position")
        .def("read_float", &PyBuffer::read_float, 
             "Read float and advance position")
        .def("read_double", &PyBuffer::read_double, 
             "Read double and advance position")
        
        // Variable-length integer operations
        .def("write_varint32", &PyBuffer::write_varint32, "value"_a, 
             "Write signed varint32")
        .def("write_varuint32", &PyBuffer::write_varuint32, "value"_a, 
             "Write unsigned varint32")
        .def("read_varint32", &PyBuffer::read_varint32, 
             "Read signed varint32")
        .def("read_varuint32", &PyBuffer::read_varuint32, 
             "Read unsigned varint32")
        
        // Byte array operations
        .def("write_bytes_and_size", &PyBuffer::write_bytes_and_size, "value"_a, 
             "Write bytes with length prefix")
        .def("read_bytes_and_size", &PyBuffer::read_bytes_and_size, 
             "Read bytes with length prefix")
        .def("get_bytes", &PyBuffer::get_bytes, "offset"_a, "nbytes"_a, 
             "Get bytes from offset");
}
