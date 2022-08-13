import os
import requests
import hashlib
import platform
from shutil import move
from requests.exceptions import RequestException, ConnectionError

from .ps_logger import Logger, Colors


class Hash(object):
    def __init__(self, args):
        self.args = args
        self.logger = Logger(self.args)

    def get_hash(self, filePath, url):
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
            except (ConnectionError, RequestException) as e:
                self.logger.error(f"ldid download URL is not reachable. Error: {e}")
                return m.hexdigest(), None


class Ldid(object):
    def __init__(self, data_dir, args, utils, exists=False):
        self.data_dir = data_dir
        self.args = args
        self.utils = utils
        self.ldid_fork = "itsnebulalol"
        self.exists = exists
        self.logger = Logger(self.args)
        self.hash = Hash(self.args)

    def get_arch(self):
        if self.utils.is_linux() and platform.machine() == "x86_64":
            return "ldid_linux_x86_64"
        elif self.utils.is_linux() and platform.machine() == "aarch64":
            return "ldid_linux_aarch64"
        elif self.utils.is_linux() and platform.machine() == "armv7l":
            return "ldid_linux_armv7l"
        elif self.utils.is_macos() and platform.machine() == "x86_64":
            return "ldid_macos_x86_64"
        elif self.utils.is_macos() and platform.machine() == "arm64":
            return "ldid_macos_arm64"

    def process(self, res):
        if res is not None and res.status_code == 200:
            self.logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
            with open(f"ldid", "wb") as f:
                f.write(res.content)
                self.logger.debug(f"Wrote file.")

            if self.exists:
                self.logger.debug("Removing outdated version of ldid")
                os.remove(f"{self.data_dir}/ldid")

            os.chmod('ldid', 256 | 128 | 64 | 32 | 8 | 4 | 1)
            move("ldid", f"{self.data_dir}/ldid")
            self.logger.debug(f"Moved ldid to {self.data_dir}")
        else:
            if self.exists:
                self.logger.log('Reusing the existing ldid', color=Colors.pink)
            else:
                exit(1)

    def download(self):
        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        else:
            ldid_fork = self.ldid_fork

        self.logger.debug(f"Using ldid fork {ldid_fork}.")

        url = f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{self.get_arch()}"

        if self.exists:
            self.logger.debug(f"Comparing {self.get_arch()} hash with {url}")

            remote_hash, res = self.hash.get_hash(None, url)
            local_hash = self.hash.get_hash(f"{self.data_dir}/ldid", None)

            if remote_hash == local_hash:
                self.logger.debug(f"ldid hash successfully verified.")
            else:
                self.logger.debug(f"ldid hash failed to verify.")
                self.process(res)
        else:
            self.logger.debug(f"Downloading {self.get_arch()} from {url}")
            try:
                res = requests.get(url, stream=True)
                self.process(res)
            except (ConnectionError, RequestException) as err:
                self.logger.error(f"ldid download URL is not reachable. Error: {err}")
                exit(1)
