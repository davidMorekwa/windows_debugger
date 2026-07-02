from ctypes import *
from my_debugger_defines import *

kernel32 = WinDLL('kernel32', use_last_error=True)

class Debugger():
    def __init__(self):
        self.h_process = None
        self.pid = None
        self.debugger_active = False

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
            self.run()
        else:
            error = get_last_error()
            print(f"[-] Unable to attach to process. Error: {error}")

    def get_debug_event(self):
        """
        handles debug events and ensures the debugging continues
        """
        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE
        print("calling WaitForDebugEvent()")
        is_event_thrown = kernel32.WaitForDebugEvent(byref(debug_event), INFINITE)
        print(f"is_event_thrown: {is_event_thrown}")
        if is_event_thrown:
            input("press enter to continue...") # simulate debugging process
            # self.debugger_active = False
            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)
        else:
            e = get_last_error()
            print(f"Waiting.... {e}")
    
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
        if h_thread is not None:
            return h_thread
        else:
            e = get_last_error()
            print(f"[-] Could not obtain handle on thread. Error {e}")
            return False
    
    def enumerate_threads(self):
        """
        Enumerate threads of a process and return list of threads
        """
        thread_entry = THREADENTRY32()
        thread_list = [] # list of thread Ids
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)
        if snapshot is not None:
            thread_entry.dwSize = sizeof(thread_entry)
            is_success = kernel32.Thread32First(snapshot, byref(thread_entry))
            while is_success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                    is_success = kernel32.Thread32Next(snapshot, byref(thread_entry))
            kernel32.CloseHandle(snapshot)
            return thread_list
        else:
            e = get_last_error()
            print(f"Error enumerating threads: {e}")
    
    def get_thread_context(self, thread_id):
        """
        Return register values
        """
        context = CONTEXT()
        context.ContextFlags = CONTEXT_FULL # CONTEXT_FULL or CONTEXT_DEBUG_REGISTER
        h_thread = self.open_thread(thread_id)
        if kernel32.GetThreadContext(h_thread, byref(context)):
            kernel32.CloseHandle(h_thread)
            return context
        else:
            e = get_last_error()
            print(f"Error getting thread context: {e}")
            return False

    def run(self):
        """
        main entry point of class
        """
        while self.debugger_active == True:
            print("waiting for debug events")
            self.get_debug_event()
