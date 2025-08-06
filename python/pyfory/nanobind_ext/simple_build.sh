#!/bin/bash
# 最简单的编译脚本

echo "🔨 开始编译 nanobind Buffer..."

# 检查文件是否存在
if [ ! -f "pyfory_nb.cpp" ]; then
    echo "❌ 找不到 pyfory_nb.cpp"
    exit 1
fi

if [ ! -f "buffer.cpp" ]; then
    echo "❌ 找不到 buffer.cpp"
    exit 1
fi

# 方法1：尝试使用 nanobind cmake
echo "尝试方法1: nanobind cmake"
if python3 -m nanobind.cmake --module pyfory_nb pyfory_nb.cpp buffer.cpp 2>/dev/null; then
    echo "✅ 方法1成功!"
    exit 0
fi

# 方法2：手动编译
echo "尝试方法2: 手动编译"
EXT_SUFFIX=$(python3-config --extension-suffix)
if [ -z "$EXT_SUFFIX" ]; then
    EXT_SUFFIX=".so"
fi

c++ -O3 -Wall -shared -std=c++17 -fPIC \
    $(python3-config --includes) \
    $(python3 -c "import nanobind; print('-I' + nanobind.include_dir())") \
    pyfory_nb.cpp buffer.cpp \
    -o "pyfory_nb${EXT_SUFFIX}"

if [ $? -eq 0 ]; then
    echo "✅ 方法2成功!"
    echo "编译完成: pyfory_nb${EXT_SUFFIX}"
else
    echo "❌ 编译失败"
    exit 1
fi
