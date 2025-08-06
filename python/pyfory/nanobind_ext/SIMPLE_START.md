# 🚀 超简单开始指南

## 只需要这 3 步：

### 1. 检查 nanobind（✅ 你已经安装了）
```bash
python3 -c "import nanobind; print('OK:', nanobind.__version__)"
```

### 2. 直接手动编译
```bash
cd /workspace/fury/python/pyfory/nanobind_ext

# 一行命令编译
python3 -m nanobind.cmake --module pyfory_nb pyfory_nb.cpp buffer.cpp
```

### 3. 测试使用
```python
# 简单测试
python3 -c "
from pyfory.nanobind_ext import Buffer
buffer = Buffer.allocate(100)
buffer.write_int32(12345)
buffer.reader_index = 0
print('测试结果:', buffer.read_int32())
print('✅ 成功!')
"
```

## 如果第 2 步失败，用这个：

```bash
# 手动编译（备用方案）
c++ -O3 -Wall -shared -std=c++17 -fPIC \
    `python3 -m nanobind --cmake_dir` \
    `python3-config --includes` \
    pyfory_nb.cpp buffer.cpp \
    -o pyfory_nb`python3-config --extension-suffix`
```

## 测试是否工作：

```python
# 运行这个简单测试
python3 -c "
try:
    from pyfory.nanobind_ext import Buffer
    b = Buffer.allocate(10)
    b.write_int32(999)
    print('✅ nanobind Buffer 工作正常!')
except Exception as e:
    print('❌ 错误:', e)
"
```

---

**就这么简单！忽略其他复杂的文档，只看这个文件就够了。**
