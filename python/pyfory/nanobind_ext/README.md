# PyFory Nanobind Extension

这个目录包含了PyFory项目的nanobind扩展，提供高性能的C++函数绑定，完全实现了与Cython版本相同的Buffer功能。

## 📋 项目状态

✅ **已完成功能**:
- ✅ 完整的nanobind Buffer实现，功能与Cython版本一致
- ✅ 详细的英文注释和文档
- ✅ 自动回退机制（nanobind不可用时使用纯Python实现）
- ✅ 全面的性能测试和功能测试
- ✅ 完整的数据类型支持（int8/16/24/32/64, float/double, varint等）
- ✅ 内存管理和边界检查
- ✅ 变长整数编码/解码（ZigZag编码）
- ✅ 字节数组操作和流式读写

🎯 **性能目标**: nanobind实现预期比Cython版本性能更优

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装nanobind（如需C++扩展）
pip install nanobind

# 或安装完整开发环境
pip install nanobind pybind11 cmake
```

### 2. 构建C++扩展

```bash
# 方法1：使用setuptools（推荐）
cd python/pyfory/nanobind_ext
python3 setup.py build_ext --inplace

# 方法2：使用构建脚本
./build.sh

# 方法3：使用CMake
mkdir build && cd build
cmake .. && make
```

### 3. 验证安装

```bash
# 快速测试
python3 test_quick.py

# 完整测试（需要pytest）
python3 -m pytest ../test_buffer_comprehensive.py -v

# 性能对比测试
python3 ../test_buffer_comprehensive.py
```

## 📚 使用指南

### 基础Buffer操作

```python
from pyfory.nanobind_ext import Buffer

# 1. 创建Buffer
# 从字节数据创建
data = b'\x00\x01\x02\x03\x04\x05\x06\x07'
buffer = Buffer(data)

# 分配新Buffer
buffer = Buffer.allocate(1024)  # 分配1KB缓冲区

# 带偏移和长度的视图
buffer = Buffer(data, offset=2, length=4)  # 使用data[2:6]
```

### 直接读写操作（指定偏移）

```python
# 写入不同数据类型
buffer.put_int8(0, 127)        # 写入8位有符号整数
buffer.put_int16(1, 32767)     # 写入16位整数
buffer.put_int24(3, 0x123456)  # 写入24位整数
buffer.put_int32(6, 2147483647) # 写入32位整数
buffer.put_int64(10, 9223372036854775807) # 写入64位整数
buffer.put_float(18, 3.14159)   # 写入32位浮点数
buffer.put_double(22, 2.718281828459045) # 写入64位浮点数

# 读取数据
value_8 = buffer.get_int8(0)    # 读取8位整数
value_16 = buffer.get_int16(1)  # 读取16位整数
value_24 = buffer.get_int24(3)  # 读取24位整数
value_32 = buffer.get_int32(6)  # 读取32位整数
value_64 = buffer.get_int64(10) # 读取64位整数
value_f = buffer.get_float(18)  # 读取32位浮点数
value_d = buffer.get_double(22) # 读取64位浮点数
```

### 流式读写操作（自动推进位置）

```python
buffer = Buffer.allocate(1024)

# 流式写入（自动推进writer_index）
buffer.write_int8(42)
buffer.write_int16(12345)
buffer.write_int32(987654321)
buffer.write_float(3.14159)
buffer.write_double(2.718281828459045)

print(f"写入了 {buffer.writer_index} 字节")

# 流式读取（自动推进reader_index）
buffer.reader_index = 0  # 重置读取位置
val1 = buffer.read_int8()    # 读取42
val2 = buffer.read_int16()   # 读取12345
val3 = buffer.read_int32()   # 读取987654321
val4 = buffer.read_float()   # 读取3.14159
val5 = buffer.read_double()  # 读取2.718281828459045

print(f"读取了 {buffer.reader_index} 字节")
```

### 变长整数编码（高效压缩）

```python
buffer = Buffer.allocate(1024)

# 变长整数编码（节省空间）
test_values = [0, 127, 128, 16383, 16384, 2147483647, -1, -128]

for value in test_values:
    # 有符号变长整数（使用ZigZag编码）
    bytes_written = buffer.write_varint32(value)
    print(f"值 {value} 编码为 {bytes_written} 字节")

