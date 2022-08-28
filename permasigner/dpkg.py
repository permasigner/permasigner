import subprocess
import tarfile
from argparse import Namespace
from pathlib import Path

import unix_ar

from . import logger
from .constrictor.dpkg import DPKGBuilder


class Dpkg:
    def __init__(self,
                 bundle: dict,
                 tmpfolder: Path,
                 output_path: Path,
                 dpkg: bool,
                 in_package: bool,
                 args: Namespace) -> None:
        self.bundle = bundle
        self.tmpfolder = tmpfolder
        self.dpkg = dpkg
        self.output_path = output_path
        self.in_package = in_package
        self.args = args

    def package_with_constrictor(self, source, control, postinst, prerm) -> Path:

        dirs = [{
            'source': source,
            'destination': '/Applications',
            'executable':  self.bundle["executable"]
        }]

        scripts = {
            'postinst': postinst,
            'prerm': prerm
        }

        builder = DPKGBuilder(self.output_path, self.bundle, dirs, control, scripts)
        return builder.build_package()

    def package_with_dpkg(self, output_path: Path, tmp: Path, debug: Namespace) -> Path:
        # Construct output name from app name and app version
        # Then create a deb package with dpkg-deb
        name = self.bundle["name"].replace(' ', '')
        version = self.bundle["version"]
        output_path = output_path / f"{name}_{version}.deb"
        dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {tmp}/deb {output_path}"
        logger.debug(f"Running command: {dpkg_cmd}", debug)
        subprocess.run(dpkg_cmd.split(), stdout=subprocess.DEVNULL)

        return output_path

    def package(self) -> Path:
        # If dpkg is in PATH
        # then, package with dpkg-deb
        # otherwise, package with constrictor
        if self.dpkg:
            return self.package_with_dpkg(self.output_path, self.tmpfolder, self.args.debug)
        else:
            return self.package_with_constrictor(
                                            self.tmpfolder / "deb/Applications",
                                            self.tmpfolder / "deb/DEBIAN/control",
                                            self.tmpfolder / "deb/DEBIAN/postinst",
                                            self.tmpfolder / "deb/DEBIAN/prerm")


class Deb:
    def __init__(self, src: Path, dest: Path, debug: Namespace) -> None:
        self.src = src
        self.dest = dest
        self.debug = debug

    def extract_with_dpkg(self) -> None:
        # Extract deb contents with dpkg-deb -X
        logger.debug(f"Running command: dpkg-deb -X {self.src} {self.dest}", self.debug)
        subprocess.run(
            ["dpkg-deb", "-X", self.src, self.dest], stdout=subprocess.DEVNULL)

    def extract_with_ar(self) -> None:
        # Extract deb file with unix-ar
        # This needs a better aproach
        logger.debug(f"Extracting {self.src} with unix-ar", self.debug)

        ar_file = unix_ar.open(self.src)
        try:
            try:
                tarball = ar_file.open('data.tar.xz')
            except KeyError:
                tarball = ar_file.open('data.tar.gz')
        except KeyError:
            tarball = ar_file.open('data.tar.bz2')
        with tarfile.open(fileobj=tarball) as data:
            data.extractall(path=self.dest)
        ar_file.close()
