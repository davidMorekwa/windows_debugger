from ctypes import *
from ctypes import wintypes
from my_debugger_defines import *

kernel32 = WinDLL('kernel32', use_last_error=True)

# DebugActiveProcess function
kernel32.DebugActiveProcess.argtypes = [wintypes.DWORD]
kernel32.DebugActiveProcess.restype = wintypes.BOOL

# DebugActiveProcessStop function
kernel32.DebugActiveProcessStop.argtypes = [wintypes.DWORD]
kernel32.DebugActiveProcessStop.restype = wintypes.BOOL

# WaitForDebugEvent function
kernel32.WaitForDebugEvent.argtypes = [POINTER(DEBUG_EVENT), wintypes.DWORD]
kernel32.WaitForDebugEvent.restype = wintypes.BOOL

# ContinueDebugEvent function
kernel32.ContinueDebugEvent.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
kernel32.ContinueDebugEvent.restype = wintypes.BOOL

# OpenProcess function
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE

# SuspendThread function
kernel32.SuspendThread.argtypes = [HANDLE]
kernel32.SuspendThread.restypes = DWORD

# ReadProcessMemory function
kernel32.ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, c_size_t, POINTER(c_size_t) ]
kernel32.ReadProcessMemory.restype = wintypes.BOOL

# WriteProcessmemory function
kernel32.WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, c_size_t, POINTER(c_size_t)]
kernel32.WriteProcessMemory.restype = wintypes.BOOL

# LoadLibraryA function
kernel32.LoadLibraryA.argtypes = [wintypes.LPCSTR]
kernel32.LoadLibraryA.restype = wintypes.HMODULE

# GetProcAddress function
kernel32.GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]
kernel32.GetProcAddress.restype = c_void_p

# CloseHandle function
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

# GetModuleHandle function
kernel32.GetModuleHandleA.argtypes = [wintypes.LPCSTR]
kernel32.GetModuleHandleA.restype = wintypes.HMODULE