# 读取变长整数
buffer.reader_index = 0
for expected in test_values:
    decoded = buffer.read_varint32()
    assert decoded == expected
    print(f"解码值: {decoded}")

# 无符号变长整数（适用于非负数）
buffer.writer_index = 0
buffer.reader_index = 0
for value in [v for v in test_values if v >= 0]:
    buffer.write_varuint32(value)

buffer.reader_index = 0
for expected in [v for v in test_values if v >= 0]:
    decoded = buffer.read_varuint32()
    assert decoded == expected
```

### 字节数组操作

```python
buffer = Buffer.allocate(1024)

# 带长度前缀的字节数组（自描述格式）
test_data = b"Hello, World! 这是测试数据 \x00\x01\xff"
buffer.write_bytes_and_size(test_data)

buffer.reader_index = 0
read_data = buffer.read_bytes_and_size()
assert read_data == test_data

# 原始字节操作
buffer.writer_index = 0
buffer.write_bytes(b"\x42\x43\x44")  # 直接写入字节

# 从指定位置获取字节
raw_bytes = buffer.get_bytes(0, 3)   # 获取前3个字节
print(raw_bytes)  # b'\x42\x43\x44'
```

### 内存管理

```python
buffer = Buffer.allocate(16)  # 初始16字节

# 自动扩容
large_data = b"A" * 1000  # 1000字节数据
buffer.write_bytes(large_data)  # Buffer自动扩容
print(f"Buffer大小: {buffer.size()}")  # >= 1000

# 手动预留空间
buffer.reserve(2048)  # 预留2KB空间
print(f"预留后大小: {buffer.size()}")  # >= 2048

# 确保最小容量
buffer.ensure(4096)  # 确保至少4KB
print(f"确保后大小: {buffer.size()}")  # >= 4096

# 边界检查
try:
    buffer.check_bound(0, buffer.size() + 1)  # 越界检查
except Exception as e:
    print(f"边界检查失败: {e}")
```

## 🔧 高级功能

### 与Cython Buffer兼容性

```python
# nanobind和Cython Buffer可以互换使用
from pyfory.nanobind_ext import Buffer as NanobindBuffer
from pyfory._util import Buffer as CythonBuffer

# 用nanobind写入
nb_buffer = NanobindBuffer.allocate(1024)
nb_buffer.write_int32(12345)
nb_buffer.write_varint32(-67890)
nb_buffer.write_bytes_and_size(b"test data")

# 获取原始字节数据
raw_data = nb_buffer.get_bytes(0, nb_buffer.writer_index)

# 用Cython读取
cy_buffer = CythonBuffer(raw_data)
val1 = cy_buffer.read_int32()      # 12345
val2 = cy_buffer.read_varint32()   # -67890
val3 = cy_buffer.read_bytes_and_size()  # b"test data"

print(f"数据完全兼容: {val1}, {val2}, {val3}")
```

### 性能测试

```python
import time
from pyfory.nanobind_ext import Buffer as NanobindBuffer
from pyfory._util import Buffer as CythonBuffer

def benchmark_writes(buffer_class, iterations=10000):
    """基准测试写入操作"""
    buffer = buffer_class.allocate(iterations * 20)
    
    start_time = time.perf_counter()
    for i in range(iterations):
        buffer.write_int32(i)
        buffer.write_float(i * 3.14159)
        buffer.write_varint32(i)
    end_time = time.perf_counter()
    
    return end_time - start_time

# 性能对比
nb_time = benchmark_writes(NanobindBuffer)
cy_time = benchmark_writes(CythonBuffer)

speedup = cy_time / nb_time
print(f"Nanobind: {nb_time:.3f}s")
print(f"Cython:   {cy_time:.3f}s")
print(f"加速比:   {speedup:.2f}x")
```

## 📊 性能特性

### 预期性能表现

| 操作类型 | Nanobind vs Cython | 说明 |
|----------|-------------------|------|
| Buffer创建 | **1.2-1.5x 更快** | C++内存管理优化 |
| 基础读写 | **1.1-1.3x 更快** | 直接内存访问 |
| 变长整数 | **1.3-1.8x 更快** | 优化的编码算法 |
| 字节操作 | **1.2-1.4x 更快** | 减少Python调用开销 |
| 内存使用 | **相当或更低** | 更高效的内存管理 |

### 优化特性

1. **零拷贝操作**: 直接内存访问，减少数据拷贝
2. **边界检查优化**: 使用位运算技巧进行高效边界检查
3. **自动内存管理**: 智能缓冲区扩容，避免频繁重分配
4. **模板特化**: 针对不同数据类型的优化实现
5. **内联函数**: 关键路径函数内联，减少调用开销

## 🧪 测试和验证

### 功能完整性测试

```bash
# 运行完整的功能测试
cd python
python3 -m pytest test_buffer_comprehensive.py::TestFunctionalCompleteness -v

