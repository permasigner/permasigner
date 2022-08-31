import subprocess
import tarfile
from pathlib import Path

from . import logger
from .bundled.unix_ar import unix_ar
from .bundled.constrictor.dpkg import DPKGBuilder


class Dpkg:
    def __init__(self,
                 bundle: dict,
                 executables: set,
                 tmpfolder: Path,
                 output_path: Path,
                 dpkg: bool,
                 in_package: bool,
                 debug: bool) -> None:
        self.bundle = bundle
        self.executables = executables
        self.tmpfolder = tmpfolder
        self.dpkg = dpkg
        self.output_path = output_path
        self.in_package = in_package
        self.debug = debug

    @property
    def absolute_output_path(self):
        name = self.bundle['name'].replace(' ', '')
        version = self.bundle['version']

        return self.output_path / f"{name}_{version}.deb"

    def package_with_constrictor(self, source, control, postinst, prerm) -> None:
        dirs = [{
            'source': source,
            'destination': '/Applications',
        }]

        scripts = {
            'postinst': postinst,
            'prerm': prerm
        }

        builder = DPKGBuilder(self.absolute_output_path, self.executables, dirs, control, scripts)
        builder.build_package()

    def package_with_dpkg(self) -> None:
        """ Package application with dpkg-deb"""

        dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {self.tmpfolder}/deb {self.absolute_output_path}"
        logger.debug(f"Running command: {dpkg_cmd}", self.debug)
        subprocess.run(dpkg_cmd.split(), stdout=subprocess.DEVNULL)

    def package(self) -> Path:
        # If dpkg is in PATH
        # then, package with dpkg-deb
        # otherwise, package with constrictor
        if self.dpkg:
            self.package_with_dpkg()
        else:
            self.package_with_constrictor(
                self.tmpfolder / "deb/Applications",
                self.tmpfolder / "deb/DEBIAN/control",
                self.tmpfolder / "deb/DEBIAN/postinst",
                self.tmpfolder / "deb/DEBIAN/prerm"
            )

        return self.absolute_output_path


class Deb:
    def __init__(self, src: Path, dest: Path, debug: bool) -> None:
        self.src = src
        self.dest = dest
        self.debug = debug

    def extract_with_dpkg(self) -> None:
        # Extract deb contents with dpkg-deb -X
        logger.debug(f"Extracting deb package from {self.src} to {self.dest} with dpkg-deb", self.debug)
        subprocess.run(["dpkg-deb", "-X", self.src, self.dest], stdout=subprocess.DEVNULL)

    def extract_with_ar(self) -> None:
        """ Opens deb archive and extracts content of data.tar.* """
        logger.debug(f"Extracting deb package from {self.src} to {self.dest} with unix-ar", self.debug)
        with unix_ar.open(self.src) as ar_file:
            for member in ar_file.infolist():
                if b"data.tar" in ar_file.getinfo(member).name:
                    tarball = ar_file.open(member)
                    with tarfile.open(fileobj=tarball) as tar_file:
                        tar_file.extractall(path=self.dest)
                        break
