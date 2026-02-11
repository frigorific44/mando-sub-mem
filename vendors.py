import subprocess
import shutil
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import tomllib


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        install_vendors(
            self.metadata.core.dependencies, get_ignore(self.metadata.config)
        )


def install_vendors(dependencies, ignore):
    vendor = [p for p in dependencies if all([ig not in p for ig in ignore])]
    print(" ".join(vendor))
    if not shutil.which("uv"):
        print("uv is not found in PATH.")
    uv_args = ["uv", "pip", "install", "-t", "src/subtitleterms/vendor", *vendor]
    subprocess.run(uv_args)


def get_ignore(config):
    try:
        ignore = config["tool"]["vendors"]["ignore"]
    except KeyError:
        ignore = []
    return ignore


if __name__ == "__main__":
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    dependencies = config["project"]["dependencies"]
    ignore = get_ignore(config)
    install_vendors(dependencies, ignore)
