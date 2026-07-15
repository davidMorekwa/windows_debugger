import my_debugger
import shlex
import subprocess
import sys

def startup_script():
    script_path = r"C:\Users\User\CYBERSECURITY\grey_hat_python\startup-script.ps1"
    script_command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
    res = subprocess.run(script_command, text=True, capture_output=True, check=False)
    if res.returncode == 0:
        print(f"Process pid: {res.stdout}")
        return res.stdout
    else:
        print(f"Failed to execute startup command: {res.stderr}")
        sys.exit()

def dump_register_content(dbg):
    thread_list = dbg.enumerate_threads()
    print(f"Thread list : {len(thread_list)}")
    for thread in thread_list:
        h_thread = dbg.open_thread(thread)
        ctx_thread = dbg.get_thread_context(h_thread)
        print("*"*20)
        print(f"Dumping the registers for thread {thread} ")
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
    pid = startup_script()
    debugger.attach(int(pid))
    # dump_register_content(debugger)
    address = debugger.func_resolve(b"msvcrt.dll", b"printf")
    print(f"printf function address: {address:#010x}")
    debugger.set_soft_breakpoint(address)
    debugger.run()
    debugger.detach()
        
