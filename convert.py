import os
import sys
import subprocess
if len(sys.argv) != 3:
    print("Incorrect args. Example:")
    print("python3 convert.py dataset/ogg/ dataset/wav/")
    exit(1)

source = sys.argv[1]
dest = sys.argv[2]
if source[-1] != '/':
    source += '/'
if dest[-1] != '/':
    dest += '/'
files = os.listdir(source)
for i in files:
    if i[-4:] == '.ogg':
        subprocess.call(["ffmpeg", "-n", "-i", source + i, dest + i[:-4] + '.wav'])
