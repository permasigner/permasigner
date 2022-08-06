import requests
import subprocess
import os
import platform
from shutil import copy, rmtree, move

from .ps_utils import Utils
from .ps_logger import Logger


class DpkgDeb(object):
    def __init__(self, args):
        self.args = args

    def get_arch(self):
        if platform.machine() == "x86_64":
            return "amd64"
        elif platform.machine() == "aarch64":
            return "arm64"

    def download(self):
        utils = Utils(self.args)
        
        arch = self.get_arch()
        if args.debug:
            Logger.debug(f"Downloading dpkg-deb for {arch} architecture.")

        res = requests.get(
            f"http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.21.9_{arch}.deb", stream=True)
        try:
            if res.status_code == 200:
                with open(f"dpkg.deb", "wb") as f:
                    f.write(res.content)
                    if self.args.debug:
                        Logger.debug(f"Wrote file.")
            else:
                Logger.error(f"dpkg download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            Logger.error(f"dpkg download URL is not reachable. Error: {err}")
            exit(1)

        subprocess.run(f"ar x dpkg.deb".split(), stdout=subprocess.DEVNULL)
        if self.args.debug:
            Logger.debug(f"Extracted with ar.")
        subprocess.run(f"tar -xf data.tar.xz".split(),
                       stdout=subprocess.DEVNULL)
        if self.args.debug:
            Logger.debug(f"Extracted with tar.")
        copy("usr/bin/dpkg-deb", "dpkg-deb")
        if self.args.debug:
            Logger.debug(f"Copied.")
        subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
        os.remove("data.tar.xz")
        os.remove("control.tar.xz")
        os.remove("debian-binary")
        os.remove("dpkg.deb")
        rmtree("etc")
        rmtree("sbin")
        rmtree("usr")
        rmtree("var")
        move("dpkg-deb", f"{utils.get_home_data_directory()}/.permasigner/dpkg-deb")
        if self.args.debug:
            Logger.debug(f"Cleaned up.")


class Ldid(object):
    def __init__(self, args):
        self.args = args
        self.ldid_fork = "itsnebulalol"  # Use my fork to make unc0ver users shut up

    def get_arch(self):
        utils = Utils(self.args)
        
        if utils.is_linux() and platform.machine() == "x86_64":
            return "ldid_linux_x86_64"
        elif utils.is_linux() and platform.machine() == "aarch64":
            return "ldid_linux_aarch64"
        elif utils.is_macos() and platform.machine() == "x86_64":
            return "ldid_macos_x86_64"
        elif utils.is_macos() and platform.machine() == "arm64":
            return "ldid_macos_arm64"

    def download(self):
        utils = Utils(self.args)
        
        arch = self.get_arch()
        if self.args.debug:
            Logger.debug(f"Downloading {arch}")

        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        else:
            ldid_fork = self.ldid_fork

        url = f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{arch}"

        if self.args.debug:
            Logger.debug(f"Using ldid fork {ldid_fork}.")

        res = requests.get(url, stream=True)
        try:
            if res.status_code == 200:
                with open(f"ldid", "wb") as f:
                    f.write(res.content)
                    if self.args.debug:
                        Logger.debug(f"Wrote file.")
            else:
                Logger.error(f"ldid download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            Logger.error(f"ldid download URL is not reachable. Error: {err}")
            exit(1)

        subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        move("ldid", f"{utils.get_home_data_directory()}/.permasigner/ldid")
