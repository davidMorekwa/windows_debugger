import my_debugger

if __name__ == "__main__":
    debugger = my_debugger.Debugger()
    # pid = debugger.load("C:\\Windows\\System32\\calc.exe")
    pid = "11488"
    if pid is not None:
        debugger.attach(int(pid))
        thread_list = debugger.enumerate_threads()
        print(f"Thread list : {len(thread_list)}")
        for thread in thread_list:
            thread_context = debugger.get_thread_context(thread)
            if thread_context:
                print("*"*20)
                print(f"Dumping the registers for thread {thread} ")
                print("*"*20)
                print(f"Register RIP: {thread_context.Rip:#010x}")
                print(f"Register RBX: {thread_context.Rbx:#010x}")
                print(f"Register RDX: {thread_context.Rdx:#010x}")
                print(f"Register RCX: {thread_context.Rcx:#010x}")
                print(f"Register RAX: {thread_context.Rax:#010x}")
                print(f"Register RSP: {thread_context.Rsp:#010x}")
                print(f"Register RBP: {thread_context.Rbp:#010x}")
                
        debugger.detach()