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

from .copy import Copy
from .hash import LdidHash
from .downloader import DpkgDeb, Ldid
from . import __version__
from .utils import Utils


if not Utils.is_ios():
    from .usbmux import USBMux
    from .installer import Installer


""" Main Function """


def main(args, in_package=False):
    if in_package:
        if args.debug:
            print("[DEBUG] Running from package, not cloned repo.")
    
    ldid_in_path = Utils.cmd_in_path(args, 'ldid')
    dpkg_in_path = Utils.cmd_in_path(args, 'dpkg-deb')
    git_in_path = Utils.cmd_in_path(args, 'git')
    
    if git_in_path:
        if args.debug:
            print(f"[DEBUG] Git is in PATH")
            
        if in_package: 
            ver_string = f"{__version__.__version__}"
        elif not "main" in subprocess.getoutput(['git', 'rev-parse', '--abbrev-ref', 'HEAD']):
            ver_string = f"{subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}_{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
        else:
            ver_string = f"{__version__.__version__}_rev-{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
            
    else:
        if args.debug:
            print(f"[DEBUG] Git is not in PATH")
        
        ver_string = f"{__version__.__version__}"

    print(
        f"IPA Permasigner | Version {ver_string}")
    print("Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")
    print()

    # Check if script is running on Windows, if so, fail
    if sys.platform == "windows":
        print("[-] Script must be ran on macOS or Linux.")
        exit(1)

    # Check if codesign is added on Linux or iOS
    if args.codesign:
        if not Utils.is_macos():
            print(
                "[-] Codesign can only be used on macOS, remove the argument to use ldid instead.")
            exit(1)

    # Auto download ldid
    if not ldid_in_path:
        if Path(f"{os.getcwd()}/ldid").exists():
            if Utils.is_linux() and platform.machine() == "x86_64":
                if args.debug:
                    print(f"[DEBUG] On Linux x86_64, ldid not found...")

                if not LdidHash.check_linux_64(args):
                    print(
                        "[*] ldid is outdated or malformed, downloading latest version...")
                    os.remove(f"{os.getcwd()}/ldid")
                    Ldid.download_linux_64(args)
            elif Utils.is_linux() and platform.machine() == "aarch64":
                if args.debug:
                    print(f"[DEBUG] On Linux aarch64, ldid not found...")

                if not LdidHash.check_linux_arm64(args):
                    print(
                        "[*] ldid is outdated or malformed, downloading latest version...")
                    os.remove(f"{os.getcwd()}/ldid")
                    Ldid.download_linux_arm64(args)
            elif Utils.is_macos() and platform.machine() == "x86_64":
                if args.debug:
                    print(f"[DEBUG] On macOS x86_64, ldid not found...")

                if not LdidHash.check_macos_64(args):
                    print(
                        "[*] ldid is outdated or malformed, downloading latest version...")
                    os.remove(f"{os.getcwd()}/ldid")
                    Ldid.download_macos_64(args)
            elif Utils.is_macos() and platform.machine() == "arm64":
                if args.debug:
                    print(f"[DEBUG] On macOS arm64, ldid not found...")

                if not LdidHash.check_macos_arm64(args):
                    print(
                        "[*] ldid is outdated or malformed, downloading latest version...")
                    os.remove(f"{os.getcwd()}/ldid")
                    Ldid.download_macos_arm64(args)
        else:
            print(
                "[*] ldid binary is not found or fails hash check, downloading latest binary.")
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
                    print(f"[DEBUG] On Linux x86_64, dpkg-deb not found...")

                print("[*] dpkg-deb not found, downloading.")
                DpkgDeb.download_linux_64(args)
                print()
            elif platform.machine() == "aarch64":
                if args.debug:
                    print(f"[DEBUG] On Linux aarch64, dpkg-deb not found...")

                print("[*] dpkg-deb not found, downloading.")
                DpkgDeb.download_linux_arm64(args)
                print()

    if Utils.is_macos():
        if not subprocess.getstatusoutput("which dpkg")[0] == 0:
            if args.debug:
                print(f"[DEBUG] On macOS x86_64, dpkg not found...")
            print(
                "[-] dpkg is not installed and is required on macOS. Install it though brew or Procursus to continue.")
            exit(1)

    # Prompt the user if they'd like to use an external IPA or a local IPA
    if not (args.url or args.path):
        option = input(
            "[?] Would you like to use an external or a local IPA? [E, L] ").lower()

    with tempfile.TemporaryDirectory() as tmpfolder:
        print("[*] Created temporary directory.")
        print()

        # If the user's choice is external, download an IPA
        # Otherwise, copy the IPA to the temporary directory
        if args.url:
            url = args.url

            if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                print(
                    "[-] URL provided is not an IPA, make sure to provide a direct link.")
                exit(1)

            res = requests.get(url, stream=True)

            try:
                if res.status_code == 200:
                    print(f"[*] Downloading file...")

                    with open(f"{tmpfolder}/app.ipa", "wb") as f:
                        f.write(res.content)
                else:
                    print(
                        f"[-] URL provided is not reachable. Status code: {res.status_code}")
                    exit(1)
            except requests.exceptions.RequestException as err:
                print(f"[-] URL provided is not reachable. Error: {err}")
                exit(1)
        elif args.path:
            path = args.path
            path = path.strip().lstrip("'").rstrip("'")

            if Path(path).exists():
                copy(path, f"{tmpfolder}/app.ipa")
            else:
                print(
                    "[-] That file does not exist! Make sure you're using a direct path to the IPA file.")
                exit(1)
        elif option == "e":
            url = input("[?] Paste in the *direct* path to an IPA online: ")

            if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                print(
                    "[-] URL provided is not an IPA, make sure to provide a direct link.")
                exit(1)

            res = requests.get(url, stream=True)

            try:
                if res.status_code == 200:
                    print(f"[*] Downloading file...")

                    with open(f"{tmpfolder}/app.ipa", "wb") as f:
                        f.write(res.content)
                else:
                    print(
                        f"[-] URL provided is not reachable. Status code: {res.status_code}")
                    exit(1)
            except requests.exceptions.RequestException as err:
                print(f"[-] URL provided is not reachable. Error: {err}")
                exit(1)
        elif option == "l":
            if os.environ.get('IS_DOCKER_CONTAINER', False):
                print(
                    "[*] Running in Docker container, please place an IPA in the ipas folder, then put the name of the file below.")
                ipa_name = input(
                    '    IPA name (ex. Taurine.ipa, DemoApp.ipa): ')
                path = f"/usr/src/permasigner/ipas/{ipa_name}"
            else:
                path = input(
                    "[?] Paste in the path to an IPA in your file system: ")

            path = path.strip().lstrip("'").rstrip("'")

            if Path(path).exists():
                copy(path, f"{tmpfolder}/app.ipa")
            else:
                print(
                    "[-] That file does not exist! Make sure you're using a direct path to the IPA file.")
                exit(1)
        else:
            print("[-] That is not a valid option!")
            exit(1)
        print()

        # Unzip the IPA file
        print("[*] Unzipping IPA...")
        with zipfile.ZipFile(f"{tmpfolder}/app.ipa", 'r') as f:
            os.makedirs(f"{tmpfolder}/app", exist_ok=False)
            f.extractall(f"{tmpfolder}/app")
        print()

        # Read data from the plist
        print("[*] Reading plist...")

        if Path(f"{tmpfolder}/app/Payload").exists():
            for fname in os.listdir(path=f"{tmpfolder}/app/Payload"):
                if fname.endswith(".app"):
                    app_dir = fname
            print("Found app directory!")
        else:
            print("[-] IPA is not valid!")
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
                app_executable = info["CFBundleExecutable"]
                print("Found information about the app!")
        print()

        # Get the deb file ready
        print("[*] Preparing deb file...")
        print("Making directories...")
        os.makedirs(f"{tmpfolder}/deb/Applications", exist_ok=False)
        os.makedirs(f"{tmpfolder}/deb/DEBIAN", exist_ok=False)
        print("Copying deb file scripts and control...")
        Copy.copy_postrm(f"{tmpfolder}/deb/DEBIAN/postrm", app_name)
        Copy.copy_postinst(f"{tmpfolder}/deb/DEBIAN/postinst", app_name)
        Copy.copy_control(f"{tmpfolder}/deb/DEBIAN/control", app_name,
                          app_bundle, app_version, app_min_ios, app_author)
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
        print("[*] Signing app...")
        Copy.copy_entitlements(f"{tmpfolder}/entitlements.plist", app_bundle)
        frameworks_path = os.path.join(full_app_path, 'Frameworks')
        if args.codesign:
            print("Signing with codesign as it was specified...")
            subprocess.run(
                ['security', 'import', './data/certificate.p12', '-P', 'password', '-A'], stdout=DEVNULL)

            subprocess.run(['codesign', '-s', 'We Do A Little Trolling iPhone OS Application Signing',
                            '--force', '--deep', '--preserve-metadata=entitlements', f'{full_app_path}'], stdout=DEVNULL)
        else:
            print("Signing with ldid...")
            if Utils.is_ios():
                ldid_cmd = 'ldid'
            else:
                ldid_cmd = './ldid'
            if args.debug:
                print(
                    f"[DEBUG] Running command: {ldid_cmd} -S{tmpfolder}/entitlements.plist -M -Kdata/certificate.p12 -Upassword '{full_app_path}'")

            subprocess.run([f'{ldid_cmd}', f'-S{tmpfolder}/entitlements.plist', '-M',
                            '-Kdata/certificate.p12', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)

        print()

        # Package the deb file
        print("[*] Packaging the deb file...")
        if args.output:
            path_to_deb = args.output
        elif in_package:
            path_to_deb = f"{Utils.get_home_data_directory(args)}/.permasigner/output/{app_name.replace(' ', '')}.deb"
        else:
            os.makedirs("output", exist_ok=True)
            path_to_deb = f"output/{app_name.replace(' ', '')}.deb"

        dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb {path_to_deb}"

        if dpkg_in_path:
            if args.debug:
                print(f"[DEBUG] Path to deb file: {path_to_deb}")
                print(f"[DEBUG] Running command: {dpkg_cmd}")

            subprocess.run(f"{dpkg_cmd}".split(), stdout=DEVNULL)
        else:
            if args.debug:
                print(f"[DEBUG] Running command: ./{dpkg_cmd}")

            subprocess.run(f"./{dpkg_cmd}".split(), stdout=DEVNULL)

        is_installed = False
        if not args.noinstall:
            option = 'n'
            if not args.install:
                option = input(
                    "[?] Would you like install the application to your device (must be connected)? [y, n]: ").lower()

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
                            print(
                                f"[DEBUG] Running command: sudo dpkg -i {path_to_deb}")

                        subprocess.run(
                            ["sudo", "dpkg", "-i", f"{path_to_deb}"], capture_output=True)

                        subprocess.run(
                            ['sudo', 'apt-get', 'install', '-f'], capture_output=True)
                    else:
                        print("User is not in sudoers, using su instead")
                        if args.debug:
                            print(
                                f"[DEBUG] Running command: su root -c 'dpkg -i {path_to_deb}")

                        subprocess.run(
                            f"su root -c 'dpkg -i {path_to_deb}'".split(), capture_output=True)

                        subprocess.run(
                            "su root -c 'apt-get install -f'".split(), capture_output=True)

    # Done!!!
    print()
    print("[*] We are finished!")

    if is_installed:
        print(
            "[*] The application was installed to your device, no further steps are required!")
    else:
        print("[*] Copy the newly created deb from the output folder to your jailbroken iDevice and install it!")

    print("[*] The app will continue to work when rebooted to stock.")
    print("[*] Also, this is free and open source software! Feel free to donate to my Patreon if you enjoy :)")
    print("    https://patreon.com/nebulalol")
    print(f"[*] Output file: {path_to_deb}")
