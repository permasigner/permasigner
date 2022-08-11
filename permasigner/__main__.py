import os
from pathlib import Path
from shutil import copy, copytree, rmtree, which
import plistlib
import requests
from urllib.parse import urlparse
import zipfile
import sys
import subprocess
import tempfile
import platform
from subprocess import DEVNULL
from glob import glob

from .ps_copier import Copier
from .ps_downloader import DpkgDeb, Ldid
from . import __version__
from .ps_utils import Utils
from .ps_logger import Logger, Colors

""" Main Class """


class Main(object):
    def __init__(self, args, in_package=False):
        self.args = args
        self.in_package = in_package
        self.utils = Utils(self.args)
        self.logger = Logger(self.args)
        self.outputs = []

    def main(self):
        data_dir = self.utils.get_home_data_directory()
        os.makedirs(data_dir, exist_ok=True)

        if self.in_package:
            self.logger.debug(f"Running from package, not cloned repo.")

        is_extracted = False

        ldid_in_path = self.utils.cmd_in_path('ldid')
        dpkg_in_path = self.utils.cmd_in_path('dpkg-deb')
        git_in_path = self.utils.cmd_in_path('git')

        if git_in_path:
            self.logger.debug(f"Git is in PATH")

            if self.in_package:
                ver_string = f"{__version__.__version__}"
            elif "main" not in subprocess.getoutput(['git', 'rev-parse', '--abbrev-ref', 'HEAD']):
                ver_string = f"{subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}_{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
            else:
                ver_string = f"{__version__.__version__}_rev-{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
        else:
            self.logger.debug(f"Git is not in PATH")
            if os.environ.get('IS_DOCKER_CONTAINER'):
                ver_string = os.environ.get('VERSION', False)
            else:
                ver_string = f"{__version__.__version__}"

        print(Colors.bold + f"Permasigner | Version {ver_string}")
        print(
            Colors.bold + "Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")
        print()

        # Run checks
        self.checks(ldid_in_path, dpkg_in_path, data_dir)

        # Prompt the user if they'd like to use an external IPA or a local IPA
        if not (self.args.url or self.args.path or self.args.folder):
            option = self.logger.ask("Would you like to use an external or a local IPA? [E, L] ").lower()
            print()

        with tempfile.TemporaryDirectory() as tmpfolder:
            # If the user's choice is external, download an IPA
            # Otherwise, copy the IPA to the temporary directory
            if self.args.url:
                url = self.args.url

                if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                    self.logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                    exit(1)

                res = requests.get(url, stream=True)
                try:
                    if res.status_code == 200:
                        self.logger.log(f"Downloading file...", color=Colors.pink)

                        with open(f"{tmpfolder}/app.ipa", "wb") as f:
                            f.write(res.content)
                    else:
                        self.logger.error(f"URL provided is not reachable. Status code: {res.status_code}")
                        exit(1)
                except requests.exceptions.RequestException as err:
                    self.logger.error(f"URL provided is not reachable. Error: {err}")
                    exit(1)
            elif self.args.path:
                path = self.args.path
                path = path.strip().lstrip("'").rstrip("'")

                if Path(path).exists():
                    if path.endswith(".deb"):
                        if dpkg_in_path:
                            self.logger.debug(f"Running command: dpkg-deb -X {path} {tmpfolder}/extractedDeb")

                            subprocess.run(
                                ["dpkg-deb", "-X", path, f"{tmpfolder}/extractedDeb"], stdout=DEVNULL)
                        else:
                            self.logger.debug(f"Running command: {data_dir}/dpkg-deb -X {path} {tmpfolder}/extractedDeb")

                            subprocess.run(
                                [f"{data_dir}/dpkg-deb", "-X", path, f"{tmpfolder}/extractedDeb"],
                                stdout=DEVNULL)

                        os.makedirs(f"{tmpfolder}/app/Payload", exist_ok=False)
                        for fname in os.listdir(path=f"{tmpfolder}/extractedDeb/Applications"):
                            if fname.endswith(".app"):
                                copytree(f"{tmpfolder}/extractedDeb/Applications/{fname}",
                                         f"{tmpfolder}/app/Payload/{fname}")

                        is_extracted = True
                    elif path.endswith(".ipa"):
                        copy(path, f"{tmpfolder}/app.ipa")
                    else:
                        self.logger.error("That file is not supported by Permasigner! Make sure you're using an IPA or deb.")
                        exit(1)
                else:
                    self.logger.error("That file does not exist! Make sure you're using a direct path to the IPA file.")
                    exit(1)
            elif self.args.folder:
                for fpath in glob(f"{self.args.folder}/*.ipa"):
                    if os.path.exists(f"{tmpfolder}/app.ipa"):
                        os.remove(f"{tmpfolder}/app.ipa")
                    if os.path.exists(f"{tmpfolder}/app"):
                        rmtree(f"{tmpfolder}/app")
                    if os.path.exists(f"{tmpfolder}/deb"):
                        rmtree(f"{tmpfolder}/deb")

                    fname = os.path.basename(fpath)
                    self.logger.log(f"Signing {fname}...", color=Colors.pink)
                    print()

                    copy(fpath, f"{tmpfolder}/app.ipa")
                    path_to_deb = self.run(tmpfolder, dpkg_in_path, data_dir, is_extracted)
                    self.outputs.append(path_to_deb)
            elif option == "e":
                url = self.logger.ask("Paste in the *direct* path to an IPA online: ")

                if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                    self.logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                    exit(1)
                print()

                res = requests.get(url, stream=True)
                try:
                    if res.status_code == 200:
                        self.logger.log(f"Downloading file...", color=Colors.pink)

                        with open(f"{tmpfolder}/app.ipa", "wb") as f:
                            f.write(res.content)
                    else:
                        self.logger.error(f"URL provided is not reachable. Status code: {res.status_code}")
                        exit(1)
                except requests.exceptions.RequestException as err:
                    self.logger.error(f"URL provided is not reachable. Error: {err}")
                    exit(1)
            elif option == "l":
                if os.environ.get('IS_DOCKER_CONTAINER', False):
                    self.logger.log(
                        "Running in Docker container, please place an IPA in the 'ipas' folder, then put the name of the file below.",
                        color=Colors.orange)
                    ipa_name = self.logger.ask('    IPA name (ex. Taurine.ipa, DemoApp.ipa): ')
                    path = f"/permasigner/ipas/{ipa_name}"
                else:
                    path = self.logger.ask("Paste in the path to an IPA in your file system: ")

                path = path.strip().lstrip("'").rstrip("'")

                if Path(path).exists():
                    if path.endswith(".deb"):
                        if dpkg_in_path:
                            self.logger.debug(f"Running command: dpkg-deb -X {path} {tmpfolder}/extractedDeb")

                            subprocess.run(
                                ["dpkg-deb", "-X", path, f"{tmpfolder}/extractedDeb"], stdout=DEVNULL)
                        else:
                            self.logger.debug(f"Running command: {data_dir}/dpkg-deb -X {path} {tmpfolder}/extractedDeb")

                            subprocess.run(
                                [f"{data_dir}/dpkg-deb", "-X", path, f"{tmpfolder}/extractedDeb"],
                                stdout=DEVNULL)

                        os.makedirs(f"{tmpfolder}/app/Payload", exist_ok=False)
                        for fname in os.listdir(path=f"{tmpfolder}/extractedDeb/Applications"):
                            if fname.endswith(".app"):
                                copytree(f"{tmpfolder}/extractedDeb/Applications/{fname}",
                                         f"{tmpfolder}/app/Payload/{fname}")

                        is_extracted = True
                    elif path.endswith(".ipa"):
                        copy(path, f"{tmpfolder}/app.ipa")
                    else:
                        self.logger.error("That file is not supported by Permasigner! Make sure you're using an IPA or deb.")
                        exit(1)
                else:
                    self.logger.error("That file does not exist! Make sure you're using a direct path to the IPA file.")
                    exit(1)
            else:
                self.logger.error(f"That is not a valid option!")
                exit(1)

            if not self.args.folder:
                print()

            is_installed = False
            if not self.args.folder:
                path_to_deb = self.run(tmpfolder, dpkg_in_path, data_dir, is_extracted)

                if self.args.install:
                    is_installed = self.install(path_to_deb)

            # Done, print end message
            self.logger.log(f"We are finished!", color=Colors.green)

            if is_installed:
                self.logger.log(f"The application was installed to your device, no further steps are required!",
                                color=Colors.green)
            else:
                self.logger.log(
                    f"Copy the newly created deb from the output folder to your jailbroken iDevice and install it!",
                    color=Colors.green)

            self.logger.log(f"The app will continue to work when rebooted to stock.", color=Colors.green)
            self.logger.log(
                f"Also, this is free and open source software! Feel free to donate to my Patreon if you enjoy :)",
                color=Colors.green)
            print(Colors.green + "    https://patreon.com/nebulalol" + Colors.reset)
            if self.args.folder:
                final_outputs = ""
                for output in self.outputs:
                    if final_outputs == "":
                        final_outputs = f"{output}"
                    else:
                        final_outputs = f"{final_outputs}, {output}"
                self.logger.log(f"Output files: {final_outputs}", color=Colors.green)
            else:
                self.logger.log(f"Output file: {path_to_deb}", color=Colors.green)

    def checks(self, ldid_in_path, dpkg_in_path, data_dir):
        # Check if script is running on Windows, if so, fail
        if sys.platform == "windows":
            self.logger.error(f"Script must be ran on macOS or Linux.")
            exit(1)

        # Check if codesign arg is added on Linux or iOS
        if self.args.codesign:
            if not self.utils.is_macos():
                self.logger.error(f"Codesign can only be used on macOS, remove the argument to use ldid instead.")
                exit(1)

        # Auto download ldid
        if not ldid_in_path:
            if Path(f"{data_dir}/ldid").exists():
                ldid = Ldid(self.args, data_dir, self.utils, True)
            else:
                self.logger.log("ldid binary is not found, downloading latest binary.", color=Colors.pink)
                ldid = Ldid(self.args, data_dir, self.utils, False)
            ldid.download()

        # Auto download dpkg-deb on Linux
        if not dpkg_in_path and self.utils.is_linux():
            if not Path(f"{data_dir}/dpkg-deb").exists():
                self.logger.debug(f"On Linux {platform.machine()}, dpkg-deb not found...")
                self.logger.log(f"dpkg-deb not found, downloading.", color=Colors.pink)
                dpkg_downloader = DpkgDeb(self.args, data_dir)
                dpkg_downloader.download()
                print()

        if self.utils.is_macos():
            if which('dpkg') is None:
                self.logger.debug(f"On macOS x86_64, dpkg not found...")
                self.logger.error(
                    "dpkg is not installed and is required on macOS. Install it though brew or Procursus to continue.")
                exit(1)

    def install(self, path_to_deb):
        if not self.utils.is_ios():
            from .ps_installer import Installer

        if not self.utils.is_ios():
            installer = Installer(self.args, path_to_deb)
            is_installed = installer.install_deb()
        else:
            print("Checking if user is in sudoers")
            p = subprocess.run('sudo -nv'.split(),
                               capture_output=True)
            if p.returncode == 0 or 'password' in p.stderr.decode():
                print("User is in sudoers, using sudo command")
                self.logger.debug(f"Running command: sudo dpkg -i {path_to_deb}")

                subprocess.run(
                    ["sudo", "dpkg", "-i", f"{path_to_deb}"], capture_output=True)

                subprocess.run(
                    ['sudo', 'apt-get', 'install', '-f'], capture_output=True)

                is_installed = True
            else:
                print("User is not in sudoers, using su instead")
                self.logger.debug(f"Running command: su root -c 'dpkg -i {path_to_deb}")

                subprocess.run(
                    f"su root -c 'dpkg -i {path_to_deb}'".split(), capture_output=True)

                subprocess.run(
                    "su root -c 'apt-get install -f'".split(), capture_output=True)

                is_installed = True

        return is_installed

    def run(self, tmpfolder, dpkg_in_path, data_dir, is_extracted):
        # Unzip the IPA file
        if not is_extracted:
            self.logger.log(f"Unzipping IPA...", color=Colors.pink)
            with zipfile.ZipFile(f"{tmpfolder}/app.ipa", 'r') as f:
                os.makedirs(f"{tmpfolder}/app", exist_ok=False)
                f.extractall(f"{tmpfolder}/app")
            print()

        # Read data from the plist
        self.logger.log(f"Reading plist...", color=Colors.pink)
        if Path(f"{tmpfolder}/app/Payload").exists():
            for fname in os.listdir(path=f"{tmpfolder}/app/Payload"):
                if fname.endswith(".app"):
                    app_dir = fname
            print("Found app directory!")
        else:
            self.logger.error(f"IPA/deb is not valid!")
            exit(1)

        pre_app_path = os.path.join(f"{tmpfolder}/app/Payload", app_dir)

        if Path(f'{pre_app_path}/Info.plist').exists():
            print("Found Info.plist")
            with open(f'{pre_app_path}/Info.plist', 'rb') as f:
                info = plistlib.load(f)
                if self.args.name:
                    app_name = self.args.name
                else:
                    app_name = info["CFBundleName"]

                if self.args.bundleid:
                    app_bundle = self.args.bundleid
                elif "science.xnu.undecimus" in info["CFBundleIdentifier"]:
                    app_bundle = "8H69ZMY835.science.xnu.undecimus.8H69ZMY835"
                else:
                    app_bundle = info["CFBundleIdentifier"]

                app_version = info["CFBundleShortVersionString"]

                if self.args.minver:
                    app_min_ios = self.args.minver
                else:
                    app_min_ios = info["MinimumOSVersion"]

                app_author = app_bundle.split(".")[1]

                app_executable = info["CFBundleExecutable"]
                print("Found information about the app!")
        print()

        # Get the deb file ready
        self.logger.log(f"Preparing deb file...", color=Colors.pink)
        print("Making directories...")
        os.makedirs(f"{tmpfolder}/deb/Applications", exist_ok=False)
        os.makedirs(f"{tmpfolder}/deb/DEBIAN", exist_ok=False)
        print("Copying deb file scripts and control...")
        copier = Copier(app_name, app_bundle, app_version, app_min_ios, app_author, self.in_package)
        copier.copy_postrm(f"{tmpfolder}/deb/DEBIAN/postrm")
        copier.copy_postinst(f"{tmpfolder}/deb/DEBIAN/postinst")
        copier.copy_control(f"{tmpfolder}/deb/DEBIAN/control")
        print("Copying app files...")
        full_app_path = os.path.join(f"{tmpfolder}/deb/Applications", app_dir)
        copytree(pre_app_path, full_app_path)
        print("Changing deb file scripts permissions...")
        subprocess.run(
            f"chmod 0755 {tmpfolder}/deb/DEBIAN/postrm".split(), stdout=DEVNULL)
        subprocess.run(
            f"chmod 0755 {tmpfolder}/deb/DEBIAN/postinst".split(), stdout=DEVNULL)
        if app_executable is not None:
            print("Changing app executable permissions...")
            exec_path = os.path.join(full_app_path, app_executable)
            subprocess.run(['chmod', '0755', f'{exec_path}'])
        print()

        # Sign the app
        self.logger.log(f"Signing app...", color=Colors.pink)
        copier.copy_entitlements(f"{tmpfolder}/entitlements.plist")
        if self.in_package:
            cert_path = self.utils.get_resource_path(__name__, "data/certificate.p12")
        else:
            cert_path = "permasigner/data/certificate.p12"

        if self.args.codesign:
            print("Signing with codesign as it was specified...")
            subprocess.run(
                ['security', 'import', cert_path, '-P', 'password', '-A'], stdout=DEVNULL)

            subprocess.run(['codesign', '-s', 'We Do A Little Trolling iPhone OS Application Signing',
                            '--force', '--deep', '--preserve-metadata=entitlements', f'{full_app_path}'],
                           stdout=DEVNULL)
        else:
            print("Signing with ldid...")
            if self.utils.is_ios():
                ldid_cmd = 'ldid'
            else:
                ldid_cmd = f'{data_dir}/ldid'
            self.logger.debug(
                f"Running command: {ldid_cmd} -S{tmpfolder}/entitlements.plist -M -K{cert_path} -Upassword '{full_app_path}'")

            subprocess.run([f'{ldid_cmd}', f'-S{tmpfolder}/entitlements.plist', '-M',
                            f'-K{cert_path}', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)

            if self.args.entitlements:
                self.logger.debug(f"Signing with extra entitlements located in {self.args.entitlements}")
                subprocess.run([f'{ldid_cmd}', f'-S{self.args.entitlements}', '-M',
                                f'-K{cert_path}', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)
        print()

        # Package the deb file
        self.logger.log(f"Packaging the deb file...", color=Colors.pink)
        if self.args.output:
            path_to_deb = self.args.output
        elif self.in_package:
            os.makedirs(f"{data_dir}/output", exist_ok=True)
            path_to_deb = f"{data_dir}/output/{app_name.replace(' ', '')}.deb"
        else:
            os.makedirs("output", exist_ok=True)
            path_to_deb = f"output/{app_name.replace(' ', '')}.deb"

        dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb {path_to_deb}"

        if dpkg_in_path:
            self.logger.debug(f"Path to deb file: {path_to_deb}")
            self.logger.debug(f"Running command: {dpkg_cmd}")

            subprocess.run(
                ["dpkg-deb", "-Zxz", "--root-owner-group", "-b", f"{tmpfolder}/deb", f"{path_to_deb}"], stdout=DEVNULL)
        else:
            self.logger.debug(f"Running command: {data_dir}/{dpkg_cmd}")

            subprocess.run(
                [f"{data_dir}/dpkg-deb", "-Zxz", "--root-owner-group", "-b", f"{tmpfolder}/deb", f"{path_to_deb}"],
                stdout=DEVNULL)
        print()

        return path_to_deb
