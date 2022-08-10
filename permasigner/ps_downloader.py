import hashlib

import requests
import subprocess
from subprocess import DEVNULL
import os
import platform
from shutil import copy, rmtree, move

from .ps_utils import Utils
from .ps_logger import Logger, Colors


class Hash:
    def get_hash(filePath, url):
        m = hashlib.md5()
        if url is None:
            with open(filePath, 'rb') as fh:
                m = hashlib.md5()
                while True:
                    data = fh.read(8192)
                    if not data:
                        break
                    m.update(data)
                return m.hexdigest()
        else:
            try:
                res = requests.get(url, stream=True)
                for data in res.iter_content(4096):
                    m.update(data)
                return m.hexdigest(), res
            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                Logger.error(f"ldid download URL is not reachable. Error: {e}")
                return m.hexdigest(), None


class DpkgDeb(object):
    def __init__(self, args, data_dir):
        self.args = args
        self.utils = Utils(self.args)
        self.data_dir = data_dir

    def get_arch(self):
        if platform.machine() == "x86_64":
            return "amd64"
        elif platform.machine() == "aarch64":
            return "arm64"

    def download(self):
        arch = self.get_arch()
        Logger.debug(f"Downloading dpkg-deb for {arch} architecture.", self.args)

        res = requests.get(
            f"http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.21.9_{arch}.deb", stream=True)
        try:
            if res.status_code == 200:
                with open(f"dpkg.deb", "wb") as f:
                    f.write(res.content)
                    Logger.debug(f"Wrote file.", self.args)
            else:
                Logger.error(f"dpkg download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            Logger.error(f"dpkg download URL is not reachable. Error: {err}")
            exit(1)

        Logger.debug(f"Running command: ar x dpkg.deb", self.args)
        subprocess.run(f"ar x dpkg.deb".split(), stdout=subprocess.DEVNULL)
        Logger.debug(f"Running command: tar -xf data.tar.xz", self.args)
        subprocess.run(f"tar -xf data.tar.xz".split(),
                       stdout=DEVNULL)

        copy("usr/bin/dpkg-deb", "dpkg-deb")
        Logger.debug(f"Copied dpkg-deb to project directory", self.args)

        Logger.debug(f"Running command: chmod +x dpkg-deb", self.args)
        subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
        os.remove("data.tar.xz")
        os.remove("control.tar.xz")
        os.remove("debian-binary")
        os.remove("dpkg.deb")
        rmtree("etc")
        rmtree("sbin")
        rmtree("usr")
        rmtree("var")
        Logger.debug(f"Cleaned up extracted content", self.args)

        Logger.debug(f"Moving dpkg-deb to {self.data_dir}", self.args)
        move("dpkg-deb", f"{self.data_dir}/dpkg-deb")


class Ldid(object):
    def __init__(self, args, data_dir, utils, exists=False):
        self.args = args
        self.ldid_fork = "itsnebulalol"
        self.utils = utils
        self.data_dir = data_dir
        self.exists = exists

    def get_arch(self):
        if self.utils.is_linux() and platform.machine() == "x86_64":
            return "ldid_linux_x86_64"
        elif self.utils.is_linux() and platform.machine() == "aarch64":
            return "ldid_linux_aarch64"
        elif self.utils.is_macos() and platform.machine() == "x86_64":
            return "ldid_macos_x86_64"
        elif self.utils.is_macos() and platform.machine() == "arm64":
            return "ldid_macos_arm64"

    def process(self, res):
        if res is not None and res.status_code == 200:
            Logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
            with open(f"ldid", "wb") as f:
                f.write(res.content)
                Logger.debug(f"Wrote file.", self.args)

            if self.exists:
                Logger.debug("Removing outdated version of ldid")
                os.remove(f"{self.data_dir}/ldid")

            Logger.debug("Running command: chmod +x ldid", self.args)
            Logger.debug(f"Moving ldid to {self.data_dir}", self.args)
            subprocess.run(f"chmod +x ldid".split(), stdout=DEVNULL)
            move("ldid", f"{self.data_dir}/ldid")
        else:
            if self.exists:
                Logger.log('Reusing the existing ldid', color=Colors.pink)
            else:
                exit(1)

    def download(self):
        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        else:
            ldid_fork = self.ldid_fork

        Logger.debug(f"Using ldid fork {ldid_fork}.", self.args)

        url = f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{self.get_arch()}"

        if self.exists:
            Logger.debug(f"Comparing {self.get_arch()} hash with {url}", self.args)

            remote_hash, res = Hash.get_hash(None, url)
            local_hash = Hash.get_hash(f"{self.data_dir}/ldid", None)

            if remote_hash == local_hash:
                Logger.debug(f"ldid hash successfully verified.", self.args)
            else:
                Logger.debug(f"ldid hash failed to verify.", self.args)
                self.process(res)
        else:
            Logger.debug(f"Downloading {self.get_arch()} from {url}", self.args)
            try:
                res = requests.get(url, stream=True)
                self.process(res)
            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                Logger.error(f"ldid download URL is not reachable. Error: {e}")
                exit(1)
