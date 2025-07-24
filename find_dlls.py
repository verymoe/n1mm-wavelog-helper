#!/usr/bin/env python3
import os
import sys
import glob

def find_ssl_dlls():
    conda_root = os.path.dirname(sys.executable)
    dll_dirs = [
        os.path.join(conda_root, 'DLLs'),
        os.path.join(conda_root, 'Library', 'bin'),
        conda_root
    ]
    
    ssl_dlls = ['libssl-3-x64.dll', 'libcrypto-3-x64.dll', 'libffi*.dll', 'libmpdec*.dll']
    
    found_dlls = []
    for dll_dir in dll_dirs:
        if os.path.exists(dll_dir):
            for pattern in ssl_dlls:
                matches = glob.glob(os.path.join(dll_dir, pattern))
                found_dlls.extend(matches)
    
    return found_dlls

if __name__ == "__main__":
    dlls = find_ssl_dlls()
    for dll in dlls:
        print(dll)