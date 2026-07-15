import my_debugger

def dump_register_content(id_thread, ctx_thread):
    print("*"*20)
    print(f"Dumping the registers for thread {id_thread} ")
    print("*"*20)
    if ctx_thread:
        print(f"Register RIP: {ctx_thread.Rip:#010x}")
        print(f"Register RBX: {ctx_thread.Rbx:#010x}")
        print(f"Register RDX: {ctx_thread.Rdx:#010x}")
        print(f"Register RCX: {ctx_thread.Rcx:#010x}")
        print(f"Register RAX: {ctx_thread.Rax:#010x}")
        print(f"Register RSP: {ctx_thread.Rsp:#010x}")
        print(f"Register RBP: {ctx_thread.Rbp:#010x}")


if __name__ == "__main__":
    debugger = my_debugger.Debugger()
    # pid = debugger.load("C:\\Windows\\System32\\calc.exe")
    pid = "9440"
    if pid is not None:
        debugger.attach(int(pid))
        thread_list = debugger.enumerate_threads()
        print(f"Thread list : {len(thread_list)}")
        for thread in thread_list:
            thread_context = debugger.get_thread_context(thread)
            dump_register_content(id_thread=thread, ctx_thread=thread_context)
        debugger.detach()
