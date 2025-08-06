#!/usr/bin/env python3
"""
nanobind Buffer 编译脚本

使用方法:
pip install scikit-build-core[pyproject]
python3 -m pip install . --no-build-isolation

或者继续使用 setuptools 尝试:
python3 setup.py build_ext --inplace
"""

from setuptools import setup, Extension
import subprocess
import sys

try:
    import nanobind
    
    # 尝试使用CMake的方式来编译（推荐）
    print("✓ nanobind 可用，建议使用 CMake 编译:")
    print("  pip install scikit-build-core[pyproject]")
    print("  python3 -m pip install . --no-build-isolation")
    print("")
    print("  当前正在尝试 setuptools 方式...")
    
    # 简单的解决方案：尝试手动链接 nanobind
    ext_modules = [
        Extension(
            "pyfory_nb",
            ["pyfory_nb.cpp", "buffer.cpp"],
            include_dirs=[nanobind.include_dir()],
            language='c++',
            extra_compile_args=['-std=c++17', '-O3', '-fvisibility=hidden'],
            define_macros=[('NB_STATIC', None)],  # 静态链接 nanobind
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