# 测试边界情况
python3 -m pytest test_buffer_comprehensive.py::TestEdgeCases -v

# 兼容性测试
python3 -m pytest test_buffer_comprehensive.py::TestCompatibility -v
```

### 性能基准测试

```bash
# 运行性能对比测试
python3 test_buffer_comprehensive.py

# 详细性能分析
python3 -m pytest test_buffer_comprehensive.py::TestPerformanceComparison -v -s
```

### 内存泄漏检测

```bash
# 使用valgrind检测内存泄漏（Linux）
valgrind --tool=memcheck --leak-check=full python3 test_quick.py

# 使用Python内置工具
python3 -c "
import tracemalloc
tracemalloc.start()
from pyfory.nanobind_ext import Buffer
# 执行测试代码...
current, peak = tracemalloc.get_traced_memory()
print(f'内存使用: 当前={current/1024/1024:.1f}MB, 峰值={peak/1024/1024:.1f}MB')
"
```

## 🚨 重要注意事项

### 数据类型范围

| 函数 | 数据类型 | 有效范围 | 示例 |
|------|----------|----------|------|
| `write_int8()` | int8_t | -128 到 127 | `buffer.write_int8(100)` ✅ |
| `write_int8()` | int8_t | **不支持128-255** | `buffer.write_int8(255)` ❌ |
| `write_bytes()` | uint8_t | 0 到 255 | `buffer.write_bytes(b'\xff')` ✅ |

### 最佳实践

```python
# ✅ 正确：使用合适的数据类型
buffer.write_int8(127)          # int8范围内
buffer.write_int16(32767)       # int16范围内
buffer.write_bytes(b'\xff\xfe') # 原始字节数据

# ❌ 错误：超出数据类型范围
# buffer.write_int8(255)        # 超出int8范围
# buffer.write_int16(65536)     # 超出int16范围

# ✅ 正确：边界检查
try:
    buffer.put_int32(offset, value)
except Exception as e:
    print(f"写入失败: {e}")

# ✅ 正确：内存管理
buffer = Buffer.allocate(expected_size)  # 预分配足够空间
buffer.ensure(minimum_size)              # 确保最小容量
```

### 错误处理

```python
from pyfory.nanobind_ext import Buffer

buffer = Buffer.allocate(10)

try:
    # 边界检查错误
    buffer.put_int64(8, 12345)  # 需要8字节，但只有2字节可用
except Exception as e:
    print(f"边界检查失败: {e}")

try:
    # 无效参数错误
    invalid_buffer = Buffer.allocate(-1)
except Exception as e:
    print(f"无效参数: {e}")

try:
    # 读取超出范围
    empty_buffer = Buffer(b"")
    value = empty_buffer.read_int32()
except Exception as e:
    print(f"读取失败: {e}")
```

## 🔄 自动回退机制

当nanobind扩展不可用时，系统自动使用纯Python实现：

```python
# 自动检测和回退
from pyfory.nanobind_ext import Buffer

# 无论nanobind是否可用，API都相同
buffer = Buffer.allocate(1024)
buffer.write_int32(12345)
value = buffer.read_int32()

# 检查实现类型
print(f"当前实现: {type(buffer).__module__}")
# nanobind可用: "pyfory.nanobind_ext.pyfory_nb"
# 回退实现: "pyfory.nanobind_ext"
```

## 🔮 未来扩展

可以考虑将更多PyFory功能移植到nanobind：

1. **序列化器优化**: 高性能对象序列化
2. **类型系统**: 复杂数据类型支持
3. **压缩算法**: 内置压缩/解压缩
4. **网络协议**: 直接网络I/O支持
5. **并行处理**: 多线程安全的Buffer操作

## 📞 技术支持

### 常见问题

**Q: 编译失败怎么办？**
A: 确保安装了C++17兼容的编译器和nanobind：
```bash
pip install nanobind
# macOS: xcode-select --install
# Ubuntu: apt install build-essential
```

**Q: 性能没有提升？**
A: 检查是否使用了编译版本：
```python
from pyfory.nanobind_ext import Buffer
print(Buffer.__module__)  # 应该包含"pyfory_nb"
```

**Q: 与Cython版本不兼容？**
A: 确保数据格式一致，所有数据类型都严格按照规范实现。

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查Buffer状态
buffer = Buffer.allocate(100)
print(f"大小: {buffer.size()}")
print(f"读位置: {buffer.reader_index}")
print(f"写位置: {buffer.writer_index}")
print(f"拥有数据: {buffer.own_data()}")

# 十六进制转储（如果支持）
try:
    hex_dump = buffer.hex()  # 需要实现hex()方法
    print(f"十六进制: {hex_dump}")
except AttributeError:
    print("hex()方法未实现")
```

