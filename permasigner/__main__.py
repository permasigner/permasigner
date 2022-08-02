import os
from pathlib import Path
from shutil import copy, copytree
import plistlib
import requests
from urllib.parse import urlparse
import zipfile
import sys
import subprocess
import tempfile
import platform
import argparse
from glob import glob
from subprocess import DEVNULL
import pkgutil

from .ps_copier import Copier
from .ps_hash import LdidHash
from .ps_downloader import DpkgDeb, Ldid
from . import __version__
from .ps_utils import Utils
from .ps_logger import Logger, Colors


if not Utils.is_ios():
    from .ps_usbmux import USBMux
    from .ps_installer import Installer


""" Main Function """


def main(args, in_package=False):
    data_dir = f"{Utils.get_home_data_directory(args)}/.permasigner"
    os.makedirs(data_dir, exist_ok=True)

    if in_package:
        if args.debug:
            Logger.debug(f"Running from package, not cloned repo.")

    ldid_in_path = Utils.cmd_in_path(args, 'ldid')
    dpkg_in_path = Utils.cmd_in_path(args, 'dpkg-deb')
    git_in_path = Utils.cmd_in_path(args, 'git')

    if git_in_path:
        if args.debug:
            Logger.debug(f"Git is in PATH")

        if in_package:
            ver_string = f"{__version__.__version__}"
        elif not "main" in subprocess.getoutput(['git', 'rev-parse', '--abbrev-ref', 'HEAD']):
            ver_string = f"{subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}_{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
        else:
            ver_string = f"{__version__.__version__}_rev-{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"

    else:
        if args.debug:
            Logger.debug(f"Git is not in PATH")

        ver_string = f"{__version__.__version__}"

    print(Colors.bold + f"Permasigner | Version {ver_string}")
    print(Colors.bold + "Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")
    print()

    # Check if script is running on Windows, if so, fail
    if sys.platform == "windows":
        Logger.error(f"Script must be ran on macOS or Linux.")
        exit(1)

    # Auto download ldid
    if not ldid_in_path:
        if Path(f"{data_dir}/ldid").exists():
            if Utils.is_linux() and platform.machine() == "x86_64":
                if not LdidHash.check_linux_64(args, data_dir):
                    Logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
                    os.remove(f"{data_dir}/ldid")
                    Ldid.download_linux_64(args)
            elif Utils.is_linux() and platform.machine() == "aarch64":
                if not LdidHash.check_linux_arm64(args, data_dir):
                    Logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
                    os.remove(f"{data_dir}/ldid")
                    Ldid.download_linux_arm64(args)
            elif Utils.is_macos() and platform.machine() == "x86_64":
                if not LdidHash.check_macos_64(args, data_dir):
                    Logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
                    os.remove(f"{data_dir}/ldid")
                    Ldid.download_macos_64(args)
            elif Utils.is_macos() and platform.machine() == "arm64":
                if not LdidHash.check_macos_arm64(args, data_dir):
                    Logger.log(f"ldid is outdated or malformed, downloading latest version...", color=Colors.pink)
                    os.remove(f"{data_dir}/ldid")
                    Ldid.download_macos_arm64(args)
        else:
            Logger.log("ldid binary is not found, downloading latest binary.", color=Colors.pink)
            if Utils.is_linux() and platform.machine() == "x86_64":
                Ldid.download_linux_64(args)
            elif Utils.is_linux() and platform.machine() == "aarch64":
                Ldid.download_linux_arm64(args)
            elif Utils.is_macos() and platform.machine() == "x86_64":
                Ldid.download_macos_64(args)
            elif Utils.is_macos() and platform.machine() == "arm64":
                Ldid.download_macos_arm64(args)

    # Auto download dpkg-deb on Linux
    if not dpkg_in_path and Utils.is_linux():
        if not Path(f"{os.getcwd()}/dpkg-deb").exists():
            if platform.machine() == "x86_64":
                if args.debug:
                    Logger.debug(f"On Linux x86_64, dpkg-deb not found...")

                Logger.log(f"dpkg-deb not found, downloading.", color=Colors.pink)
                DpkgDeb.download_linux_64(args)
                print()
            elif platform.machine() == "aarch64":
                if args.debug:
                    Logger.debug(f"On Linux aarch64, dpkg-deb not found...")

                Logger.log(f"dpkg-deb not found, downloading.", color=Colors.pink)
                DpkgDeb.download_linux_arm64(args)
                print()

    if Utils.is_macos():
        if not subprocess.getstatusoutput("which dpkg")[0] == 0:
            if args.debug:
                Logger.debug(f"On macOS x86_64, dpkg not found...")
            Logger.error("dpkg is not installed and is required on macOS. Install it though brew or Procursus to continue.")
            exit(1)

    # Prompt the user if they'd like to use an external IPA or a local IPA
    if not (args.url or args.path):
        option = Logger.ask("Would you like to use an external or a local IPA? [E, L] ").lower()
        print()

    with tempfile.TemporaryDirectory() as tmpfolder:
        Logger.log(f"Created temporary directory.", color=Colors.pink)
        print()

        # If the user's choice is external, download an IPA
        # Otherwise, copy the IPA to the temporary directory
        if args.url:
            url = args.url

            if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                Logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                exit(1)

            res = requests.get(url, stream=True)

            try:
                if res.status_code == 200:
                    Logger.log(f"Downloading file...", color=Colors.pink)

                    with open(f"{tmpfolder}/app.ipa", "wb") as f:
                        f.write(res.content)
                else:
                    Logger.error(f"URL provided is not reachable. Status code: {res.status_code}")
                    exit(1)
            except requests.exceptions.RequestException as err:
                Logger.error(f"URL provided is not reachable. Error: {err}")
                exit(1)
        elif args.path:
            path = args.path
            path = path.strip().lstrip("'").rstrip("'")

            if Path(path).exists():
                copy(path, f"{tmpfolder}/app.ipa")
            else:
                priLogger.errornt("That file does not exist! Make sure you're using a direct path to the IPA file.")
                exit(1)
        elif option == "e":
            url = Logger.ask("Paste in the *direct* path to an IPA online: ")

            if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                Logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                exit(1)

            res = requests.get(url, stream=True)

            try:
                if res.status_code == 200:
                    Logger.log(f"Downloading file...", color=Colors.pink)

                    with open(f"{tmpfolder}/app.ipa", "wb") as f:
                        f.write(res.content)
                else:
                    Logger.error(f"URL provided is not reachable. Status code: {res.status_code}")
                    exit(1)
            except requests.exceptions.RequestException as err:
                Logger.error(f"URL provided is not reachable. Error: {err}")
                exit(1)
        elif option == "l":
            if os.environ.get('IS_DOCKER_CONTAINER', False):
                Logger.info("Running in Docker container, please place an IPA in the 'ipas' folder, then put the name of the file below.")
                ipa_name = input(Colors.orange + '    IPA name (ex. Taurine.ipa, DemoApp.ipa): ' + Colors.reset)
                path = f"/usr/src/permasigner/ipas/{ipa_name}"
            else:
                path = Logger.ask("Paste in the path to an IPA in your file system: ")

            path = path.strip().lstrip("'").rstrip("'")

            if Path(path).exists():
                copy(path, f"{tmpfolder}/app.ipa")
            else:
                Logger.error("That file does not exist! Make sure you're using a direct path to the IPA file.")
                exit(1)
        else:
            Logger.error(f"That is not a valid option!")
            exit(1)
        print()

        # Unzip the IPA file
        Logger.log(f"Unzipping IPA...", color=Colors.pink)
        with zipfile.ZipFile(f"{tmpfolder}/app.ipa", 'r') as f:
            os.makedirs(f"{tmpfolder}/app", exist_ok=False)
            f.extractall(f"{tmpfolder}/app")
        print()

        # Read data from the plist
        Logger.log(f"Reading plist...", color=Colors.pink)

        if Path(f"{tmpfolder}/app/Payload").exists():
            for fname in os.listdir(path=f"{tmpfolder}/app/Payload"):
                if fname.endswith(".app"):
                    app_dir = fname
            print("Found app directory!")
        else:
            Logger.error(f"IPA is not valid!")
            exit(1)

        pre_app_path = os.path.join(f"{tmpfolder}/app/Payload", app_dir)

        if Path(f'{pre_app_path}/Info.plist').exists():
            print("Found Info.plist")
            with open(f'{pre_app_path}/Info.plist', 'rb') as f:
                info = plistlib.load(f)
                if args.name:
                    app_name = args.name
                else:
                    app_name = info["CFBundleName"]

                if args.bundleid:
                    app_bundle = args.bundleid
                else:
                    app_bundle = info["CFBundleIdentifier"]

                app_version = info["CFBundleShortVersionString"]

                if args.minver:
                    app_min_ios = args.minver
                else:
                    app_min_ios = info["MinimumOSVersion"]

                app_author = app_bundle.split(".")[1]
                app_author = app_author[0].upper() + app_author[1:]

                app_executable = info["CFBundleExecutable"]
                print("Found information about the app!")
        print()

        # Get the deb file ready
        Logger.log(f"Preparing deb file...", color=Colors.pink)
        print("Making directories...")
        os.makedirs(f"{tmpfolder}/deb/Applications", exist_ok=False)
        os.makedirs(f"{tmpfolder}/deb/DEBIAN", exist_ok=False)
        print("Copying deb file scripts and control...")
        Copier.copy_postrm(f"{tmpfolder}/deb/DEBIAN/postrm", app_name, in_package)
        Copier.copy_postinst(f"{tmpfolder}/deb/DEBIAN/postinst", app_name, in_package)
        Copier.copy_control(f"{tmpfolder}/deb/DEBIAN/control", app_name,
                            app_bundle, app_version, app_min_ios, app_author, in_package)
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
        Logger.log(f"Signing app...", color=Colors.pink)
        Copier.copy_entitlements(f"{tmpfolder}/entitlements.plist", app_bundle, in_package)
        frameworks_path = os.path.join(full_app_path, 'Frameworks')
        if in_package:
            cert_path = Utils.get_resource_path(__name__, "data/certificate.p12")
        else:
            cert_path = "permasigner/data/certificate.p12"

        print("Signing with ldid...")
        if Utils.is_ios():
            ldid_cmd = 'ldid'
        else:
            ldid_cmd = f'{data_dir}/ldid'
        if args.debug:
            Logger.debug(
                f"Running command: {ldid_cmd} -S{tmpfolder}/entitlements.plist -M -K{cert_path} -Upassword '{full_app_path}'")

        subprocess.run([f'{ldid_cmd}', f'-S{tmpfolder}/entitlements.plist', '-M',
                        f'-K{cert_path}', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)

        print()

        # Package the deb file
        Logger.log(f"Packaging the deb file...", color=Colors.pink)
        if args.output:
            path_to_deb = args.output
        elif in_package:
            os.makedirs(f"{Utils.get_home_data_directory(args)}/.permasigner/output", exist_ok=True)
            path_to_deb = f"{Utils.get_home_data_directory(args)}/.permasigner/output/{app_name.replace(' ', '')}.deb"
        else:
            os.makedirs("output", exist_ok=True)
            path_to_deb = f"output/{app_name.replace(' ', '')}.deb"

        dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb {path_to_deb}"

        if dpkg_in_path:
            if args.debug:
                Logger.debug(f"Path to deb file: {path_to_deb}")
                Logger.debug(f"Running command: {dpkg_cmd}")

            subprocess.run(f"{dpkg_cmd}".split(), stdout=DEVNULL)
        else:
            if args.debug:
                Logger.debug(f"Running command: ./{dpkg_cmd}")

            subprocess.run(f"{data_dir}/{dpkg_cmd}".split(), stdout=DEVNULL)

        is_installed = False
        if not args.noinstall:
            option = 'n'
            if not args.install:
                option = Logger.ask("Would you like install the application to your device (must be connected)? [y, n]: ").lower()

            if option == 'y' or args.install:
                if Utils.is_macos() or Utils.is_linux():
                    try:
                        mux = USBMux()
                        if not mux.devices:
                            mux.process(1.0)
                        if not mux.devices:
                            print("Did not find a connected device")
                        else:
                            print("Found a connected device")
                            Installer.install_deb(args, path_to_deb)
                            is_installed = True
                    except ConnectionRefusedError:
                        print("Did not find a connected device")
                        pass
                elif Utils.is_ios():
                    print("Checking if user is in sudoers")
                    p = subprocess.run('sudo -nv'.split(),
                                       capture_output=True)
                    if p.returncode == 0 or 'password' in p.stderr.decode():
                        print("User is in sudoers, using sudo command")
                        if args.debug:
                            Logger.debug(f"Running command: sudo dpkg -i {path_to_deb}")

                        subprocess.run(
                            ["sudo", "dpkg", "-i", f"{path_to_deb}"], capture_output=True)

                        subprocess.run(
                            ['sudo', 'apt-get', 'install', '-f'], capture_output=True)
                    else:
                        print("User is not in sudoers, using su instead")
                        if args.debug:
                            Logger.debug(f"Running command: su root -c 'dpkg -i {path_to_deb}")

                        subprocess.run(
                            f"su root -c 'dpkg -i {path_to_deb}'".split(), capture_output=True)

                        subprocess.run(
                            "su root -c 'apt-get install -f'".split(), capture_output=True)

    # Done!!!
    print()
    Logger.log(f"We are finished!", color=Colors.green)

    if is_installed:
        Logger.log(f"The application was installed to your device, no further steps are required!", color=Colors.green)
    else:
        Logger.log(f"Copy the newly created deb from the output folder to your jailbroken iDevice and install it!", color=Colors.green)

    Logger.log(f"The app will continue to work when rebooted to stock.", color=Colors.green)
    Logger.log(f"Also, this is free and open source software! Feel free to donate to my Patreon if you enjoy :)", color=Colors.green)
    print(Colors.green + "    https://patreon.com/nebulalol" + Colors.reset)
    Logger.log(f"Output file: {path_to_deb}", color=Colors.green)
