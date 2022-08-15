import sys
import platform
import os
import subprocess
import importlib
from importlib import util
from pathlib import Path, PurePath
from shutil import which

from permasigner.ps_logger import Logger


class Utils(object):
    def __init__(self, args):
        self.args = args
        self.logger = Logger(self.args)

    @staticmethod
    def is_ios():
        if not sys.platform == "darwin":
            return False

        return platform.machine().startswith("i")

    @staticmethod
    def is_macos():
        if platform.machine().startswith("i"):
            return False

        return sys.platform == "darwin"

    @staticmethod
    def is_linux():
        return sys.platform == "linux"

    @staticmethod
    def is_windows():
        return sys.platform == "win32"

    @staticmethod
    def is_dpkg_installed(pkg):
        return (os.system("dpkg -s " + pkg + "> /dev/null 2>&1")) == 0

    def cmd_in_path(self, cmd):
        self.logger.debug(f"Checking if command {cmd} is in PATH...")

        path = which(cmd)
        utility = Utility(path)

        if cmd == "ldid":
            if self.is_ios():
                self.logger.debug(f"Checking for ldid on iOS")

                if Path("/.bootstrapped").exists():
                    self.logger.error(
                        "Your device seems to be strapped with Elucubratus. Unfortunately, we do not support these devices. You can switch to a device that uses Procursus (Taurine, odysseyra1n), or use the online method on our GitHub.")
                    print("    https://github.com/itsnebulalol/permasigner/wiki/Run-Online")
                    exit(1)

                if self.is_dpkg_installed("ldid"):
                    self.logger.debug(f"ldid is installed via dpkg")
                    utility.in_path = True
                    return utility
                else:
                    self.logger.error("ldid is required on iOS, but it is not installed. Please install it from Procursus.")
                    exit(1)

            if utility.path is not None:
                if "procursus" not in subprocess.getoutput([utility.path]):
                    utility.in_path = False
                    return utility

                self.logger.debug(f"Procursus ldid is installed")
                utility.in_path = True
                return utility

            utility.in_path = False
            return utility

        utility.in_path = path is not None
        return utility

    def get_home_data_directory(self):
        ps_home = os.environ.get("PERMASIGNER_HOME")
        if ps_home:
            return ps_home

        user_home = Path.home()
        if self.is_linux():
            xdg_data_home = os.environ.get("XDG_DATA_HOME", PurePath(f'{user_home}/.local/share'))
            return PurePath(f'{xdg_data_home}/permasigner')
        elif self.is_ios() or self.is_macos():
            return PurePath(f'{user_home}/Library/Application Support/permasigner')
        elif self.is_windows():
            return PurePath(f"{os.getenv('APPDATA')}/permasigner")

    @staticmethod
    def get_resource_path(package, resource):
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
        return f"{PurePath(*parts)}"


class Utility:
    def __init__(self, path, in_path=False):
        self.path = path
        self.in_path = in_path
