#!/usr/bin/env python3
"""
nanobind Buffer 编译脚本

使用方法:
python3 setup.py build_ext --inplace
"""

from setuptools import setup, Extension

try:
    import nanobind
    
    print("✓ 找到 nanobind 版本:", nanobind.__version__)
    
    # 最简单正确的方法 - 使用nanobind的官方API
    # nanobind 2.8.0的正确做法是这样的
    ext_modules = [
        Extension(
            "pyfory_nb",
            sources=["pyfory_nb.cpp", "buffer.cpp"],
            include_dirs=[nanobind.include_dir()],
            language='c++',
            extra_compile_args=['-std=c++17', '-O3'],
            # 关键：不要静态链接，让Python运行时处理nanobind符号
            extra_link_args=['-Wl,--undefined,dynamic_lookup'],
        ),
    ]
    
    print("✓ nanobind 可用，将编译 C++ 扩展")
    
    setup(
        name="pyfory_nb",
        ext_modules=ext_modules,
        zip_safe=False,
        python_requires=">=3.8",
    )
    
except ImportError as e:
    print(f"✗ nanobind 导入失败: {e}")
    print("  尝试: pip install nanobind")
    setup(name="pyfory_nb")
    print(f"✗ nanobind 导入失败: {e}")
    print("  尝试: pip install nanobind")
    setup(name="pyfory_nb")
