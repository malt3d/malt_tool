#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import json
import malt_registry

def get_cmake_path():
    return shutil.which("cmake")

def test_module(module):
    original_wd = os.getcwd()
    registry = malt_registry.module_registry(original_wd)

    cmake_dir = ""
    mod_exists = False
    for mod_name in registry.installed:
        if (mod_name == module.name):
            mod_exists = True
            cmake_dir = os.path.normpath(os.path.join(original_wd, registry.installed[mod_name]["cmake_path"]))

    if not mod_exists:
        raise("Module to test is not installed!")

    os.chdir(cmake_dir)

    proc = subprocess.Popen([get_cmake_path(), "--build", ".", "--", "test"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    res = proc.wait()
    if res != 0:
        print("Tests failed")
        return (False, proc.stdout.read())

    os.chdir(original_wd)
    return (True, "")


def build_module(module, **kwargs):
    silent = False

    if "silent" in kwargs and kwargs["silent"]:
        silent = True

    original_wd = os.getcwd()
    registry = malt_registry.module_registry(original_wd)

    cmake_dir = os.path.join(registry.modules_path(), "modules/", module.name)

    mod_exists = False
    for mod_name in registry.installed:
        if (mod_name == module.name):
            mod_exists = True
            cmake_dir = os.path.normpath(os.path.join(original_wd, registry.installed[mod_name]["cmake_path"]))

    if mod_exists and os.path.exists(cmake_dir) and "regen" not in kwargs:
        os.chdir(cmake_dir)
    else:
        print("Generating module {}".format(module.name))
        if not os.path.exists(cmake_dir):
            os.makedirs(cmake_dir)
        os.chdir(cmake_dir)

        proc = subprocess.Popen(
                [get_cmake_path(),
                 "-DCMAKE_BUILD_TYPE=Debug",
                 "-DCMAKE_PREFIX_PATH=/home/fatih/rtk_build/",
                 "-DCMAKE_INSTALL_PREFIX=" + registry.modules_path(),
                 module.path],
            stdout = subprocess.PIPE
        )

        result = proc.wait()

        if result != 0:
            shutil.rmtree(cmake_dir)
            return False

        if not silent:
            print("Generated module {}".format(module.name))

    proc = subprocess.Popen([get_cmake_path(), "--build", ".", "--", "-j16"], stdout = subprocess.PIPE)
    res = proc.wait()
    if res != 0:
        shutil.rmtree(cmake_dir)
        return False

    if not silent:
        print("Built module {}".format(module.name))

    proc = subprocess.Popen([get_cmake_path(), "--build", ".", "--", "install"], stdout = subprocess.PIPE)
    res = proc.wait()
    if res != 0:
        shutil.rmtree(cmake_dir)
        return False

    if not silent:
        print("Installed module {}".format(module.name))

    registry.add_installed_module(module, cmake_dir)
    registry.save()

    os.chdir(original_wd)
    return True
