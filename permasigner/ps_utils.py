import sys
import subprocess
import platform
import os
import importlib

from .ps_logger import Logger


class Utils:
    def is_ios():
        if not sys.platform == "darwin":
            return False

        return platform.machine().startswith("i")

    def cmd_in_path(args, cmd):
        if args.debug:
            Logger.debug(f"Checking if command {cmd} is in PATH...")

        if cmd == "ldid":
            if Utils.is_ios():
                if args.debug:
                    Logger.debug(f"Checking for ldid on iOS")

                if os.path.exists("/.bootstrapped"):
                    Logger.error("Your device seems to be strapped with Elucubratus. Unfortunately, we do not support these devices. You can switch to a device that uses Procursus (Taurine, odysseyra1n), or use the online method on our GitHub.")
                    print("    https://github.com/itsnebulalol/permasigner/wiki/Run-Online")
                    exit(1)

                if Utils.is_dpkg_installed("ldid"):
                    if args.debug:
                        Logger.debug(f"ldid is installed via dpkg")

                    return True
                else:
                    Logger.error("[-] ldid is required on iOS, but it is not installed. Please install it from Procursus.")
                    exit(1)

            # It seems like a better idea to force download ldid on macOS and Linux to make sure
            # they have the proper version all the time. A lot of ugly code is necessary for it.
            return False

        return subprocess.getstatusoutput(f"which {cmd}")[0] == 0

    def is_macos():
        if platform.machine().startswith("i"):
            return False

        return sys.platform == "darwin"

    def is_linux():
        return sys.platform == "linux"

    def is_dpkg_installed(pkg):
        return (os.system("dpkg -s " + pkg + "> /dev/null 2>&1")) == 0

    def get_home_data_directory(args):
        if os.environ.get("XDG_DATA_HOME"):
            if args.debug:
                Logger.debug(f"Using XDG_DATA_HOME: {os.environ.get('XDG_DATA_HOME')}")
            return os.environ.get("XDG_DATA_HOME")
        else:
            if args.debug:
                Logger.debug(f"Using user home directory: {os.path.expanduser('~')}")
            return os.path.expanduser('~')

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
        parts.insert(0, os.path.dirname(mod.__file__))
        return f"{os.path.join(*parts)}"
