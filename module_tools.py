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
    src = ""
    _internal_ref = None

class malt_module:
    _json_data = {}
    path = ""

    def __init__(self, path):
        self.path = os.path.normpath(os.path.join(os.getcwd(), path))
        module_def = open(os.path.join(path, "module.json"), encoding="utf-8")
        self._json_data = json.loads(module_def.read())
        module_def.close()

        if "dependencies" not in self._json_data:
            self._json_data["dependencies"] = []

        if "components" not in self._json_data:
            self._json_data["components"] = {}

    @property
    def name(self):
        return self._json_data["name"]

    @name.setter
    def name(self, name):
        self._json_data["name"] = name

    @property
    def human_name(self):
        return self._json_data["readable_name"]

    @human_name.setter
    def human_name(self, name):
        self._json_data["readable_name"] = name

    @property
    def version(self):
        return self._json_data["version"]

    @version.setter
    def version(self, name):
        self._json_data["version"] = name

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
            dep._internal_ref = elem
            deps.append(dep)
        return deps

    def set_dependency(self, mod):
        exists = None
        for dep in self.depends:
            if dep.name == mod.name:
                exists = dep
                break

        if exists is not None:
            exists._internal_ref["name"] = mod.name
            exists._internal_ref["version"] = mod.version
            exists._internal_ref["src"] = mod.src
            return

        self._json_data["dependencies"].append({
            "name" : mod.name,
            "version" : mod.version,
            "src" : mod.src
        })

    def build(self, **kwargs):
        build_module.build_module(self, **kwargs)

    def test(self, **kwargs):
        return build_module.test_module(self)

    def save(self):
        open(os.path.join(self.path, "module.json"), "w+", encoding="utf-8").write(json.dumps(self._json_data, indent=2))


def parse_namespaces(comps):
    res = {
        "components" : [],
        "children" : {}
    }

    for comp in comps:
        sp = comp.name.split("::")
        final = res
        for ns in sp[:-1]:
            if ns not in final["children"]:
                final["children"][ns] = { "components" : [], "children" : {} }
            final = final["children"][ns]
        final["components"].append(sp[-1])
    return res

def generate_files(mod):
    include_dir = os.path.normpath(os.path.join(mod.path, "include/" + mod.name))
    src_dir = os.path.normpath(os.path.join(mod.path, "src/"))

    if not os.path.exists(include_dir):
        os.makedirs(include_dir)
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    from jinja2 import Template

    renderable = {
        "module_name" : mod.name,
        "components" : mod.components,
        "fwd_decls" : parse_namespaces(mod.components),
        "dependencies" : mod.depends
    }

    with open(os.path.join(include_dir, "module.hpp"), "w+", encoding="utf-8") as module_header:
        source = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/module/module_header.j2"), encoding="utf-8").read()
        template = Template(source, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
        module_header.write(template.render(renderable))

    with open(os.path.join(src_dir, "module.cpp"), "w+", encoding="utf-8") as module_src:
        source = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/module/module_impl.j2"), encoding="utf-8").read()
        template = Template(source, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
        module_src.write(template.render(renderable))

    with open(os.path.join(mod.path, "CMakeLists.txt"), "w+", encoding="utf-8") as cmake_file:
        source = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/module/CMakeLists.j2"), encoding="utf-8").read()
        template = Template(source, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
        cmake_file.write(template.render(renderable))

    with open(os.path.join(mod.path, mod.name + "-config.cmake"), "w+", encoding="utf-8") as cmake_file:
        source = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/module/config.cmake.j2"), encoding="utf-8").read()
        template = Template(source, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
        cmake_file.write(template.render(renderable))



def new_module():
    if os.path.exists(os.path.join(os.getcwd(), "module.json")):
        raise(Exception("Module already exists!"))

    with open(os.path.join(os.getcwd(), "module.json"), "w+") as file:
        file.write("{}")

    mod = malt_module(".")
    mod.name = input("module name: ")
    mod.human_name = input("human readable name: ")
    mod.version = input("module version: ")

    core_dep = module_decl()
    core_dep.name = "malt_core"
    core_dep.version = "^0.1.0"
    core_dep.src = "malt3d/malt_core"

    mod.set_dependency(core_dep)

    generate_files(mod)
    mod.save()

def info(module):
    print(module.name)
    print("Components: ")
    for comp in module.components:
        print("    + {}".format(comp.name))
    print("Dependencies: ")
    for dep in module.depends:
        print("    + {}".format(dep.name))

def handle(args):
    if args[0] == "new":
        new_module()
        return

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
        generate_files(module)

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
