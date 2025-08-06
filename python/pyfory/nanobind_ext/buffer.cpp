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

#include "buffer.h"
#include <cstring>
#include <algorithm>
#include <sstream>
#include <iomanip>

namespace pyfory_nb {

// Buffer implementation
Buffer::Buffer(uint8_t* data, uint32_t size, bool own_data)
    : data_(data), size_(size), own_data_(own_data) {
}

Buffer::Buffer(uint32_t size) : size_(size), own_data_(true) {
    data_ = new uint8_t[size];
    std::memset(data_, 0, size);
}

Buffer::Buffer(const Buffer& other) 
    : size_(other.size_), own_data_(true) {
    data_ = new uint8_t[size_];
    std::memcpy(data_, other.data_, size_);
}

Buffer& Buffer::operator=(const Buffer& other) {
    if (this != &other) {
        if (own_data_ && data_) {
            delete[] data_;
        }
        size_ = other.size_;
        own_data_ = true;
        data_ = new uint8_t[size_];
        std::memcpy(data_, other.data_, size_);
    }
    return *this;
}

Buffer::~Buffer() {
    if (own_data_ && data_) {
        delete[] data_;
    }
}

bool Buffer::Reserve(uint32_t new_size) {
    if (new_size <= size_) {
        return true;
    }
    
    uint8_t* new_data = new uint8_t[new_size];
    if (!new_data) {
        return false;
    }
    
    std::memset(new_data, 0, new_size);
    if (data_) {
        std::memcpy(new_data, data_, size_);
        if (own_data_) {
            delete[] data_;
        }
    }
    
    data_ = new_data;
    size_ = new_size;
    own_data_ = true;
    return true;
}

void Buffer::UnsafePutByte(uint32_t offset, bool value) {
    data_[offset] = value ? 1 : 0;
}

void Buffer::UnsafePutByte(uint32_t offset, uint8_t value) {
    data_[offset] = value;
}

void Buffer::UnsafePutByte(uint32_t offset, int8_t value) {
    data_[offset] = static_cast<uint8_t>(value);
}

template<typename T>
void Buffer::UnsafePutValue(uint32_t offset, T value) {
    std::memcpy(data_ + offset, &value, sizeof(T));
}

void Buffer::UnsafePut(uint32_t offset, int16_t value) {
    UnsafePutValue(offset, value);
}

void Buffer::UnsafePut(uint32_t offset, int32_t value) {
    UnsafePutValue(offset, value);
}

void Buffer::UnsafePut(uint32_t offset, int64_t value) {
    UnsafePutValue(offset, value);
}

void Buffer::UnsafePut(uint32_t offset, float value) {
    UnsafePutValue(offset, value);
}

void Buffer::UnsafePut(uint32_t offset, double value) {
    UnsafePutValue(offset, value);
}

void Buffer::CopyFrom(uint32_t offset, const uint8_t* src, uint32_t src_offset, uint32_t nbytes) {
    std::memcpy(data_ + offset, src + src_offset, nbytes);
}

bool Buffer::GetBool(uint32_t offset) const {
    return data_[offset] != 0;
}

int8_t Buffer::GetInt8(uint32_t offset) const {
    return static_cast<int8_t>(data_[offset]);
}

template<typename T>
T Buffer::GetValue(uint32_t offset) const {
    T value;
    std::memcpy(&value, data_ + offset, sizeof(T));
    return value;
}

int16_t Buffer::GetInt16(uint32_t offset) const {
    return GetValue<int16_t>(offset);
}

int32_t Buffer::GetInt32(uint32_t offset) const {
    return GetValue<int32_t>(offset);
}

int64_t Buffer::GetInt64(uint32_t offset) const {
    return GetValue<int64_t>(offset);
}

float Buffer::GetFloat(uint32_t offset) const {
    return GetValue<float>(offset);
}

double Buffer::GetDouble(uint32_t offset) const {
    return GetValue<double>(offset);
}

Status Buffer::GetBytesAsInt64(uint32_t offset, uint32_t length, int64_t* target) const {
    if (length == 0) {
        *target = 0;
        return Status(StatusCode::OK);
    }
    
    if (offset + length > size_) {
        return Status(StatusCode::OutOfBound, "Buffer access out of bounds");
    }
    
    if (length > 8) {
        return Status(StatusCode::Invalid, "Length cannot exceed 8 bytes for int64");
    }
    
    int64_t result = 0;
    for (uint32_t i = 0; i < length; ++i) {
        result |= (static_cast<int64_t>(data_[offset + i]) << (i * 8));
    }
    *target = result;
    return Status(StatusCode::OK);
}

uint32_t Buffer::PutVarUint32(uint32_t offset, int32_t value) {
    uint32_t uvalue = static_cast<uint32_t>(value);
    uint32_t bytes_written = 0;
    
    while (uvalue >= 0x80) {
        data_[offset + bytes_written] = static_cast<uint8_t>((uvalue & 0x7F) | 0x80);
        uvalue >>= 7;
        bytes_written++;
    }
    data_[offset + bytes_written] = static_cast<uint8_t>(uvalue & 0x7F);
    bytes_written++;
    
    return bytes_written;
}

int32_t Buffer::GetVarUint32(uint32_t offset, uint32_t* readBytesLength) const {
    uint32_t result = 0;
    uint32_t shift = 0;
    uint32_t bytes_read = 0;
    
    while (offset + bytes_read < size_) {
        uint8_t byte = data_[offset + bytes_read];
        result |= (static_cast<uint32_t>(byte & 0x7F) << shift);
        bytes_read++;
        
        if ((byte & 0x80) == 0) {
            break;
        }
        shift += 7;
        if (shift >= 32) {
            break; // Prevent overflow
        }
    }
    
    *readBytesLength = bytes_read;
    return static_cast<int32_t>(result);
}

void Buffer::Copy(uint32_t start, uint32_t nbytes, uint8_t* out, uint32_t offset) const {
    std::memcpy(out + offset, data_ + start, nbytes);
}

std::string Buffer::Hex() const {
    return hex(data_, size_);
}

std::shared_ptr<Buffer> Buffer::Allocate(uint32_t size) {
    try {
        return std::make_shared<Buffer>(size);
    } catch (...) {
        return nullptr;
    }
}

// Utility functions implementation
bool GetBit(const uint8_t* bits, uint32_t i) {
    return (bits[i / 8] & (1 << (i % 8))) != 0;
}

void SetBit(uint8_t* bits, uint32_t i) {
    bits[i / 8] |= (1 << (i % 8));
}

void ClearBit(uint8_t* bits, uint32_t i) {
    bits[i / 8] &= ~(1 << (i % 8));
}

void SetBitTo(uint8_t* bits, uint32_t i, bool bit_is_set) {
    if (bit_is_set) {
        SetBit(bits, i);
    } else {
        ClearBit(bits, i);
    }
}

std::string hex(const uint8_t* data, int32_t length) {
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (int32_t i = 0; i < length; ++i) {
        ss << std::setw(2) << static_cast<unsigned>(data[i]);
    }
    return ss.str();
}

bool utf16HasSurrogatePairs(const uint16_t* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        uint16_t code_unit = data[i];
        if (code_unit >= 0xD800 && code_unit <= 0xDBFF) {
            // High surrogate
            if (i + 1 < size) {
                uint16_t next = data[i + 1];
                if (next >= 0xDC00 && next <= 0xDFFF) {
                    // Valid surrogate pair
                    return true;
                }
            }
        }
    }
    return false;
}

bool AllocateBuffer(uint32_t size, std::shared_ptr<Buffer>* out) {
    try {
        *out = Buffer::Allocate(size);
        return *out != nullptr;
    } catch (...) {
        return false;
    }
}

} // namespace pyfory_nb
