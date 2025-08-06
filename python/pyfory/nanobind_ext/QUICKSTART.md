# PyFory Nanobind Buffer - 快速使用指南

## 🚀 快速开始

### 1. 构建扩展
```bash
cd python/pyfory/nanobind_ext
python3 setup.py build_ext --inplace
```

### 2. 基础用法
```python
from pyfory.nanobind_ext import Buffer

# 创建Buffer
buffer = Buffer.allocate(1024)

# 写入数据
buffer.write_int32(12345)
buffer.write_float(3.14159)
buffer.write_bytes_and_size(b"Hello, World!")

# 读取数据
buffer.reader_index = 0
value1 = buffer.read_int32()        # 12345
value2 = buffer.read_float()        # 3.14159
value3 = buffer.read_bytes_and_size()  # b"Hello, World!"
```

## 💡 主要特性

### ✅ 完整功能实现
- **所有数据类型**: int8/16/24/32/64, float/double
- **变长整数**: varint32/varuint32（高效压缩）
- **字节操作**: 带长度前缀和原始字节
- **内存管理**: 自动扩容和边界检查
- **流式读写**: 自动位置管理

### ⚡ 性能优势
- **比Cython快1.2-1.8倍**（预期）
- **零拷贝操作**
- **优化的内存管理**
- **内联函数优化**

### 🔄 自动回退
- nanobind不可用时自动使用纯Python实现
- API完全相同，无需修改代码
- 兼容性最佳，性能次优

## 📝 API 速查表

### 创建Buffer
```python
# 从字节创建
buffer = Buffer(b'\x00\x01\x02\x03')

# 分配新Buffer  
buffer = Buffer.allocate(size)

# 带偏移的视图
buffer = Buffer(data, offset=10, length=20)
```

### 直接读写（指定位置）
```python
# 写入
buffer.put_int32(offset, value)
buffer.put_float(offset, value)

# 读取  
value = buffer.get_int32(offset)
value = buffer.get_float(offset)
```

### 流式读写（自动位置）
```python
# 写入（推进writer_index）
buffer.write_int32(value)
buffer.write_float(value)

# 读取（推进reader_index）
value = buffer.read_int32()
value = buffer.read_float()
```

### 变长整数（空间优化）
```python
# 有符号（ZigZag编码）
buffer.write_varint32(value)
value = buffer.read_varint32()

# 无符号  
buffer.write_varuint32(value)
value = buffer.read_varuint32()
```

### 字节数组
```python
# 带长度前缀（自描述）
buffer.write_bytes_and_size(b"data")
data = buffer.read_bytes_and_size()

# 原始字节
buffer.write_bytes(b"data")
data = buffer.get_bytes(offset, length)
```

## ⚠️ 重要提醒

### 数据类型范围
```python
# ✅ 正确用法
buffer.write_int8(127)      # -128 到 127
buffer.write_bytes(b'\xff') # 0 到 255

# ❌ 错误用法  
# buffer.write_int8(255)    # 超出int8范围！
```

### 性能测试
```python
# 对比nanobind vs Cython性能
python3 test_buffer_comprehensive.py
```

## 🔧 故障排除

### 编译失败
```bash
# 确保安装nanobind
pip install nanobind

# 检查C++编译器
gcc --version  # 需要支持C++17
```

### 检查实现类型
```python
from pyfory.nanobind_ext import Buffer
print(Buffer.__module__)
# "pyfory_nb" = 使用nanobind扩展
# 其他 = 使用Python回退
```

---
🎯 **目标**: 提供比Cython更快的高性能Buffer实现，同时保持完全的API兼容性！
