#!/usr/bin/env python3

import sys
import module_tools
import malt_registry

def main():
    cmd = sys.argv[1]
    if cmd == "module":
        module_tools.handle(sys.argv[2:])

    if cmd == "init":
        reg = malt_registry.module_registry.create()

    if cmd == "libs":
        reg = malt_registry.module_registry()

        for lib in reg.library_prefixes:
            print(lib)


    return

if __name__ == '__main__':
    main()