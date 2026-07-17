from ctypes import *
import time
import os

ucrt = CDLL('msvcrt.dll')
counter = 0
print(f"PID: {os.getpid()} PPID: {os.getppid()}")
while True:
    ucrt.printf(b"Loop counter in C: %d\n"% counter)
    time.sleep(5)
    counter+=1