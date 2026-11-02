"""Compile URL/body regular expressions with the host ICU library, not Python re.

QX's parser/engine is not public. ICU is a stricter, relevant iOS-family static
check; this is explicitly not a claim to run the proprietary QX engine.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import re


class ICURegex:
    def __init__(self):
        path = ctypes.util.find_library("icucore") or ctypes.util.find_library("icui18n")
        if not path:
            raise RuntimeError("找不到系统 ICU；macOS 自带，Ubuntu 可使用 libicu-dev")
        self.lib = ctypes.CDLL(path)
        versions = [""] + [f"_{n}" for n in range(100, 49, -1)]
        def symbol(name):
            for suffix in versions:
                try:
                    return getattr(self.lib, name + suffix)
                except AttributeError:
                    continue
            raise RuntimeError(f"ICU 缺少 {name}: {path}")
        self.open = symbol("uregex_open")
        self.open.restype = ctypes.c_void_p
        self.open.argtypes = [ctypes.POINTER(ctypes.c_uint16), ctypes.c_int32,
                              ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int32)]
        self.close = symbol("uregex_close")
        self.close.argtypes = [ctypes.c_void_p]
        self.error_name = symbol("u_errorName")
        self.error_name.restype = ctypes.c_char_p
        self.error_name.argtypes = [ctypes.c_int32]
        self.set_text = symbol("uregex_setText")
        self.set_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint16), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.looking_at = symbol("uregex_lookingAt")
        self.looking_at.restype = ctypes.c_int8
        self.looking_at.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.hit_end = symbol("uregex_hitEnd")
        self.hit_end.restype = ctypes.c_int8
        self.hit_end.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int32)]
        self._compiled = {}
        self._text_buffers = {}
        self.library = path

    def prefix_viable(self, pattern: str, prefix: str):
        """Whether a URL prefix can reach a rule (used only to trace MITM scope)."""
        handle = self._compiled.get(pattern)
        status = ctypes.c_int32(0)
        if handle is None:
            data = pattern.encode("utf-16-le")
            array = (ctypes.c_uint16 * (len(data) // 2)).from_buffer_copy(data)
            handle = self.open(array, len(data) // 2, 0, ctypes.create_string_buffer(128), ctypes.byref(status))
            if status.value > 0 or not handle:
                return False
            self._compiled[pattern] = handle
        data = prefix.encode("utf-16-le")
        array = (ctypes.c_uint16 * (len(data) // 2)).from_buffer_copy(data)
        self._text_buffers[pattern] = array
        self.set_text(handle, array, len(data) // 2, ctypes.byref(status))
        matched = self.looking_at(handle, 0, ctypes.byref(status))
        partial = self.hit_end(handle, ctypes.byref(status))
        return status.value <= 0 and bool(matched or partial)

    def __del__(self):
        for handle in getattr(self, "_compiled", {}).values():
            self.close(handle)

    def error(self, pattern: str) -> str | None:
        data = pattern.encode("utf-16-le")
        array = (ctypes.c_uint16 * (len(data) // 2)).from_buffer_copy(data)
        # UParseError is 72 bytes on the supported ABIs. Reserve extra space.
        parse_error = ctypes.create_string_buffer(128)
        status = ctypes.c_int32(0)
        handle = self.open(array, len(data) // 2, 0, parse_error, ctypes.byref(status))
        if handle:
            self.close(handle)
        if status.value > 0:
            return self.error_name(status.value).decode("ascii")
        return None
