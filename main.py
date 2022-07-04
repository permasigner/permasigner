import os
from pathlib import Path
from shutil import rmtree, copy, copytree
import plistlib
import requests
from urllib.parse import urlparse
import zipfile
import sys
import subprocess
import tempfile
import platform
import argparse

""" Functions """
def copy_postinst(file_path, app_name):
    """Copy postinst file.

    Args:
        file_path (String): Path of the copy destination.
        app_name (String): Name of the app being processed.
    """
    
    # Read the file
    with open("postinst", 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("{APP_NAME}", app_name)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(filedata)
        
def copy_postrm(file_path, app_name):
    """Copy postrm file.

    Args:
        file_path (String): Path of the copy destination.
        app_name (String): Name of the app being processed.
    """
    
    # Read the file
    with open('postrm', 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("{APP_NAME}", app_name)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(filedata)
        
def copy_control(file_path, app_name, app_bundle, app_version, app_min_ios, app_author):
    """Copy control file.

    Args:
        file_path (String): Path of the copy destination.
        app_name (String): Name of the app being processed.
        app_bundle (String): Bundle ID of the app being processed.
        app_version (String): Version of the app being processed.
        app_min_ios (String): Minimum iOS version required by the app being processed.
        app_author (String): Author of the app being processed.
    """
    
    # Read the file
    with open('control', 'r') as file:
        filedata = file.read()

    # Replace the target strings
    filedata = filedata.replace("{APP_NAME}", app_name)
    filedata = filedata.replace("{APP_BUNDLE}", app_bundle)
    filedata = filedata.replace("{APP_VERSION}", app_version)
    filedata = filedata.replace("{APP_MIN_IOS}", app_min_ios)
    filedata = filedata.replace("{APP_AUTHOR}", app_author)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(filedata)


""" Main Function """
def main(args):
    print(f"IPA Permasigner - Version {subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}")
    print("Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")
    print("")
    
    # Check if script is running on Windows, if so, fail
    if sys.platform == "windows":
        print("[-] Script must be ran on macOS or Linux.")
        exit(1)
        
    # Auto download ldid
    if not os.path.exists("ldid"):
        print("[*] ldid not found, downloading.")
        if sys.platform == "linux" and platform.machine() == "x86_64":
            subprocess.run(f"curl -sLO https://nightly.link/ProcursusTeam/ldid/workflows/build/master/ldid_linux_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"unzip ldid_linux_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"rm ldid_linux_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        elif sys.platform == "linux" and platform.machine() == "aarch64":
            subprocess.run(f"curl -sLO https://nightly.link/ProcursusTeam/ldid/workflows/build/master/ldid_linux_aarch64.zip".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"unzip ldid_linux_aarch64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"rm ldid_linux_aarch64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        elif sys.platform == "darwin" and platform.machine() == "x86_64":
            subprocess.run(f"curl -sLO https://nightly.link/ProcursusTeam/ldid/workflows/build/master/ldid_macos_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"unzip ldid_macos_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"rm ldid_macos_x86_64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        elif sys.platform == "darwin" and platform.machine() == "arm64":
            subprocess.run(f"curl -sLO https://nightly.link/ProcursusTeam/ldid/workflows/build/master/ldid_macos_arm64.zip".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"unzip ldid_macos_arm64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"rm ldid_macos_arm64.zip".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
            
    # Auto download dpkg-deb
    if not os.path.exists("dpkg-deb"):
        print("[*] dpkg-deb not found, downloading.")
        if sys.platform == "linux" and platform.machine() == "x86_64":
            subprocess.run(f"curl -sLO http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.20.9_amd64.deb".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"ar x dpkg_1.20.9_amd64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"tar -xf data.tar.xz".split(), stdout=subprocess.DEVNULL)
            copy("usr/bin/dpkg-deb", "dpkg-deb")
            subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
            os.remove("data.tar.xz")
            os.remove("control.tar.xz")
            os.remove("debian-binary")
            os.remove("dpkg_1.20.9_amd64.deb")
            rmtree("etc")
            rmtree("sbin")
            rmtree("usr")
            rmtree("var")
        elif sys.platform == "linux" and platform.machine() == "aarch64":
            subprocess.run(f"curl -sLO http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.20.9_arm64.deb".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"ar x dpkg_1.20.9_arm64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"tar -xf data.tar.xz".split(), stdout=subprocess.DEVNULL)
            copy("usr/bin/dpkg-deb", "dpkg-deb")
            subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
            os.remove("data.tar.xz")
            os.remove("control.tar.xz")
            os.remove("debian-binary")
            os.remove("dpkg_1.20.9_arm64.deb")
            rmtree("etc")
            rmtree("sbin")
            rmtree("usr")
            rmtree("var")
        elif sys.platform == "darwin" and platform.machine() == "x86_64":
            subprocess.run(f"curl -sLO https://procursus.itsnebula.net/pool/main/big_sur/dpkg_1.21.8_darwin-amd64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run("curl -sLO https://cameronkatri.com/zstd".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x zstd".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"ar x dpkg_1.21.8_darwin-arm64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"./zstd -d data.tar.zst".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"tar -xf data.tar".split(), stdout=subprocess.DEVNULL)
            copy("opt/procursus/bin/dpkg-deb", "dpkg-deb")
            subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
            os.remove("data.tar.zst")
            os.remove("data.tar")
            os.remove("control.tar.zst")
            os.remove("debian-binary")
            os.remove("dpkg_1.21.8_darwin-arm64.deb")
            os.remove("zstd")
            rmtree("opt")
        elif sys.platform == "darwin" and platform.machine() == "arm64":
            subprocess.run(f"curl -sLO https://procursus.itsnebula.net/pool/main/big_sur/dpkg_1.21.8_darwin-arm64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run("curl -sLO https://cameronkatri.com/zstd".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"chmod +x zstd".split(), stdout=subprocess.DEVNULL)
            print("Unzipping...")
            subprocess.run(f"ar x dpkg_1.21.8_darwin-arm64.deb".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"./zstd -d data.tar.zst".split(), stdout=subprocess.DEVNULL)
            subprocess.run(f"tar -xf data.tar".split(), stdout=subprocess.DEVNULL)
            copy("opt/procursus/bin/dpkg-deb", "dpkg-deb")
            subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
            os.remove("data.tar.zst")
            os.remove("data.tar")
            os.remove("control.tar.zst")
            os.remove("debian-binary")
            os.remove("dpkg_1.21.8_darwin-arm64.deb")
            os.remove("zstd")
            rmtree("opt")
        print()
    
    # Prompt the user if they'd like to use an external IPA or a local IPA
    option = input("[?] Would you like to use an IPA stored on the web, or on your system? [external, local] ")
    option = option.lower()
    
    with tempfile.TemporaryDirectory() as tmpfolder:
        print("[*] Created temporary directory.")
        print("")
        
        # If the user's choice is external, download an IPA
        # Otherwise, copy the IPA to the temporary directory
        if option == "external":
            url = input("[?] Paste in the *direct* path to an IPA online: ")
            
            if not os.path.splitext(urlparse(url).path)[1] == ".ipa":
                print("[-] URL provided is not an IPA, make sure to provide a direct link.")
                exit(1)
            
            res = requests.get(url, stream=True)
            
            try:
                if res.status_code == 200:
                    print(f"[*] Downloading file...")
                    
                    with open(f"{tmpfolder}/app.ipa", "wb") as f:
                        f.write(res.content)
                else:
                    print(f"[-] URL provided is not reachable. Status code: {res.status_code}")
                    exit(1)
            except requests.exceptions.RequestException as err:
                print(f"[-] URL provided is not reachable. Error: {err}")
                exit(1)  
        elif option == "local":
            path = input("[?] Paste in the path to an IPA in your file system: ")
            
            if os.path.exists(path):
                copy(path, f"{tmpfolder}/app.ipa")
            else:
                print("[-] That file does not exist! Make sure you're using a direct path to the IPA file.")
                exit(1)
        else:
            print("[-] That is not a valid option!")
            exit(1)
        print("")
        
        # Unzip the IPA file
        print("[*] Unzipping IPA...")
        with zipfile.ZipFile(f"{tmpfolder}/app.ipa", 'r') as f:
            os.makedirs(f"{tmpfolder}/app", exist_ok=False)
            f.extractall(f"{tmpfolder}/app")
        print("")
            
        # Read data from the plist
        print("[*] Reading plist...")
        global folder, app_name, app_bundle, app_version, app_min_ios, app_author, app_executable
        
        if os.path.exists(f"{tmpfolder}/app/Payload"):
            for fname in os.listdir(path=f"{tmpfolder}/app/Payload"):
                if fname.endswith(".app"):
                    folder = fname
            print("Found plist!")
        else:
            print("[-] IPA is not valid!")
            exit(1)
            
        if os.path.isfile(f"{tmpfolder}/app/Payload/{folder}/Info.plist"):
            with open(f"{tmpfolder}/app/Payload/{folder}/Info.plist", 'rb') as f:
                info = plistlib.load(f)
                app_name = info["CFBundleName"]
                app_bundle = info["CFBundleIdentifier"]
                app_version = info["CFBundleShortVersionString"]
                app_min_ios = info["MinimumOSVersion"]
                app_author = app_bundle.split(".")[1]
                if info["CFBundleExecutable"]:
                    app_executable = info["CFBundleExecutable"]
                    print("Executable found.")
                else:
                    app_executable = None
                    print("No executable found.")
                print("Found information about the app!")
        print("")
        
        # Get the deb file ready
        print("[*] Preparing deb file...")
        print("Making directories...")
        os.makedirs(f"{tmpfolder}/deb/Applications", exist_ok=False)
        os.makedirs(f"{tmpfolder}/deb/DEBIAN", exist_ok=False)
        print("Copying deb file scripts and control...")
        copy_postrm(f"{tmpfolder}/deb/DEBIAN/postrm", app_name)
        copy_postinst(f"{tmpfolder}/deb/DEBIAN/postinst", app_name)
        copy_control(f"{tmpfolder}/deb/DEBIAN/control", app_name, app_bundle, app_version, app_min_ios, app_author)
        print("Copying app files...")
        copytree(f"{tmpfolder}/app/Payload/{folder}", f"{tmpfolder}/deb/Applications/{folder}", dirs_exist_ok=False)
        print("Changing deb file scripts permissions...")
        subprocess.run(f"chmod 0755 {tmpfolder}/deb/DEBIAN/postrm".split(), stdout=subprocess.DEVNULL)
        subprocess.run(f"chmod 0755 {tmpfolder}/deb/DEBIAN/postinst".split(), stdout=subprocess.DEVNULL)
        if app_executable is not None:
            print("Changing app executable permissions...")
            subprocess.run(f"chmod 0755 {tmpfolder}/deb/Applications/{folder}/{app_executable}".split(), stdout=subprocess.DEVNULL)
        print("")
        
        # Sign the app
        print("[*] Signing app...")
        if args.codesign:
            print("Signing with codesign as it was specified...")
            subprocess.run(f"security import ./dev_certificate.p12 -P password -A".split(), stdout=subprocess.DEVNULL)
            os.system(f"codesign -s 'Worth Doing Badly iPhone OS Application Signing' --force --deep --preserve-metadata=entitlements --entitlements=app.entitlements {tmpfolder}/deb/Applications/{folder}")
        else:
            print("Signing with ldid...")
            subprocess.run("chmod +x ldid".split(), stdout=subprocess.DEVNULL)
            os.system(f"./ldid -Sapp.entitlements -M -Upassword -Kdev_certificate.p12 {tmpfolder}/deb/Applications/{folder}")
        print("")

        # Package the deb file
        print("[*] Packaging the deb file...")
        os.makedirs("output", exist_ok=True)
        if os.path.exists(f"output/{app_name}.deb"):
            os.remove(f"output/{app_name}.deb")
        subprocess.run(f"./dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb output/{app_name}.deb".split(), stdout=subprocess.DEVNULL)
        
    # Done!!!
    print("")
    print("[*] We are finished!")
    print("[*] Copy the newly created deb from the output folder to your jailbroken iDevice and install it!")
    print("[*] The app will continue to work when rebooted to stock.")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codesign', action='store_true', help="uses codesign instead of ldid.")
    args = parser.parse_args()
    
    main(args)
