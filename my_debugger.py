from ctypes import *
from my_debugger_defines import *
from ctypes import wintypes
from windows_api_defs import kernel32

# kernel32 = WinDLL('kernel32', use_last_error=True)

class Debugger():
    def __init__(self):
        self.h_process = None
        self.pid = None
        self.debugger_active = False
        self.h_thread = None
        self.ctx_thread = None
        self.exception = None
        self.exception_address = None
        self.breakpoints = {}

    def load(self, path_to_exe):
        """
        Create a process to debug
        """
        creation_flag = DEBUG_PROCESS # set CREATE_NEW_CONSOLE to see GUI
        startupinfo = STARTUPINFO()
        processinfo = PROCESS_INFORMATION()
        startupinfo.dwSize = sizeof(startupinfo)
        startupinfo.wShowWindow = 0x0
        startupinfo.cb = sizeof(startupinfo)
        success = kernel32.CreateProcessA(
            None, # application name
            path_to_exe.encode("utf-8"), # command line
            None, # process attributes
            None, # thread attributes
            False, # inherit handles
            creation_flag, # creation flags
            None, # environment
            None, # current directory
            byref(startupinfo), # startup info
            byref(processinfo) # process information
        )
        if success:
            print("[+] Successfully launched process")
            print(f"[+] PID: {processinfo.dwProcessId}")
            return processinfo.dwProcessId
        else:
            print("[-] Failed to launch process")
            print(f"[-] Error: {get_last_error()}")
            return None
    
    def open_process(self, pid):
        """
        Returns a handle of the sepecified process, with highest level access privileges i.e. PROCESS_ALL_ACCESS
        """
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        return h_process
    
    def attach(self, pid):
        """
        obtain handle and attach to target process for debugging
        """
        print("getting process handle")
        self.h_process = self.open_process(pid)
        print("attaching debugger to process")
        is_attached = kernel32.DebugActiveProcess(pid)
        if is_attached:
            self.debugger_active = True
            self.pid = pid
            # self.run()
        else:
            error = get_last_error()
            print(f"[-] Unable to attach to process. Error: {error}")

    def run(self):
        """
        main entry point of class
        """
        while self.debugger_active == True:
            self.get_debug_event()

    def get_debug_event(self):
        """
        handles debug events and ensures the debugging continues
        """
        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE
        if kernel32.WaitForDebugEvent(byref(debug_event), INFINITE):
            self.h_thread = self.open_thread(debug_event.dwThreadId)
            print(f"Event Code {debug_event.dwDebugEventCode} ThreadId {debug_event.dwThreadId}")
            if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                print("Debug Event Exception detected")
                self.exception = debug_event.u.Exception.ExceptionRecord.ExceptionCode
                self.exception_address = debug_event.u.Exception.ExceptionRecord.ExceptionAddress
                self.ctx_thread = self.get_thread_context(self.h_thread)
                if self.exception == EXCEPTION_ACCESS_VIOLATION:
                    print("Access Violation Exception detected")
                elif self.exception == EXCEPTION_BREAKPOINT:
                    print(f"Breakpoint Exception detected at address {self.exception_address:#010x}")
                    continue_status = self.exception_breakpoint_handler()
                elif self.exception == EXCEPTION_GUARD_PAGE:
                    print("Guard Page Access Exception detected")
                elif self.exception == EXCEPTION_SINGLE_STEP:
                    print("Harware Breakpoint Exception detected")
            # input("press enter to continue...") # simulate debugging process
            # self.debugger_active = False
            kernel32.CloseHandle(self.h_thread)
            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)
        else:
            print("Waiting for debug events.....")
    
    def detach(self):
        """
        stops the debugger
        """
        is_stopped = kernel32.DebugActiveProcessStop(self.pid)
        if is_stopped:
            print('[*] Stopping the debugger')
            return True
        else:
            e = get_last_error()
            print(f"[-] An error occurred when detaching the debugger: {e}")

    def open_thread(self, thread_id):
        """
        obtain handle of specified thread
        """
        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)
        if h_thread is None:
            print(f"[-] Could not obtain handle on thread. Error {get_last_error()}")
            return False
        return h_thread
            
    def enumerate_threads(self):
        """
        Enumerate threads of a process and return list of thread_ids
        """
        print("Enumerating threads")
        thread_entry = THREADENTRY32()
        thread_list = [] # list of thread Ids
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)
        invalid_handle_value = INVALID_HANDLE_VALUE
        if snapshot != invalid_handle_value:
            thread_entry.dwSize = sizeof(thread_entry)
            is_success = kernel32.Thread32First(snapshot, byref(thread_entry))
            while is_success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                is_success = kernel32.Thread32Next(snapshot, byref(thread_entry))
            kernel32.CloseHandle(snapshot)
            print(f"Thread count: {len(thread_list)}")
            return thread_list
        else:
            e = get_last_error()
            print(f"Error enumerating threads: {e}")
    
    def suspend_thread(self, h_thread):
        """
        Suspend thread
        """
        sus = kernel32.SuspendThread(h_thread)
        if sus != INVALID_HANDLE_VALUE:
            print("Thread suspended")
            return sus
        else:
            e = get_last_error()
            print(f"An error occurred when suspending the thread: {e}")
            return False
    
    def get_thread_context(self, h_thread):
        """
        Return CONTEXT64 object of a thread
        """
        context = CONTEXT64()
        context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS
        self.suspend_thread(h_thread)
        if kernel32.GetThreadContext(h_thread, byref(context)):
            # kernel32.ResumeThread(h_thread)
            kernel32.CloseHandle(h_thread)
            return context
        else:
            print(f"Error getting thread context: {get_last_error()}")
            # kernel32.ResumeThread(h_thread)
            kernel32.CloseHandle(h_thread)
            return False

    def exception_breakpoint_handler(self):
        """
        Brekapoint handler
        """
        print(f"Inside the soft breakpoint exception handler function. Address {self.exception_address:#010x}")
        return DBG_CONTINUE

    def read_process_memory(self, address, length):
        """
        Read Process Memory
        """
        data = b""
        read_buffer = create_string_buffer(length)
        count = c_size_t()
        if not kernel32.ReadProcessMemory(self.h_process, address, read_buffer, length, byref(count)):
            print(f"Failed to read process memory: {get_last_error()}")
            return False
        else:
            data += read_buffer.raw
            return data
    
    def write_process_memory(self, address, data):
        """
        Write data to process memory
        """
        count = c_size_t()
        length = len(data)
        c_data = c_char_p(data[count.value:])
        if not kernel32.WriteProcessMemory(self.h_process, address, c_data, length, byref(count)):
            print(f"Failed to write to process memory: {get_last_error()}")
            return False
        else:
            print("Breakpoint added")
            return True

    def set_soft_breakpoint(self, address):
        """
        Set Soft Breakpoint at specified address
        """
        if address not in self.breakpoints.keys():
            try:
                # to set the soft breakpoint, read the data in the address and replace it with INT3 i.e. x\CC
                original_byte = self.read_process_memory(address, 1)
                print(f"Original bytes in address {address:#010x} is {str(original_byte)}")
                self.write_process_memory(address, b"\xCC")
                self.breakpoints[address] = (address, original_byte)
            except (OSError, ValueError, TypeError) as exc:
                print(f"Failed to set breakpoint: {exc}")
                return False
        return True
    
    def func_resolve(self, dll, function):
        """
        Get address of a function
        """
        # h_module = kernel32.LoadLibraryA(dll)
        h_module = kernel32.GetModuleHandleA(dll)
        if not h_module:
            print(f"Failed to get module handle: {get_last_error()}")
        address = kernel32.GetProcAddress(h_module, function)
        if not address:
            print(f"Failed to get process address: {get_last_error()}")
        kernel32.CloseHandle(h_module)
        return address