#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import json

def get_cmake_path():
    return shutil.which("cmake")

def get_module_dir(dir):
    return os.path.join(dir, "malt_modules/")

def build_module(module):
    original_wd = os.getcwd()

    install_prefix = get_module_dir(original_wd)
    json_path = os.path.join(original_wd, ".malt.json")
    modules_j = json.loads(open(json_path, encoding="utf8").read())

    installed = modules_j["installed_modules"]

    cmake_dir = os.path.join(get_module_dir(original_wd), "modules/", module.name)

    mod_exists = False
    for mod_name in installed:
        if (mod_name == module.name):
            mod_exists = True
            cmake_dir = os.path.join(original_wd, installed[mod_name]["cmake_path"])

    if mod_exists and os.path.exists(cmake_dir):
        os.chdir(cmake_dir)
    else:
        os.makedirs(cmake_dir)
        os.chdir(cmake_dir)
        proc = subprocess.Popen([get_cmake_path(), "-DCMAKE_INSTALL_PREFIX=" + install_prefix, module.path])
        result = proc.wait()
        if result != 0:
            shutil.rmtree(cmake_dir)
            return False

    proc = subprocess.Popen([get_cmake_path(), "--build", ".", "--", "-j16"], stdout = subprocess.PIPE)
    res = proc.wait()
    if res != 0:
        shutil.rmtree(cmake_dir)
        return False

    print("Built module {}".format(module.name))

    proc = subprocess.Popen([get_cmake_path(), "--build", ".", "--", "install"], stdout = subprocess.PIPE)
    res = proc.wait()
    if res != 0:
        shutil.rmtree(cmake_dir)
        return False

    print("Installed module {}".format(module.name))

    installed[module.name] = {}
    installed[module.name]["src_path"] = os.path.join("./", os.path.relpath(module.path, original_wd))
    installed[module.name]["cmake_path"] = os.path.join("./", os.path.relpath(cmake_dir, original_wd))
    json_text = json.dumps(modules_j, indent=2)
    open(json_path, "w", encoding="utf8").write(json_text)

    os.chdir(original_wd)
    return True
