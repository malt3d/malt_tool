import json
import os

class module_registry:
    def __init__(self, wd = os.getcwd()):
        self.path = wd
        self.file = open(os.path.join(self.path, ".malt.json"), encoding="utf-8")
        self._json_data = json.loads(self.file.read())

    @staticmethod
    def create(wd = os.getcwd()):
        empty = {}
        empty["installed_modules"] = {}
        open(os.path.join(wd, ".malt.json"), "w", encoding="utf-8").write(json.dumps(empty, indent=2))
        return module_registry(wd)

    def find_module(self, name):
        if name in self.installed:
            return self.installed[name]["src_path"]

        if os.path.exists(os.path.join(self.path, name, "module.json")):
            return os.path.join(self.path, name)

    @property
    def installed(self):
        return self._json_data["installed_modules"]