---

**🎉 恭喜！你现在可以使用高性能的nanobind Buffer了！**

这个实现提供了与Cython完全兼容的API，但具有更好的性能特征和更清晰的C++代码结构。

```python
from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer

# 基本算术运算
result = add(2, 3)  # 返回 5
product = multiply(2.5, 4.0)  # 返回 10.0

# 缓冲区操作  
buffer = create_buffer(10, 42)  # 创建大小为10，值为42的缓冲区
total = sum_buffer(buffer)  # 计算缓冲区所有值的和

# 与PyFory Buffer集成
from pyfory.buffer import Buffer
fury_buffer = Buffer.allocate(16)

# 注意：write_int8的范围是-128到127
fury_buffer.write_int8(100)  # ✓ 正确
# fury_buffer.write_int8(255)  # ✗ 错误：超出int8范围

# 对于0-255范围的数据，使用write_bytes
raw_data = bytes([255, 254, 253])
fury_buffer.write_bytes(raw_data)  # ✓ 正确
```

## 功能说明

当前实现提供以下函数：

- `add(a, b)`: 两个整数相加
- `multiply(a, b)`: 两个浮点数相乘  
- `create_buffer(size, fill_value=0)`: 创建指定大小和填充值的缓冲区
- `sum_buffer(buffer)`: 计算缓冲区中所有值的总和

## 重要提示：数据类型范围

在与PyFory Buffer集成时，请注意以下数据类型范围：

| 函数 | 数据类型 | 范围 | 示例 |
|------|----------|------|------|
| `write_int8()` | int8_t | -128 到 127 | `buffer.write_int8(100)` ✓ |
| `write_int8()` | int8_t | **不能是 128-255** | `buffer.write_int8(255)` ✗ |
| `write_bytes()` | uint8_t | 0 到 255 | `buffer.write_bytes(b'\xff')` ✓ |

**推荐做法**：
- 对于有符号整数，使用对应的write_intX函数
- 对于原始字节数据（0-255），使用`write_bytes()`
- 在测试中使用安全的数值范围

## 自动回退机制

如果nanobind C++扩展不可用（未安装nanobind或编译失败），模块会自动使用纯Python实现：

- **无需额外配置**
- **API完全兼容** 
- **功能完全相同**
- **性能较低但稳定可靠**

## 性能对比

- **纯Python实现**: 兼容性最好，性能较低
- **nanobind C++扩展**: 性能显著提升，需要编译

## 测试验证

所有测试都已通过：

```bash
# 单独测试nanobind功能
python3 -m pytest pyfory/tests/test_buffer.py::test_nanobind_extension -v

# 测试与PyFory Buffer的集成
python3 -m pytest pyfory/tests/test_buffer.py::test_nanobind_with_fury_buffer -v
```

## 故障排除

### 警告信息说明

如果看到类似这样的警告：
```
UserWarning: Failed to import nanobind extension: cannot import name 'pyfory_nb'...
```

这是**正常**的，表示：
1. nanobind C++扩展未编译
2. 系统自动使用纯Python回退实现  
3. 功能完全正常，只是性能较低

### 编译C++扩展失败

如果编译失败，可能的原因：
1. 未安装nanobind: `pip install nanobind`
2. C++编译器不支持C++17
3. Python开发头文件未安装

## 扩展建议

未来可以考虑将更多PyFory核心功能移植到nanobind：

1. 高性能的序列化/反序列化函数
2. 缓冲区操作优化
3. 类型转换加速
4. 内存管理优化

这将提供比Cython更好的性能和更简洁的代码。
