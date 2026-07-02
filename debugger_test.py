import my_debugger

if __name__ == "__main__":
    debugger = my_debugger.Debugger()
    # pid = debugger.load("C:\\Windows\\System32\\calc.exe")
    pid = "10604"
    if pid is not None:
        debugger.attach(int(pid))
        thread_list = debugger.enumerate_threads()
        print(f"Thread list : {len(thread_list)}")
        debugger.detach()