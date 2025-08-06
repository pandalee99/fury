# PyFory Nanobind Buffer 编译指南

## 快速开始

### 1. 确认环境要求

```bash
# 检查 Python 版本 (需要 3.8+)
python --version

# 检查 nanobind 是否已安装
python -c "import nanobind; print(nanobind.__version__)"

# 如果没有安装 nanobind
pip install nanobind
```

### 2. 编译扩展模块

有几种编译方法，选择适合你的：

#### 方法 A: 使用 nanobind 直接编译

```bash
cd python/pyfory/nanobind_ext

# 获取编译参数
python -m nanobind --cmake_dir

# 手动编译 (Linux/macOS)
c++ -O3 -Wall -shared -std=c++17 -fPIC \
    $(python -m nanobind --cmake_dir)/nanobind-config.cmake \
    pyfory_nb.cpp buffer.cpp \
    -o nanobind_ext$(python3-config --extension-suffix)
```

#### 方法 B: 使用 setup.py 编译

如果项目有 setup.py：

```bash
cd python
python setup.py build_ext --inplace
```

#### 方法 C: 使用 CMake 编译

如果项目支持 CMake：

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 3. 验证安装

```python
# 测试导入
from pyfory.nanobind_ext import Buffer

# 基本功能测试
buffer = Buffer.allocate(1024)
buffer.write_int32(12345)
buffer.reader_index = 0
value = buffer.read_int32()
print(f"Test passed: {value == 12345}")
```

### 4. 运行示例

```bash
# 运行完整示例
python pyfory/nanobind_ext/examples.py

# 运行性能测试
python test_buffer_comprehensive.py
```

## 常见问题

### Q: 编译时找不到 nanobind

**A:** 确保已安装 nanobind：
```bash
pip install nanobind>=2.0.0
```

### Q: 编译时出现 C++ 标准版本错误

**A:** 确保使用 C++17 或更高版本：
```bash
# 检查编译器版本
g++ --version
clang++ --version

# 编译时指定标准
-std=c++17
```

### Q: 导入时找不到模块

**A:** 检查模块路径：
```python
import sys
sys.path.append('/path/to/python')

# 或设置环境变量
export PYTHONPATH="/path/to/python:$PYTHONPATH"
```

### Q: 运行时崩溃

**A:** 检查以下几点：
1. 确保 buffer.cpp 和 buffer.h 存在
2. 检查内存对齐和边界
3. 使用调试版本编译：`-g -O0`

## 性能优化建议

### 编译优化

```bash
# 发布版本编译
c++ -O3 -DNDEBUG -march=native

# 启用链接时优化
c++ -O3 -flto

# 针对特定 CPU 优化
c++ -O3 -march=native -mtune=native
```

### 使用建议

1. **批量操作**: 尽量批量读写数据
2. **预分配**: 提前分配足够的缓冲区大小
3. **避免频繁扩容**: 使用 `reserve()` 预留空间
4. **内存重用**: 重用已分配的缓冲区

## 文件结构

```
python/
├── pyfory/
│   └── nanobind_ext/
│       ├── __init__.py           # 模块初始化
│       ├── pyfory_nb.cpp         # nanobind 绑定代码
│       ├── buffer.h              # C++ Buffer 头文件
│       ├── buffer.cpp            # C++ Buffer 实现
│       ├── examples.py           # 使用示例
│       └── README.md             # 详细文档
├── test_buffer_comprehensive.py  # 测试套件
├── build_and_test.py            # 自动化构建脚本
└── COMPILE_GUIDE.md             # 本文档
```

## 下一步

1. 成功编译后，查看 `README.md` 了解详细 API
2. 运行 `examples.py` 学习使用方法  
3. 运行 `test_buffer_comprehensive.py` 验证性能
4. 在你的项目中集成使用

## 技术支持

如果遇到问题：

1. 检查所有依赖是否正确安装
2. 确认编译参数是否正确
3. 查看编译器错误信息
4. 尝试使用调试版本编译

Happy coding! 🚀
