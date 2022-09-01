import subprocess
from argparse import Namespace
from pathlib import Path
from typing import Union

import requests
import hashlib
import platform
from shutil import move
from requests.exceptions import RequestException, ConnectionError
from urllib3.exceptions import NewConnectionError

from . import utils, logger
from .logger import colors


class Ldid:
    def __init__(self, data_dir: Path, args: Namespace) -> None:
        self.data_dir = data_dir
        self.args = args
        self.exists = False

    @staticmethod
    def get_hash(filepath, url):
        # Get remote hash if a url is provided
        # otherwise, get hash of a local file
        m = hashlib.md5()
        if url is None:
            with open(filepath, 'rb') as fh:
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
                logger.error(f"ldid download URL is not reachable. Error: {err}")
                return m.hexdigest(), None

    @property
    def remote_filename(self) -> Union[str, None]:
        # Get remote ldid name based on the platform
        if utils.is_linux() and platform.machine() == "x86_64":
            return "ldid_linux_x86_64"
        elif utils.is_linux() and platform.machine() == "aarch64":
            return "ldid_linux_aarch64"
        elif utils.is_linux() and platform.machine() == "armv7l":
            return "ldid_linux_armv7l"
        elif utils.is_macos() and platform.machine() == "x86_64":
            return "ldid_macosx_x86_64"
        elif utils.is_macos() and platform.machine() == "arm64":
            return "ldid_macosx_arm64"
        elif utils.is_freebsd() and platform.machine() == "amd64":
            return "ldid_freebsd_x86_64"
        elif utils.is_windows() and platform.machine() in ["AMD64", "x86_64"]:
            return "ldid_w64_x86_64.exe"
        elif utils.is_ios() and "64bit" in platform.platform():
            return "ldid_iphoneos_arm64"

    @property
    def local_name(self) -> str:
        # Get local ldid name based on the platform
        if utils.is_windows():
            return "ldid.exe"
        else:
            return "ldid"

    def exists_in_data_dir(self) -> bool:
        # Check if ldid is present in the data dir
        ldid_name = self.local_name

        return (self.data_dir / ldid_name).exists()

    def save_file(self, content: bytearray) -> None:
        # Get local ldid name
        ldid_name = self.local_name

        # Write bytearray to a new file
        with open(ldid_name, "wb") as f:
            f.write(content)
            logger.debug(f"Wrote file.", self.args.debug)

        # Remove outdated version of ldid it's present in the data dir
        if self.exists:
            logger.debug("Removing outdated version of ldid", self.args.debug)
            (self.data_dir / "ldid_name").unlink()

        # Make downloaded ldid executable
        utils.make_executable(ldid_name)
        destination_dir = self.data_dir / f"{ldid_name}"

        # Move downloaded ldid to data dir
        move(ldid_name, destination_dir)
        logger.debug(f"Moved ldid to {destination_dir}", self.args.debug)

    def download(self) -> None:
        # Check if ldidfork arg was passed
        # then, use it's value to construct a url
        if self.args.ldidfork:
            ldid_fork = self.args.ldidfork
        # Otherwise, use nebula's fork
        else:
            ldid_fork = "permasigner"

        # Check for ldid's presence in data directory
        exists = self.exists_in_data_dir()

        # Get name and extension of a local ldid
        local_filepath = self.data_dir / self.local_name

        # Get name of a remote ldid
        remote_filename = self.remote_filename

        url = f"https://github.com/{ldid_fork}/ldid/releases/latest/download/{remote_filename}"
        logger.debug(f"Comparing {local_filepath} hash with {url}", self.args.debug)

        # Get remote hash of ldid
        remote_hash, content = self.get_hash(None, url)
        local_hash = None

        # Determine ldid's hash if it's present in the data directory
        if exists:
            local_hash = self.get_hash(local_filepath, None)

        # Check if both hashes match, and if so proceed to the signing stage
        if remote_hash == local_hash:
            logger.debug(f"ldid hash successfully verified.", self.args.debug)
        else:
            # If hashes do no match, and the content is empty, fallback to existent ldid found in PATH/data dir
            if content is None:
                if exists:
                    logger.log('Could not verify remote hash, falling back to ldid found in path',
                               color=colors["yellow"])
                else:
                    logger.error('Download url is not reachable, and no ldid found in path, exiting.')
                    exit(1)
            # If hashes do not match but the content is not empty, save it to a file
            else:
                logger.debug(f"Ldid hash failed to verify, saving newer version", self.args.debug)
                self.save_file(content)


class Signer:
    def __init__(self, cert: Path, bundle_path: Path, data_dir: Path, tmp: Path, args: Namespace) -> None:
        self.cert = cert
        self.bundle_path = bundle_path
        self.data_dir = data_dir
        self.tmp = tmp
        self.args = args

    def sign_with_ldid(self, ldid: str) -> None:
        """ Sign the bundle with ldid """

        if ldid:
            ldid_cmd = ldid
        else:
            ldid_cmd = self.data_dir / "ldid"

        logger.log("Signing bundle with ldid...", color=colors["yellow"])
        logger.debug(
            f"Running command: {ldid_cmd} -S{self.tmp / 'entitlements.plist'} -M -K{self.cert} -Upassword '{self.bundle_path}'",
            self.args.debug)

        code, output = subprocess.getstatusoutput(f"{ldid_cmd} -S{self.tmp / 'entitlements.plist'} -M -K{self.cert} -Upassword {self.bundle_path}")

        if code != 0:
            logger.error(f'Failed to sign the bundle: {output}')
            exit(1)

        # Check if entitlements arg was passed
        # then, resign and merge the entitlements
        if self.args.entitlements:
            logger.debug(f"Signing with extra entitlements located in {self.args.entitlements}", self.args.debug)
            subprocess.run([
                f'{ldid_cmd}',
                f'-S{self.args.entitlements}',
                '-M',
                f'-K{self.cert}',
                '-Upassword', f'{self.bundle_path}'
            ],
                stdout=subprocess.DEVNULL)

    def sign_with_codesign(self) -> None:
        """ Imports the certificate and deep signs bundle with codesign"""
        logger.log("Importing certificate...", color=colors["yellow"])
        logger.debug(f"Running command: security import {self.cert} -P password -A", self.args.debug)
        subprocess.run(['security', 'import', self.cert, '-P', 'password', '-A'], stdout=subprocess.DEVNULL)

        logger.log(f"Signing bundle with codesign...", color=colors["yellow"])
        logger.debug(f"Running command: codesign -s 'We Do A Little Trolling iPhone OS Application Signing "
                     f"--force --deep --preserve-metadata=entitlements {self.bundle_path}", self.args.debug)
        subprocess.run(['codesign', '-s', 'We Do A Little Trolling iPhone OS Application Signing',
                        '--force', '--deep', '--preserve-metadata=entitlements', f'{self.bundle_path}'],
                       stdout=subprocess.DEVNULL)
