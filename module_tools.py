#!/usr/bin/env python3

import os
import json
import sys

import list_components
import list_messages
import build_module
import malt_registry

class component_decl:
    name = ""

class module_decl:
    name = ""
    version = ""

class malt_module:
    _json_data = {}
    path = ""
    def __init__(self, path):
        self.path = os.path.join(os.getcwd(), path)
        module_def = open(os.path.join(path, "module.json"), encoding="utf-8")
        self._json_data = json.loads(module_def.read())

    @property
    def name(self):
        return self._json_data["name"]

    @name.setter
    def name(self, name):
        self._json_data["name"] = name

    @property
    def components(self):
        comps = []
        for elem in self._json_data["components"]:
            res = component_decl()
            if isinstance(elem, dict):
                res.name = elem["name"]
            if isinstance(elem, str):
                res.name = elem
            comps.append(res)
        return comps

    @property
    def depends(self):
        deps = []
        for elem in self._json_data["dependencies"]:
            dep = module_decl()
            if isinstance(elem, dict):
                dep.name = elem["name"]
            if isinstance(elem, str):
                dep.name = elem
            deps.append(dep)
        return deps

    def build(self, **kwargs):
        build_module.build_module(self, **kwargs)

    def test(self, **kwargs):
        return build_module.test_module(self)

def info(module):
    print(module.name)
    print("Components: ")
    for comp in module.components:
        print("    + {}".format(comp.name))
    print("Dependencies: ")
    for dep in module.depends:
        print("    + {}".format(dep.name))

def handle(args):
    mods = malt_registry.module_registry(os.getcwd())

    if args[0] == "install":
        for mod_name in mods.installed:
            module = malt_module(mods.installed[mod_name]["src_path"])
            module.build()
        return

    module = malt_module(args[1])

    if args[0] == "info":
        info(module)

    if args[0] == "regen":
        module.build(regen=True)

    if args[0] == "build":
        for dependency in module.depends:
            dep = malt_module(mods.find_module(dependency.name))
            dep.build()
        module.build()

    if args[0] == "test":
        (res, msg) = module.test()
        if res:
            print ("All tests passed!")
        else:
            sys.stdout.buffer.write(msg)

    if args[0] == "messages":
        module.build(silent=True)
        file = mods.get_library_file(module)

        res = list_messages.list_messages(file)

        print("Messages dispatched by {}:".format(module.name))
        for (msg, args) in res:
            output = '    + {}({})'.format(msg, ", ".join(args))
            print(output)

        return

def main():
    module = malt_module(sys.argv[1])
    info(module)

if __name__ == '__main__':
    main()
