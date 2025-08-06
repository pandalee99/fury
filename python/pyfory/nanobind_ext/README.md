# PyFory Nanobind Extension

这个目录包含了PyFory项目的nanobind扩展，提供高性能的C++函数绑定。

## 重要说明

当前的实现包含了：
1. **纯Python回退实现** - 在nanobind扩展不可用时自动使用
2. **nanobind C++扩展代码** - 提供高性能的C++实现
3. **完整的测试和演示** - 验证功能的正确性

## 当前状态

✅ **工作正常**: 
- 纯Python回退实现已完全工作
- 测试通过（使用回退实现）
- 模块导入无错误

🔧 **待完成**: 
- nanobind C++扩展的编译（需要安装nanobind）

## 快速测试

```bash
# 测试当前实现（使用回退）
cd python/pyfory/nanobind_ext
python3 test_quick.py

# 在主项目中测试
cd python
python3 -m pytest pyfory/tests/test_buffer.py::test_nanobind_extension -v
```

## 安装依赖（可选 - 用于C++扩展）

要构建高性能的C++扩展，需要安装：

```bash
pip install nanobind
```

## 构建C++扩展（可选）

### 方法1：使用setuptools

```bash
cd python/pyfory/nanobind_ext
python3 setup.py build_ext --inplace
```

### 方法2：使用构建脚本

```bash
cd python/pyfory/nanobind_ext
./build.sh
```

## 使用方法

无论是否安装了nanobind，使用方法都是一样的：

```python
from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer

# 基本算术运算
result = add(2, 3)  # 返回 5
product = multiply(2.5, 4.0)  # 返回 10.0

# 缓冲区操作  
buffer = create_buffer(10, 42)  # 创建大小为10，值为42的缓冲区
total = sum_buffer(buffer)  # 计算缓冲区所有值的和
```

## 功能说明

当前实现提供以下函数：

- `add(a, b)`: 两个整数相加
- `multiply(a, b)`: 两个浮点数相乘  
- `create_buffer(size, fill_value=0)`: 创建指定大小和填充值的缓冲区
- `sum_buffer(buffer)`: 计算缓冲区中所有值的总和

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
