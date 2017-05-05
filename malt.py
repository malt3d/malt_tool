#!/usr/bin/env python3

import sys
import module_tools

def main():
    cmd = sys.argv[1]
    if cmd == "module":
        module_tools.handle(sys.argv[2:])
    return

if __name__ == '__main__':
    main()