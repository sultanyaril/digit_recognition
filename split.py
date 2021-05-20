import os
import sys
import subprocess

if len(sys.argv) != 3:
    print("Incorrect args. Example:")
    print("python3 split.py dataset/wav/ dataset/splitted/")
    exit(1)
source = sys.argv[1]
dest = sys.argv[2]
if source[-1] != '/':
    source += '/'
if dest[-1] != '/':
    dest += '/'
files = os.listdir(source)
error_count = 0
for i in files:
    if i[-4:] == '.wav':
        call_text = ["python3", "vad.py", source + i.strip(), "0.1", "0.02", dest]
        print(call_text)
        if not subprocess.call(call_text):
            error_count += 1
print("\nERROR OCCURED: ", error_count)
