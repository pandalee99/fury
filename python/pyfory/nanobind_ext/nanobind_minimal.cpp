#include <nanobind/nanobind.h>
#include <Python.h>

// 提供nanobind需要的最小stub实现
namespace nanobind {
namespace detail {

// 错误处理函数
void chain_error(handle h, const char* fmt, ...) noexcept {
    PyErr_SetString(PyExc_RuntimeError, fmt);
}

// 类型转换函数 - 添加正确的noexcept声明
bool load_i32(PyObject* src, uint8_t flags, int32_t* out) noexcept {
    if (PyLong_Check(src)) {
        long val = PyLong_AsLong(src);
        if (val == -1 && PyErr_Occurred()) {
            return false;
        }
        *out = (int32_t)val;
        return true;
    }
    return false;
}

bool load_u32(PyObject* src, uint8_t flags, uint32_t* out) noexcept {
    if (PyLong_Check(src)) {
        unsigned long val = PyLong_AsUnsignedLong(src);
        if (val == (unsigned long)-1 && PyErr_Occurred()) {
            return false;
        }
        *out = val;
        return true;
    }
    return false;
}

bool load_i64(PyObject* src, uint8_t flags, int64_t* out) noexcept {
    if (PyLong_Check(src)) {
        long long val = PyLong_AsLongLong(src);
        if (val == -1 && PyErr_Occurred()) {
            return false;
        }
        *out = val;
        return true;
    }
    return false;
}

bool load_f32(PyObject* src, uint8_t flags, float* out) noexcept {
    if (PyFloat_Check(src)) {
        *out = (float)PyFloat_AsDouble(src);
        return true;
    }
    return false;
}

bool load_f64(PyObject* src, uint8_t flags, double* out) noexcept {
    if (PyFloat_Check(src)) {
        *out = PyFloat_AsDouble(src);
        return true;
    }
    return false;
}

} // namespace detail
} // namespace nanobind
