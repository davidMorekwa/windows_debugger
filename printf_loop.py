from ctypes import *
import time

msvcrt = cdll.msvcrt
counter = 0

while True:
    msvcrt.printf(b"Loop counter in C: %d\n"% counter)
    time.sleep(5)
    counter+=1