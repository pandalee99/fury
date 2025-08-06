#!/usr/bin/env python3
"""
nanobind Buffer 编译脚本

使用方法:
python3 setup.py build_ext --inplace
"""

from setuptools import setup, Extension

try:
    import nanobind
    import os
    import glob
    
    print("✓ 找到 nanobind 版本:", nanobind.__version__)
    
    # 获取nanobind源代码 - 这是解决链接问题的关键
    nanobind_src_dir = os.path.join(os.path.dirname(nanobind.__file__), "src")
    nanobind_sources = glob.glob(os.path.join(nanobind_src_dir, "*.cpp"))
    
    print(f"✓ 找到nanobind源文件: {len(nanobind_sources)}个")
    
    # 包含nanobind源代码，这样就有完整的实现了
    ext_modules = [
        Extension(
            "pyfory_nb",
            sources=["pyfory_nb.cpp", "buffer.cpp"] + nanobind_sources,
            include_dirs=[
                nanobind.include_dir(),
                nanobind_src_dir  # 需要访问内部头文件
            ],
            language='c++',
            extra_compile_args=['-std=c++17', '-O3', '-fvisibility=hidden'],
            define_macros=[('NB_STATIC', None)],  # 静态链接nanobind
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
