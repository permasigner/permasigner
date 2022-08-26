import sys
import platform
import os
import subprocess
import importlib
from importlib import util
from pathlib import Path, PurePath
import shutil

from permasigner.ps_logger import Logger


class Utils(object):
    def __init__(self, args):
        self.args = args
        self.logger = Logger(self.args)

    @staticmethod
    def is_ios() -> bool:
        # Check if script is running on iOS
        if not sys.platform == "darwin":
            return False

        return platform.machine().startswith("i")

    @staticmethod
    def is_macos() -> bool:
        # Check if script is running on macOS
        if platform.machine().startswith("i"):
            return False

        return sys.platform == "darwin"

    @staticmethod
    def is_linux() -> bool:
        # Check if script is running on linux
        return sys.platform == "linux"

    @staticmethod
    def is_windows() -> bool:
        # Check if script is running on windows
        return sys.platform == "win32"

    @staticmethod
    def is_freebsd() -> bool:
        # Check if script is running on freebsd
        return "freebsd" in sys.platform

    @staticmethod
    def set_executable_permission(path: str) -> None:
        # Take a file on a given path and make it executable
        file = Path(path)
        mode = file.stat().st_mode
        mode |= (mode & 0o444) >> 2
        file.chmod(mode)

    @staticmethod
    def cmd_in_path(cmd: str) -> bool:
        # Check if command is in PATH
        path = shutil.which(cmd)

        # If command was not found in Path return False
        if path is None:
            return False

        # Check if ldid is from procursus
        if cmd == "ldid":
            if "procursus" in subprocess.getoutput(path):
                return True
            return False

        # Return True if command was found in PATH
        return True

    def get_data_directory(self) -> Path:
        # Get path to data directory

        # Get the value of PERMASIGNER_HOME variable and if it's exported use it as data directory
        ps_home = os.environ.get("PERMASIGNER_HOME")
        if ps_home:
            return ps_home

        # Get path to user's $HOME
        home = Path.home()

        # Use XDG_DATA_HOME as data directory on freebsd and linux if it's exported
        # otherwise default to $HOME/.local/share
        if self.is_linux() or self.is_freebsd():
            if xdg := os.environ.get("XDG_DATA_HOME"):
                return Path(xdg).joinpath("permasigner")
            return home / ".local/share/permasigner"
        # Use $HOME/Library/Application Support/permasigner as data directory on macOS and iOS
        elif self.is_ios() or self.is_macos():
            return home / "Library/Application Support/permasigner"
        # Use %APPDATA%/permasigner as data directory on Windows OS
        elif self.is_windows():
            return home / "AppData/Roaming/permasigner"

    @staticmethod
    def get_resource_path(package: str, resource: str):
        # Get path to resource in the package
        spec = importlib.util.find_spec(package)
        if spec is None:
            return None
        loader = spec.loader
        if loader is None or not hasattr(loader, 'get_data'):
            return None
        mod = (sys.modules.get(package) or
               importlib._bootstrap._load(spec))
        if mod is None or not hasattr(mod, '__file__'):
            return None

        parts = resource.split('/')
        parts.insert(0, PurePath(mod.__file__).parent)
        return PurePath(*parts)
