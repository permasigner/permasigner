from pathlib import Path, PurePath
import requests
import hashlib
import platform
from shutil import move
from requests.exceptions import RequestException, ConnectionError
from urllib3.exceptions import NewConnectionError

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
                if res.status_code == 200:
                    content = bytearray()
                    for data in res.iter_content(4096):
                        content += data
                        m.update(data)
                    return m.hexdigest(), content
                else:
                    return m.hexdigest(), None
            except (NewConnectionError, ConnectionError, RequestException) as err:
                self.logger.error(f"ldid download URL is not reachable. Error: {err}")
                return m.hexdigest(), None


class Ldid(object):
    def __init__(self, data_dir, name, args, utils, exists=False):
        self.name = name
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
            return "ldid_macosx_x86_64"
        elif self.utils.is_macos() and platform.machine() == "arm64":
            return "ldid_macosx_arm64"
        elif self.utils.is_freebsd() and platform.machine() == "amd64":
            return "ldid_freebsd_x86_64"
        elif self.utils.is_windows() and platform.machine() in ["AMD64", "x86_64"]:
            return "ldid_w64_x86_64.exe"
        elif self.utils.is_ios() and "64bit" in platform.platform():
            return "ldid_iphoneos_arm64"

    def save(self, content):
        with open(self.name, "wb") as f:
            f.write(content)
            self.logger.debug(f"Wrote file.")

        if self.exists:
            self.logger.debug("Removing outdated version of ldid")
            Path(self.data_dir).joinpath(self.name).unlink()

        self.utils.set_executable_permission(self.name)
        destination = PurePath(f'{self.data_dir}/{self.name}')
        move(self.name, destination)
        self.logger.debug(f"Moved ldid to {str(destination)}")

    def download(self):
        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        else:
            ldid_fork = self.ldid_fork

        self.logger.debug(f"Using ldid fork {ldid_fork}.")

        url = f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{self.get_arch()}"

        self.logger.debug(f"Comparing {self.get_arch()} hash with {url}")

        remote_hash, content = self.hash.get_hash(None, url)
        local_hash = None

        if self.exists:
            local_hash = self.hash.get_hash(PurePath(self.data_dir).joinpath(self.name), None)

        if remote_hash == local_hash:
            self.logger.debug(f"ldid hash successfully verified.")
        else:
            if content is None:
                if self.exists:
                    self.logger.log('Could not verify remote hash, falling back to ldid found in path',
                                    color=Colors.yellow)
                else:
                    self.logger.error('Download url is not reachable, and no ldid found in path, exiting.')
                    exit(1)
            else:
                self.logger.debug(f"Ldid hash failed to verify, saving newer version")
                self.save(content)
