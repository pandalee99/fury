#!/usr/bin/env python3
"""
PyFory Nanobind Extension 完整测试套件

测试包括：
1. 基础功能测试
2. Buffer API 完整性测试  
3. 性能对比测试
4. 兼容性验证
5. 边界情况和错误处理

运行: python3 test_nanobind.py
"""

import sys
import time
import tracemalloc
from typing import Optional

# 添加路径以便导入 pyfory
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入测试需要的模块
try:
    from pyfory.nanobind_ext import Buffer as NanobindBuffer
    NANOBIND_AVAILABLE = True
    print("✓ Nanobind Buffer 可用")
except ImportError as e:
    print(f"✗ Nanobind Buffer 不可用: {e}")
    NANOBIND_AVAILABLE = False

try:
    from pyfory._util import Buffer as CythonBuffer
    CYTHON_AVAILABLE = True
    print("✓ Cython Buffer 可用")
except ImportError:
    print("✗ Cython Buffer 不可用")
    CYTHON_AVAILABLE = False

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 基础功能测试 ===")
    
    if not NANOBIND_AVAILABLE:
        print("跳过：nanobind 不可用")
        return False
    
    try:
        # 测试 Buffer 创建
        buffer = NanobindBuffer.allocate(1024)
        assert buffer.size() >= 1024
        print("✓ Buffer.allocate() 工作正常")
        
        # 测试基本读写
        buffer.write_int32(12345)
        buffer.write_float(3.14159)
        buffer.write_bytes_and_size(b"Hello, nanobind!")
        
        buffer.reader_index = 0
        val1 = buffer.read_int32()
        val2 = buffer.read_float()
        val3 = buffer.read_bytes_and_size()
        
        assert val1 == 12345
        assert abs(val2 - 3.14159) < 1e-6
        assert val3 == b"Hello, nanobind!"
        print("✓ 基本读写操作正常")
        
        # 测试变长整数
        buffer.writer_index = 0
        buffer.reader_index = 0
        
        test_values = [0, 127, 128, 16383, 16384, -1, -128, -32768]
        for value in test_values:
            buffer.write_varint32(value)
        
        buffer.reader_index = 0
        for expected in test_values:
            actual = buffer.read_varint32()
            assert actual == expected, f"varint32: 期望 {expected}, 得到 {actual}"
        print("✓ 变长整数编码/解码正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 基础功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_types():
    """测试所有数据类型"""
    print("\n=== 数据类型测试 ===")
    
    if not NANOBIND_AVAILABLE:
        print("跳过：nanobind 不可用")
        return False
    
    try:
        buffer = NanobindBuffer.allocate(1024)
        
        # 测试所有数据类型
        test_data = [
            ("int8", -128, 127, buffer.put_int8, buffer.get_int8, 1),
            ("int16", -32768, 32767, buffer.put_int16, buffer.get_int16, 2),
            ("int32", -2147483648, 2147483647, buffer.put_int32, buffer.get_int32, 4),
            ("int64", -9223372036854775808, 9223372036854775807, buffer.put_int64, buffer.get_int64, 8),
            ("float", -3.14159, 3.14159, buffer.put_float, buffer.get_float, 4),
            ("double", -2.718281828459045, 2.718281828459045, buffer.put_double, buffer.get_double, 8),
        ]
        
        offset = 0
        for type_name, min_val, max_val, put_func, get_func, size in test_data:
            # 测试最小值和最大值
            for test_val in [min_val, 0, max_val]:
                put_func(offset, test_val)
                read_val = get_func(offset)
                
                if type_name in ["float", "double"]:
                    assert abs(read_val - test_val) < 1e-10, f"{type_name}: {test_val} != {read_val}"
                else:
                    assert read_val == test_val, f"{type_name}: {test_val} != {read_val}"
                
                offset += size
        
        print("✓ 所有数据类型读写正常")
        return True
        
    except Exception as e:
        print(f"✗ 数据类型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    if not NANOBIND_AVAILABLE:
        print("跳过：nanobind 不可用")
        return False
    
    try:
        # 测试空 Buffer
        empty_buffer = NanobindBuffer(b"")
        assert empty_buffer.size() == 0
        print("✓ 空 Buffer 创建正常")
        
        # 测试边界检查
        small_buffer = NanobindBuffer.allocate(4)
        try:
            small_buffer.put_int64(0, 12345)  # 需要8字节但只有4字节
            print("✗ 边界检查失败：应该抛出异常")
            return False
        except Exception:
            print("✓ 边界检查正常")
        
        # 测试自动扩容
        auto_buffer = NanobindBuffer.allocate(16)
        large_data = b"A" * 1000
        auto_buffer.write_bytes(large_data)
        assert auto_buffer.size() >= 1000
        print("✓ 自动扩容正常")
        
        # 测试内存重用
        reuse_buffer = NanobindBuffer.allocate(100)
        reuse_buffer.reserve(2048)
        assert reuse_buffer.size() >= 2048
        print("✓ 内存预留正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 边界情况测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_comparison():
    """性能对比测试"""
    print("\n=== 性能对比测试 ===")
    
    if not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE):
        print("跳过：需要 nanobind 和 Cython 都可用")
        return True
    
    def benchmark_buffer_operations(buffer_class, iterations=10000):
        """基准测试 Buffer 操作"""
        buffer = buffer_class.allocate(iterations * 20)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            buffer.write_int32(i)
            buffer.write_float(i * 3.14159)
            buffer.write_varint32(i - 5000)  # 包含负数
        end_time = time.perf_counter()
        
        return end_time - start_time, buffer.writer_index
    
    try:
        iterations = 50000
        print(f"基准测试 {iterations} 次操作...")
        
        # 测试 nanobind
        nb_time, nb_bytes = benchmark_buffer_operations(NanobindBuffer, iterations)
        print(f"Nanobind: {nb_time:.4f}s, {nb_bytes} 字节")
        
        # 测试 Cython
        cy_time, cy_bytes = benchmark_buffer_operations(CythonBuffer, iterations)
        print(f"Cython:   {cy_time:.4f}s, {cy_bytes} 字节")
        
        # 比较结果
        if nb_bytes == cy_bytes:
            speedup = cy_time / nb_time
            if speedup > 1.0:
                print(f"🚀 Nanobind 比 Cython 快 {speedup:.2f}x")
            else:
                print(f"📊 Cython 比 Nanobind 快 {1/speedup:.2f}x")
        else:
            print(f"⚠️ 输出字节数不同: nanobind={nb_bytes}, cython={cy_bytes}")
        
        return True
        
    except Exception as e:
        print(f"✗ 性能对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility():
    """兼容性测试"""
    print("\n=== 兼容性测试 ===")
    
    if not (NANOBIND_AVAILABLE and CYTHON_AVAILABLE):
        print("跳过：需要 nanobind 和 Cython 都可用")
        return True
    
    try:
        # 用 nanobind 写入数据
        nb_buffer = NanobindBuffer.allocate(1024)
        test_values = [12345, -67890, 3.14159, 2.718281828459045]
        
        nb_buffer.write_int32(test_values[0])
        nb_buffer.write_varint32(test_values[1])
        nb_buffer.write_float(test_values[2])
        nb_buffer.write_double(test_values[3])
        nb_buffer.write_bytes_and_size(b"compatibility test")
        
        # 获取原始数据
        raw_data = nb_buffer.get_bytes(0, nb_buffer.writer_index)
        print(f"nanobind 写入 {len(raw_data)} 字节")
        
        # 用 Cython 读取数据
        cy_buffer = CythonBuffer(raw_data)
        read_values = [
            cy_buffer.read_int32(),
            cy_buffer.read_varint32(),
            cy_buffer.read_float(),
            cy_buffer.read_double(),
            cy_buffer.read_bytes_and_size()
        ]
        
        # 验证兼容性
        expected = test_values + [b"compatibility test"]
        all_passed = True
        
        for i, (exp, act) in enumerate(zip(expected, read_values)):
            if isinstance(exp, float):
                passed = abs(exp - act) < 1e-10
            else:
                passed = exp == act
            
            status = "✓" if passed else "✗"
            print(f"  {status} 值 {i}: {exp} == {act}")
            
            if not passed:
                all_passed = False
        
        if all_passed:
            print("✓ nanobind 和 Cython 完全兼容")
        else:
            print("✗ 兼容性测试失败")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_usage():
    """内存使用测试"""
    print("\n=== 内存使用测试 ===")
    
    if not NANOBIND_AVAILABLE:
        print("跳过：nanobind 不可用")
        return True
    
    try:
        tracemalloc.start()
        
        # 创建大量 Buffer 对象
        buffers = []
        for i in range(1000):
            buffer = NanobindBuffer.allocate(1024)
            buffer.write_int32(i)
            buffers.append(buffer)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"内存使用: 当前 {current/1024/1024:.1f}MB, 峰值 {peak/1024/1024:.1f}MB")
        print("✓ 内存使用测试完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 内存使用测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("PyFory Nanobind Extension 完整测试套件")
    print("=" * 50)
    
    tests = [
        ("基础功能", test_basic_functionality),
        ("数据类型", test_data_types),
        ("边界情况", test_edge_cases),
        ("性能对比", test_performance_comparison),
        ("兼容性", test_compatibility),
        ("内存使用", test_memory_usage),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！nanobind Buffer 工作正常")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
