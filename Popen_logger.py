import subprocess
import time
import datetime

def au_debuginfo_func(err_line_stream):
    print(f"Проскальзывание: {datetime.datetime.now().time()}")
    while True:
        read_d_char = process.stderr.read(2)
        if read_d_char == b'aU':
            print(f"Проскальзывание: {datetime.datetime.now().time()}")
        if not read_char: return
        time.sleep(0.01)

process = subprocess.Popen(["python3", "HFSimulator.py"], stderr=subprocess.PIPE)
if process.stderr.read(2) == b'aU':
    au_debuginfo_func(process.stderr)
while True:
    read_char = process.stderr.read(1)
    print(read_char)
    if read_char == b'\n':
        read_d_char = process.stderr.read(2)
        print(read_d_char)
        if read_d_char == b'aU':
            au_debuginfo_func(process.stderr)
    if not read_char: break
    time.sleep(0.01)
