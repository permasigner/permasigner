import sys
import platform
import os
import importlib
from importlib import util
from shutil import which

from .ps_logger import Logger


class Utils(object):
    def __init__(self, args):
        self.args = args
        self.logger = Logger(self.args)

    def is_ios(self):
        if not sys.platform == "darwin":
            return False

        return platform.machine().startswith("i")

    def cmd_in_path(self, cmd):
        self.logger.debug(f"Checking if command {cmd} is in PATH...")

        if cmd == "ldid":
            if self.is_ios():
                self.logger.debug(f"Checking for ldid on iOS")

                if os.path.exists("/.bootstrapped"):
                    self.logger.error(
                        "Your device seems to be strapped with Elucubratus. Unfortunately, we do not support these devices. You can switch to a device that uses Procursus (Taurine, odysseyra1n), or use the online method on our GitHub.")
                    print("    https://github.com/itsnebulalol/permasigner/wiki/Run-Online")
                    exit(1)

                if self.is_dpkg_installed("ldid"):
                    self.logger.debug(f"ldid is installed via dpkg")

                    return True
                else:
                    self.logger.error("ldid is required on iOS, but it is not installed. Please install it from Procursus.")
                    exit(1)

            # It seems like a better idea to force download ldid on macOS and Linux to make sure
            # they have the proper version all the time. A lot of ugly code is necessary for it.
            return False

        return which(cmd) is not None

    def is_macos(self):
        if platform.machine().startswith("i"):
            return False

        return sys.platform == "darwin"

    def is_linux(self):
        return sys.platform == "linux"

    def is_dpkg_installed(self, pkg):
        return (os.system("dpkg -s " + pkg + "> /dev/null 2>&1")) == 0

    def get_home_data_directory(self):
        ps_home = os.environ.get("PERMASIGNER_HOME")
        if ps_home:
            return ps_home

        user_home = os.path.expanduser("~")
        if self.is_linux():
            xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.join(user_home, ".local", "share"))
            return os.path.join(xdg_data_home, "permasigner")
        elif self.is_ios() or self.is_macos():
            return os.path.join(user_home, "Library", "Application Support", "permasigner")

    def get_resource_path(self, package, resource):
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
        parts.insert(0, os.path.dirname(mod.__file__))
        return f"{os.path.join(*parts)}"
