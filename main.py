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
from utils.copy import Copy
from utils.downloader import DpkgDeb

""" Main Function """
def main(args):
    print(f"IPA Permasigner | Version {subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}-{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}")
    print("Program created by Nebula | Original scripts created by zhuowei | CoreTrust bypass by Linus Henze")
    print("")
    
    # Check if script is running on Windows, if so, fail
    if sys.platform == "windows":
        print("[-] Script must be ran on macOS or Linux.")
        exit(1)
        
    # Check if codesign is added on Linux
    if args.codesign:
        if sys.platform == "linux":
            print("[-] You cannot use codesign on Linux, remove the argument and it'll use ldid instead.")
            exit(1)
        
    # Auto download ldid
    if not Path(f"{os.getcwd()}/ldid").exists():
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
            
    # Auto download dpkg-deb on Linux
    if not Path(f"{os.getcwd()}/dpkg-deb").exists():
        print("[*] dpkg-deb not found, downloading.")
        if sys.platform == "linux" and platform.machine() == "x86_64":
            DpkgDeb.download_linux_64()
        elif sys.platform == "linux" and platform.machine() == "aarch64":
            DpkgDeb.download_linux_arm64()
        elif sys.platform == "darwin" and platform.machine() == "x86_64":
            if ("dpkg not found" in subprocess.run("which dpkg".split(), capture_output=True, text=True).stdout) or (subprocess.run("which dpkg".split(), capture_output=True, text=True).stdout == ""):
                print("[-] dpkg is not installed and is required on macOS. Install it though brew or Procursus to continue.")
                exit(1)
        elif sys.platform == "darwin" and platform.machine() == "arm64":
            if ("dpkg not found" in subprocess.run("which dpkg".split(), capture_output=True, text=True).stdout) or (subprocess.run("which dpkg".split(), capture_output=True, text=True).stdout == ""):
                print("[-] dpkg is not installed and is required on macOS. Install it though brew or Procursus to continue.")
                exit(1)
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
            
            if path.strip()[-1] == " ":
                path = path.strip()[:-1]
            
            if Path(path).exists():
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
        
        if Path(f"{tmpfolder}/app/Payload").exists():
            for fname in os.listdir(path=f"{tmpfolder}/app/Payload"):
                if fname.endswith(".app"):
                    folder = fname
            print("Found plist!")
        else:
            print("[-] IPA is not valid!")
            exit(1)
            
        if Path(f"{tmpfolder}/app/Payload/{folder}/Info.plist").exists():
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
        Copy.copy_postrm(f"{tmpfolder}/deb/DEBIAN/postrm", app_name)
        Copy.copy_postinst(f"{tmpfolder}/deb/DEBIAN/postinst", app_name)
        Copy.copy_control(f"{tmpfolder}/deb/DEBIAN/control", app_name, app_bundle, app_version, app_min_ios, app_author)
        print("Copying app files...")
        copytree(f"{tmpfolder}/app/Payload/{folder}", f"{tmpfolder}/deb/Applications/{folder}", dirs_exist_ok=False)
        print("Changing deb file scripts permissions...")
        subprocess.run(f"chmod 0755 {tmpfolder}/deb/DEBIAN/postrm".split(), stdout=subprocess.DEVNULL)
        subprocess.run(f"chmod 0755 {tmpfolder}/deb/DEBIAN/postinst".split(), stdout=subprocess.DEVNULL)
        if app_executable is not None:
            print("Changing app executable permissions...")
            full_path = f"'{tmpfolder}/deb/Applications/{folder}/{app_executable}'"
            os.system("chmod 0755 " + full_path)
        print("")
        
        # Sign the app
        print("[*] Signing app...")
        Copy.copy_entitlements(f"{tmpfolder}/entitlements.plist", app_bundle)
        if args.codesign:
            print("Signing with codesign as it was specified...")
            subprocess.run(f"security import ./dev_certificate.p12 -P password -A".split(), stdout=subprocess.DEVNULL)
            full_path = f"'{tmpfolder}/deb/Applications/{folder}'"
            frameworks_path = f"'{tmpfolder}/deb/Applications/{folder}/Frameworks'"
            os.system("codesign -s 'Worth Doing Badly iPhone OS Application Signing' --force --deep --preserve-metadata=entitlements " + full_path)
            
            if Path(frameworks_path).exists():
                for path in Path(frameworks_path).rglob('*.dylib'):
                    print(f"Signing framework {path.name.split('.')[0]}...")
                    os.system("codesign -s 'Worth Doing Badly iPhone OS Application Signing' --force --deep --preserve-metadata=entitlements " + path)
                    
                frameworks = []
                for fname in os.listdir(path=frameworks_path):
                    if fname.endswith(".framework"):
                        frameworks.append(fname)
                
                for folder in frameworks:
                    dirs = os.listdir(folder)
                    for path in dirs:
                        if "." not in path:
                            os.system("codesign -s 'Worth Doing Badly iPhone OS Application Signing' --force --deep --preserve-metadata=entitlements " + path)
        else:
            print("Signing with ldid...")
            subprocess.run("chmod +x ldid".split(), stdout=subprocess.DEVNULL)
            full_path = f"'{tmpfolder}/deb/Applications/{folder}'"
            frameworks_path = f"'{tmpfolder}/deb/Applications/{folder}/Frameworks'"
            os.system(f"./ldid -S{tmpfolder}/entitlements.plist -M -Upassword -Kdev_certificate.p12 " + full_path)
            
            if Path(frameworks_path).exists():
                for path in Path(frameworks_path).rglob('*.dylib'):
                    print(f"Signing framework {path.name.split('.')[0]}...")
                    os.system(f"./ldid -S{tmpfolder}/entitlements.plist -M -Upassword -Kdev_certificate.p12 " + path)
                    
                frameworks = []
                for fname in os.listdir(path=frameworks_path):
                    if fname.endswith(".framework"):
                        frameworks.append(fname)
                
                for folder in frameworks:
                    dirs = os.listdir(folder)
                    for path in dirs:
                        if "." not in path:
                            os.system(f"./ldid -S{tmpfolder}/entitlements.plist -M -Upassword -Kdev_certificate.p12 " + path)
                            os.system(f"chmod 0755 {path}")
        print("")

        # Package the deb file
        print("[*] Packaging the deb file...")
        os.makedirs("output", exist_ok=True)
        if Path(f"output/{app_name}.deb").exists():
            os.remove(f"output/{app_name}.deb")
        if sys.platform == "darwin":
            subprocess.run(f"dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb output/{app_name}.deb".split(), stdout=subprocess.DEVNULL)
        else:
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
