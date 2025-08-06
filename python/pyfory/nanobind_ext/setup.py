#!/usr/bin/env python3
"""
nanobind Buffer 编译脚本

使用方法:
python3 setup.py build_ext --inplace
"""

from setuptools import setup

try:
    import nanobind
    from nanobind.setup_helpers import Pybind11Extension, build_ext
    
    ext_modules = [
        Pybind11Extension(
            "pyfory_nb",
            ["pyfory_nb.cpp", "buffer.cpp"],
            include_dirs=[nanobind.include_dir()],
            language='c++',
            cxx_std=17,
        ),
    ]
    
    print("✓ nanobind 可用，将编译 C++ 扩展")
    
    setup(
        name="pyfory_nb",
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        zip_safe=False,
        python_requires=">=3.8",
    )
    
except ImportError as e:
    print(f"✗ nanobind 导入失败: {e}")
    print("  尝试: pip install nanobind")
    setup(name="pyfory_nb")
