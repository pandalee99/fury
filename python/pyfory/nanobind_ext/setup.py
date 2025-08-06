#!/usr/bin/env python3
"""
nanobind Buffer 编译脚本

使用方法:
python3 setup.py build_ext --inplace
"""

from setuptools import setup, Extension

try:
    import nanobind
    
    # 使用标准的 setuptools Extension，不依赖 setup_helpers
    ext_modules = [
        Extension(
            "pyfory_nb",
            ["pyfory_nb.cpp", "buffer.cpp"],
            include_dirs=[nanobind.include_dir()],
            language='c++',
            extra_compile_args=['-std=c++17', '-O3'],
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
