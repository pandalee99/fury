# PyFory Nanobind Extension

这个目录包含了PyFory项目的nanobind扩展，提供高性能的C++函数绑定。

## 安装依赖

要构建和使用nanobind扩展，需要安装以下依赖：

### 1. 安装nanobind

```bash
pip install nanobind
```

### 2. 安装构建工具（可选）

如果使用CMake构建：
```bash
pip install cmake
```

### 3. 安装其他依赖

```bash
pip install setuptools wheel
```

## 构建扩展

### 方法1：使用setuptools（推荐）

在`pyfory/nanobind_ext`目录下执行：

```bash
cd python/pyfory/nanobind_ext
python setup.py build_ext --inplace
```

### 方法2：使用CMake

```bash
cd python/pyfory/nanobind_ext
mkdir build
cd build
cmake ..
make
```

### 方法3：集成到主项目

修改主项目的`pyproject.toml`文件，添加nanobind依赖：

```toml
[build-system]
requires = [
    "setuptools>=45",
    "wheel",
    "Cython>=0.29",
    "numpy",
    "nanobind>=1.0.0",  # 添加这一行
    "pyarrow==15.0.0; python_version<'3.13'",
    "pyarrow==18.0.0; python_version>='3.13'",
]
```

然后在主项目的`setup.py`中添加nanobind扩展的构建逻辑。

## 使用方法

构建完成后，可以在Python中使用：

```python
from pyfory.nanobind_ext import add, multiply, create_buffer, sum_buffer

# 基本算术运算
result = add(2, 3)  # 返回 5
product = multiply(2.5, 4.0)  # 返回 10.0

# 缓冲区操作
buffer = create_buffer(10, 42)  # 创建大小为10，值为42的缓冲区
total = sum_buffer(buffer)  # 计算缓冲区所有值的和
```

## 测试

运行测试以验证扩展是否正常工作：

```bash
cd python
python -m pytest pyfory/tests/test_buffer.py::test_nanobind_extension -v
```

或者直接运行测试文件：

```bash
cd python
python pyfory/tests/test_buffer.py
```

## 功能说明

当前nanobind扩展提供以下函数：

- `add(a, b)`: 两个整数相加
- `multiply(a, b)`: 两个浮点数相乘
- `create_buffer(size, fill_value=0)`: 创建指定大小和填充值的缓冲区
- `sum_buffer(buffer)`: 计算缓冲区中所有值的总和

这些函数展示了nanobind与PyFory现有Buffer系统的集成可能性。

## 故障排除

### 如果nanobind未安装

如果nanobind未安装，扩展会自动回退到纯Python实现，不会影响项目的其他功能。

### 如果构建失败

1. 确保安装了正确版本的nanobind
2. 检查C++编译器是否支持C++17
3. 确保Python开发头文件已安装

### 模块命名注意事项

模块被命名为`pyfory_nb`以避免与现有的PyFory模块冲突。这个命名符合项目的命名约定。

## 扩展建议

可以考虑将更多PyFory的核心功能移植到nanobind：

1. 高性能的序列化/反序列化函数
2. 缓冲区操作优化
3. 类型转换加速
4. 内存管理优化

这将提供比Cython更好的性能和更简洁的代码。
