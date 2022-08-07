import hashlib
import requests
from .ps_downloader import Ldid
from .ps_logger import Logger


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
            r = requests.get(url)
            for data in r.iter_content(8192):
                m.update(data)
            return m.hexdigest()


class LdidHash(object):
    def __init__(self, args, data_dir):
        self.args = args
        self.data_dir = data_dir

    def check_hash(self):
        ldid = Ldid(self.args, self.data_dir)
        arch = ldid.get_arch()

        if self.args.debug:
            Logger.debug(f"Checking {arch} hash...")

        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        else:
            ldid_fork = ldid.ldid_fork

        remote_hash = Hash.get_hash(None, f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{arch}")
        local_hash = Hash.get_hash(f"{self.data_dir}/ldid", None)

        if remote_hash == local_hash:
            if self.args.debug:
                Logger.debug(f"ldid hash successfully verified.")

            return True
        else:
            if self.args.debug:
                Logger.debug(f"ldid hash failed to verify.")

            return False
