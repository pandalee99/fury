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

#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace pyfory_nb {

enum class StatusCode : char {
    OK = 0,
    OutOfMemory = 1,
    OutOfBound = 2,
    KeyError = 3,
    TypeError = 4,
    Invalid = 5,
    IOError = 6,
    UnknownError = 7
};

class Status {
public:
    Status(StatusCode code = StatusCode::OK, const std::string& message = "") 
        : code_(code), message_(message) {}
    
    StatusCode code() const { return code_; }
    const std::string& message() const { return message_; }
    std::string ToString() const {
        return "Status(" + std::to_string(static_cast<int>(code_)) + "): " + message_;
    }
    
private:
    StatusCode code_;
    std::string message_;
};

class Buffer {
public:
    // Constructor from existing data
    Buffer(uint8_t* data, uint32_t size, bool own_data = true);
    
    // Constructor for new allocation
    explicit Buffer(uint32_t size);
    
    // Copy constructor
    Buffer(const Buffer& other);
    
    // Assignment operator
    Buffer& operator=(const Buffer& other);
    
    // Destructor
    ~Buffer();
    
    // Basic accessors
    uint8_t* data() { return data_; }
    const uint8_t* data() const { return data_; }
    uint32_t size() const { return size_; }
    bool own_data() const { return own_data_; }
    
    // Memory management
    bool Reserve(uint32_t new_size);
    
    // Unsafe put operations (no bounds checking)
    void UnsafePutByte(uint32_t offset, bool value);
    void UnsafePutByte(uint32_t offset, uint8_t value);
    void UnsafePutByte(uint32_t offset, int8_t value);
    void UnsafePut(uint32_t offset, int16_t value);
    void UnsafePut(uint32_t offset, int32_t value);
    void UnsafePut(uint32_t offset, int64_t value);
    void UnsafePut(uint32_t offset, float value);
    void UnsafePut(uint32_t offset, double value);
    
    // Copy operations
    void CopyFrom(uint32_t offset, const uint8_t* src, uint32_t src_offset, uint32_t nbytes);
    
    // Get operations
    bool GetBool(uint32_t offset) const;
    int8_t GetInt8(uint32_t offset) const;
    int16_t GetInt16(uint32_t offset) const;
    int32_t GetInt32(uint32_t offset) const;
    int64_t GetInt64(uint32_t offset) const;
    float GetFloat(uint32_t offset) const;
    double GetDouble(uint32_t offset) const;
    
    // Special operations
    Status GetBytesAsInt64(uint32_t offset, uint32_t length, int64_t* target) const;
    uint32_t PutVarUint32(uint32_t offset, int32_t value);
    int32_t GetVarUint32(uint32_t offset, uint32_t* readBytesLength) const;
    
    // Utility operations
    void Copy(uint32_t start, uint32_t nbytes, uint8_t* out, uint32_t offset) const;
    std::string Hex() const;
    
    // Static factory method
    static std::shared_ptr<Buffer> Allocate(uint32_t size);
    
private:
    uint8_t* data_;
    uint32_t size_;
    bool own_data_;
    
    template<typename T>
    void UnsafePutValue(uint32_t offset, T value);
    
    template<typename T>
    T GetValue(uint32_t offset) const;
};

// Utility functions
bool GetBit(const uint8_t* bits, uint32_t i);
void SetBit(uint8_t* bits, uint32_t i);
void ClearBit(uint8_t* bits, uint32_t i);
void SetBitTo(uint8_t* bits, uint32_t i, bool bit_is_set);
std::string hex(const uint8_t* data, int32_t length);
bool utf16HasSurrogatePairs(const uint16_t* data, size_t size);

// Factory function
bool AllocateBuffer(uint32_t size, std::shared_ptr<Buffer>* out);

} // namespace pyfory_nb
