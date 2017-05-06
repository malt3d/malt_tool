import json
import os

class module_registry:
    def __init__(self, wd = os.getcwd()):
        self.path = wd
        self.file = open(os.path.join(self.path, ".malt.json"), "r+", encoding="utf-8")
        self._json_data = json.loads(self.file.read())

    @staticmethod
    def create(wd = os.getcwd()):
        empty = {}
        empty["installed_modules"] = {}
        empty["lib_prefix"] = ["./malt_modules"]
        open(os.path.join(wd, ".malt.json"), "w", encoding="utf-8").write(json.dumps(empty, indent=2))
        return module_registry(wd)

    def find_module(self, name):
        if name in self.installed:
            return self.installed[name]["src_path"]

        if os.path.exists(os.path.join(self.path, name, "module.json")):
            return os.path.join(self.path, name)

        return None

    @property
    def installed(self):
        return self._json_data["installed_modules"]

    def add_installed_module(self, module, cmake_dir):
        self.installed[module.name] = {}
        self.installed[module.name]["src_path"] = os.path.join("./", os.path.relpath(module.path, self.path))
        self.installed[module.name]["cmake_path"] = os.path.join("./", os.path.relpath(cmake_dir, self.path))

    def modules_path(self):
        return os.path.join(self.path, "malt_modules")

    def libraries_path(self):
        return os.path.join(self.modules_path(), "lib")

    def module_lib_path(self, mod_name):
        return os.path.join(self.libraries_path(), mod_name)

    def get_library_file(self, module):
        mod = self.find_module(module.name)
        if self.find_module(module.name) is None:
            return None

        path = os.path.join(self.module_lib_path(module.name), "lib" + module.name + ".so")
        if os.path.exists(path):
            return path

        return None

    @property
    def library_prefixes(self):
        return self._json_data["lib_prefix"]

    def save(self):
        self.file.seek(0)
        self.file.write(json.dumps(self._json_data, indent=2))
        self.file.truncate()
