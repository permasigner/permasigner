import array
import shutil
import subprocess
import tempfile
import zipfile
from argparse import Namespace
from pathlib import Path, PurePath
from shutil import copytree

import requests
from requests import RequestException
from urllib3.exceptions import NewConnectionError

from permasigner import (
    logger,
    utils,
)
from permasigner.installer import install_on_ios, install_from_pc

from permasigner.packager import (
    Builder,
    extract_with_dpkg,
    extract_with_ar
)

from permasigner.copier import Copier
from permasigner.downloader import Ldid

from permasigner.logger import colors


class Permasigner:
    def __init__(self, in_package: bool, args: Namespace) -> None:
        self.in_package = in_package
        self.args = args
        self.dpkg = None
        self.ldid = None
        self.data_dir = None
        self.output_dir = None
        self.tmp = None
        self.is_installed = False
        self.outputs = []

    def main(self) -> None:
        logger.log_header(f"Permasigner | Version {utils.get_version(self.in_package)}")
        logger.log_header("Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")

        print()

        # Output debug message if the script
        # is running from a package
        if self.in_package:
            logger.debug(f"Running from package, not cloned repo.", self.args.debug)

        # Check for dependencies
        logger.debug("Checking for dependencies...", self.args.debug)
        self.ldid = utils.cmd_in_path('ldid')
        self.dpkg = utils.cmd_in_path('dpkg-deb')

        # Determine path to data directory
        # then, create dir if it doesn't exist
        self.data_dir = utils.get_data_directory()
        Path(self.data_dir).mkdir(exist_ok=True, parents=True)

        # Determine path to output directory
        # then, create dir if it doesn't exist
        self.output_dir = utils.get_output_directory(self.data_dir, self.in_package, self.args.output)
        Path(self.output_dir).mkdir(exist_ok=True, parents=True)

        # Download ldid if it's not in PATH and no skip argument is passed
        if not self.ldid and not self.args.nocheckldid:
            Ldid(self.data_dir, self.args).download()

        # Create tmp in working directory
        with tempfile.TemporaryDirectory() as tmpfolder:
            self.tmp = Path(tmpfolder)

            # Check if url arg was specified
            # then, download ipa from url and extract it to tmp dir
            if self.args.url:
                if not self.args.url.endswith(".ipa"):
                    exit("URL provided is not an IPA, make sure to provide a direct link.")
                logger.log(f"Downloading ipa from {self.args.url}...", color=colors["yellow"])
                self.download_ipa(self.args.url, self.tmp)
                logger.log(f"Extracting IPA...", color=colors["yellow"])
                self.extract_ipa((self.tmp / "app.ipa"), self.tmp)
            # Check if path arg was specified
            # then, check if path is a deb or an ipa
            elif self.args.path:
                self.check_path_arguments(self.args.path)
            # Check if folder arg was specified
            # then, sign each ipa in the folder
            elif self.args.folder:
                self.outputs = self.sign_folder(self.tmp)

            if not self.args.folder:
                out_dir = self.permasign()

                if self.args.install:
                    if utils.is_ios():
                        self.is_installed = install_on_ios(out_dir, self.args)
                    else:
                        self.is_installed = install_from_pc(out_dir, self.args)

            # Done, print end message
            logger.log_footer(f"We are finished!", )

            if self.is_installed:
                logger.log_footer("The application was installed to your device, no further steps are required!")
            else:
                logger.log_footer("Copy the newly created deb from the output folder to your jailbroken iDevice and install it!")

            logger.log_footer("The app will continue to work when rebooted to stock.")
            logger.log_footer("Also, this is free and open source software! Feel free to donate to my Patreon if you enjoy :)")
            logger.log_footer("https://patreon.com/nebulalol")

            if self.args.folder:
                final_outputs = ""
                for output in self.outputs:
                    final_outputs += f'{output}\n'
                logger.log_footer(f"Output files:\n{final_outputs}")
            else:
                logger.log_footer(f"Output file: {out_dir}")

    def permasign(self) -> Path:
        # Search for application bundle in Payload directory
        bundle_path = utils.find_application_bundle(self.tmp)

        # Check if Info.plist exists
        # then, read the app info from it
        bundle = {}
        if (plist_path := bundle_path / "Info.plist").exists():
            logger.log(f"Reading plist...", color=colors["yellow"])
            bundle = utils.read_plist(plist_path, self.args)
        # If it doesn't exist
        # then, exit with an erro
        else:
            exit("Unable to find Info.plist, can't read application data")

        # Create directories in tmp dir
        logger.log(f"Making deb directories...\n", color=colors["yellow"])
        (self.tmp / 'deb/Applications').mkdir(exist_ok=True, parents=True)
        (self.tmp / 'deb/DEBIAN').mkdir(exist_ok=True, parents=True)

        # Copy control file and scripts into DEBIAN directory
        print("Copying control file and maintainer scripts...")
        copier = Copier(bundle, self.in_package)
        copier.copy_postinst(self.tmp / "deb/DEBIAN/postinst")
        copier.copy_control(self.tmp / "deb/DEBIAN/control")
        copier.copy_prerm(self.tmp / "deb/DEBIAN/prerm")

        # Set chmod 755 on prerm and postinst scripts
        print("Changing deb file scripts permissions...")
        utils.make_executable(self.tmp / "deb/DEBIAN/prerm")
        utils.make_executable(self.tmp / "deb/DEBIAN/postinst")

        # Copy entitlements to temporary directory
        copier.copy_entitlements(self.tmp / "entitlements.plist")

        # Copy application bundle to temporary directory
        print("Copying application bundle...")
        full_app_path = self.tmp / f"deb/Applications/{bundle_path.name}"
        copytree(bundle_path, full_app_path, dirs_exist_ok=True)

        # Set chmod 755 on application executable
        print("Changing app executable permissions...")
        utils.make_executable(full_app_path / bundle["executable"])

        # Get path to certificate file
        cert = utils.get_certificate_path(self.in_package)

        # Sign the app
        logger.log(f"Signing the application...", color=colors["yellow"])

        # Check if codesign arg was specified
        # then, check if the script runs on macOS
        # then, sign with codesign
        if self.args.codesign and utils.is_macos():
            print("Signing bundle with codesign...")
            self.sign_with_codesign(cert, full_app_path)
        # In other cases sign with ldid
        else:
            print("Signing bundle with ldid...")
            self.sign_with_ldid(self.ldid, cert, full_app_path, self.data_dir)

        print()

        # Package the deb file
        logger.log(f"Packaging the deb file...", color=colors["yellow"])
        builder = Builder(bundle, self.tmp, self.output_dir, self.dpkg, self.in_package, self.args)
        return builder.package()

    def check_path_arguments(self, source: str) -> None:
        path = source.strip('"').strip("'").strip()
        path = Path(path).expanduser()

        # Check if file exists
        if path.exists():
            # Check if given path is a deb file
            # then, extract it
            if path.suffix == ".deb":
                logger.debug(f"Extracting deb package from {path} to {self.tmp / 'extractedDeb'}", self.args.debug)
                # Check if dpkg is in PATH
                # then, extract with dpkg-deb
                if self.dpkg:
                    extract_with_dpkg(path, self.tmp / "extractedDeb", self.args.debug)
                # If dpkg is not inpath
                # then, extract with unix-ar
                else:
                    extract_with_ar(path, self.tmp / "extractedDeb", self.args.debug)

                # Check if extracted deb file contains an app bundle
                # then, extract it to Payload directory
                (self.tmp / "app/Payload").mkdir(parents=True, exist_ok=False)
                for fname in Path(f"{self.tmp}/extractedDeb/Applications").iterdir():
                    if fname.name.endswith(".app"):
                        shutil.copytree(f"{self.tmp}/extractedDeb/Applications/{fname.name}",
                                        f"{self.tmp}/app/Payload/{fname.name}")
                        break
            # Check if given path is an ipa
            # then, copy it to tmp dir and extract
            elif path.suffix == ".ipa":
                self.extract_ipa(path, self.tmp)
            # Exit win an error if path is neither an ipa nor a deb file
            else:
                exit("That file is not supported by Permasigner! Make sure you're using an IPA or deb.")
        # Exit with an error if path does not exist
        else:
            exit("That file does not exist! Make sure you're using a direct path to the IPA file.")

    def sign_with_ldid(self, ldid, cert_path, application_path, data_dir) -> None:
        # Determine path to ldid
        if ldid_path := ldid:
            ldid_cmd = ldid_path
        else:
            ldid_cmd = data_dir / "ldid"

        logger.debug(
            f"Running command: {ldid_cmd} -S{PurePath(f'{self.tmp}/entitlements.plist')} -M -K{cert_path} -Upassword '{application_path}'",
            self.args.debug)

        # Sign the bundle with ldid
        subprocess.run([
                        ldid_cmd,
                        f"-S{self.tmp / 'entitlements.plist'}",
                        "-M",
                        f"-K{cert_path}",
                        "-Upassword",
                        application_path],
                       stdout=subprocess.DEVNULL)

        # Check if entitlements arg was passed
        # then, resign and merge the entitlements
        if self.args.entitlements:
            logger.debug(f"Signing with extra entitlements located in {self.args.entitlements}", self.args.debug)
            subprocess.run([
                            f'{ldid_cmd}',
                            f'-S{self.args.entitlements}',
                            '-M',
                            f'-K{cert_path}',
                            '-Upassword', f'{application_path}'
                            ],
                           stdout=subprocess.DEVNULL)

    def sign_with_codesign(self, cert_path, applications_path: Path) -> None:
        # Import the certificate
        logger.debug(f"Running command: security import {cert_path} -P password -A", self.args.debug)
        subprocess.run(
            ['security', 'import', cert_path, '-P', 'password', '-A'], stdout=subprocess.DEVNULL)

        # Sign with codesign using imported certificate
        logger.debug(f"Running command: codesign -s 'We Do A Little Trolling iPhone OS Application Signing "
                     f"--force --deep --preserve-metadata=entitlements {applications_path}", self.args.debug)
        subprocess.run(['codesign', '-s', 'We Do A Little Trolling iPhone OS Application Signing',
                        '--force', '--deep', '--preserve-metadata=entitlements', f'{applications_path}'],
                       stdout=subprocess.DEVNULL)

    def sign_folder(self, tmp: Path) -> array:
        # Itterate over each ipa in specified folder
        # then, extract and permasign it
        for ipa in Path(self.args.folder).iterdir():
            shutil.rmtree(tmp)
            Path(tmp).mkdir()

            logger.log(f"Extracting ipa to temporary directory", color=colors["yellow"])
            self.extract_ipa(ipa, self.tmp)

            output = self.permasign()
            self.outputs.append(output)

        return self.outputs

    @staticmethod
    def download_ipa(url: str, dest: Path) -> None:
        # Attempt to download ipa from specified url
        # then, if status code is 200, save response content to a file
        # otherwise, exit with an error
        try:
            res = requests.get(url, stream=True)
            if res.status_code == 200:
                with open(f"{dest}/app.ipa", "wb") as f:
                    f.write(res.content)
            else:
                exit(f"Provided URL is not reachable. Status code: {res.status_code}")
        except (NewConnectionError, ConnectionError, RequestException) as err:
            exit(f"Provided URL is not reachable. Error: {err}")

    @staticmethod
    def extract_ipa(src: Path, dest: Path) -> None:
        # Extract ipa to destination
        with zipfile.ZipFile(src, 'r') as f:
            with Path(f"{dest}/app") as path:
                path.mkdir(exist_ok=True)
                f.extractall(path)
