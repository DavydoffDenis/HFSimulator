import subprocess
import time
import datetime

def au_debuginfo_func(err_line_stream):
    print(f"Проскальзывание: {datetime.datetime.now().time()}")
    while True:
        read_d_char = process.stderr.read(2)
        if read_d_char == b'aU' or read_d_char == b'aO':
            print(f"Проскальзывание: {datetime.datetime.now().time()}")
        if not read_d_char: return
        time.sleep(0.01)

process = subprocess.Popen(["python3", "HFSimulator.py"], stderr=subprocess.PIPE)
read_d_char = process.stderr.read(2)
if read_d_char == b'aU' or read_d_char == b'aO':
    au_debuginfo_func(process.stderr)
while True:
    read_char = process.stderr.read(1)
    print(read_char)
    if read_char == b'\n':
        read_d_char = process.stderr.read(2)
        print(read_d_char)
        if read_d_char == b'aU' or read_d_char == b'aO':
            au_debuginfo_func(process.stderr)
    if not read_char: break
    time.sleep(0.01)
