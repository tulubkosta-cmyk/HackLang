#!/usr/bin/env python3
import sys
import os
from src.repl import repl, run_file

if __name__ == '__main__':
    lib_path = os.path.join(os.path.expanduser("~"), ".hacklang", "lib")
    if len(sys.argv) > 1:
        run_file(sys.argv[1], lib_path)
    else:
        repl(lib_path)