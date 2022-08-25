import argparse
import os
from pathlib import Path, PurePath
from shutil import copy, copytree, rmtree
import plistlib
import requests
from requests import RequestException, ConnectionError
from urllib3.exceptions import NewConnectionError
import zipfile
import subprocess
import tempfile
from subprocess import DEVNULL
from glob import glob

from .ps_copier import Copier
from .ps_downloader import Ldid
from . import __version__
from .ps_utils import Utils
from .ps_logger import Logger, Colors
from .ps_builder import Deb, Control


""" Main Class """


def main(argv=None, in_package=None):
    if argv is None:
        in_package = True

    in_package = False if in_package is None else in_package

    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('-f', '--folder', type=str,
                             help="sign multiple IPAs from a direct path to a folder")
    input_group.add_argument('-u', '--url', type=str,
                             help="the direct URL of the IPA to be signed")
    input_group.add_argument('-p', '--path', type=str,
                             help="the direct local path of the IPA to be signed")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="shows some debug info, only useful for testing")
    parser.add_argument('-c', '--codesign', action='store_true',
                        help="uses codesign instead of ldid")
    parser.add_argument('-i', '--install', action='store_true',
                        help="installs the application to your device")
    parser.add_argument('-o', '--output', type=str,
                        help="specify output path")
    parser.add_argument('-b', '--bundleid', type=str,
                        help="specify new bundle id")
    parser.add_argument('-n', '--name', type=str,
                        help="specify new app name")
    parser.add_argument('-a', '--author', type=str,
                        help="specify new app author")
    parser.add_argument('-m', '--minver', type=str,
                        help="specify new minimum app version (14.0 recommended)")
    parser.add_argument('-v', '--version', action='store_true',
                        help='show current version and exit', )
    parser.add_argument('-l', '--ldidfork', type=str,
                        help="specify a fork of ldid (eg. ProcursusTeam, itsnebulalol [default])")
    parser.add_argument('-t', '--tcprelay', type=str,
                        help="args for tcprelay rport:lport:host:socketpath (ex: 22:2222:localhost:/var/run/usbmuxd)")
    parser.add_argument('-e', '--entitlements', type=str,
                        help="path to entitlements file")
    parser.add_argument('-N', '--no-ldid-check', dest='nocheckldid', action='store_true',
                        help="disable ldid hash checking")
    args = parser.parse_args()

    if args.version:
        from permasigner import __version__
        print(f"Permasigner v{__version__.__version__}")
        exit(0)

    ps = Permasigner(in_package, args)
    ps.start()


class Permasigner(object):
    def __init__(self, in_package, args):
        self.in_package = in_package
        self.args = args
        self.utils = Utils(self.args)
        self.logger = Logger(self.args)
        self.outputs = []

    def unpack(self, source, tmpfolder, dpkg_in_path):
        path = source.strip('"').strip("'").strip()
        path = Path(path).expanduser()

        if path.exists():
            if path.suffix == ".deb":
                self.logger.debug(f"Extracting deb package from {path} to {tmpfolder}/extractedDeb")
                if dpkg_in_path:
                    self.logger.debug(f"Running command: dpkg-deb -X {path} {tmpfolder}/extractedDeb")
                    subprocess.run(
                        ["dpkg-deb", "-X", path, PurePath(f'{tmpfolder}/extractedDeb')], stdout=DEVNULL)
                else:
                    deb = Deb(path, PurePath(f'{tmpfolder}/extractedDeb'), self.args)
                    deb.extract()

                Path(f"{tmpfolder}/app/Payload").mkdir(parents=True, exist_ok=False)
                for fname in Path(f"{tmpfolder}/extractedDeb/Applications").iterdir():
                    if fname.name.endswith(".app"):
                        copytree(f"{tmpfolder}/extractedDeb/Applications/{fname.name}",
                                 f"{tmpfolder}/app/Payload/{fname.name}")
                        break
            elif path.suffix == ".ipa":
                copy(path, f"{tmpfolder}/app.ipa")
                self.unzip(tmpfolder)
            else:
                self.logger.error("That file is not supported by Permasigner! Make sure you're using an IPA or deb.")
                exit(1)
        else:
            self.logger.error("That file does not exist! Make sure you're using a direct path to the IPA file.")
            exit(1)

    def unzip(self, tmpfolder):
        self.logger.log(f"Unzipping IPA...", color=Colors.yellow)
        with zipfile.ZipFile(PurePath(f'{tmpfolder}/app.ipa'), 'r') as f:
            with Path(f"{tmpfolder}/app") as path:
                path.mkdir(exist_ok=False)
                f.extractall(path)

    def start(self):
        data_dir = self.utils.get_home_data_directory()
        Path(data_dir).mkdir(exist_ok=True, parents=True)

        if self.in_package:
            self.logger.debug(f"Running from package, not cloned repo.")

        ldid_in_path = self.utils.cmd_in_path('ldid')
        dpkg_in_path = self.utils.cmd_in_path('dpkg-deb')
        git_in_path = self.utils.cmd_in_path('git')

        if git_in_path:
            self.logger.debug(f"Git is in PATH")

            if self.in_package:
                ver_string = f"{__version__.__version__}"
            elif "main" not in subprocess.getoutput([f'git', 'rev-parse', '--abbrev-ref', 'HEAD']):
                ver_string = f"{subprocess.check_output([f'git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}_{subprocess.check_output([f'git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
            else:
                ver_string = f"{__version__.__version__}_rev-{subprocess.check_output([f'git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
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
        self.checks(ldid_in_path, data_dir)

        # Prompt the user if they'd like to use an external IPA or a local IPA
        if not (self.args.url or self.args.path or self.args.folder):
            option = self.logger.ask("Would you like to use an external or a local IPA? [E, L] ").lower()
            print()

        with tempfile.TemporaryDirectory() as tmpfolder:
            # If the user's choice is external, download an IPA
            # Otherwise, copy the IPA to the temporary directory
            if self.args.url:
                if not self.args.url.endswith(".ipa"):
                    self.logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                    exit(1)

                try:
                    self.logger.log(f"Downloading file...", color=Colors.yellow)
                    res = requests.get(self.args.url, stream=True)
                    if res.status_code == 200:
                        with open(f"{tmpfolder}/app.ipa", "wb") as f:
                            f.write(res.content)
                        self.unzip(tmpfolder)
                    else:
                        self.logger.error(f"Provided URL is not reachable. Status code: {res.status_code}")
                        exit(1)
                except (NewConnectionError, ConnectionError, RequestException) as err:
                    self.logger.error(f"Provided URL is not reachable. Error: {err}")
                    exit(1)
            elif self.args.path:
                self.unpack(self.args.path, tmpfolder, dpkg_in_path)
            elif self.args.folder:
                for fpath in glob(f"{self.args.folder}/*.ipa"):
                    if Path(f"{tmpfolder}/app.ipa").exists():
                        Path(f"{tmpfolder}/app.ipa").unlink()
                    if Path(f"{tmpfolder}/app").exists():
                        rmtree(f"{tmpfolder}/app")
                    if Path(f"{tmpfolder}/deb").exists():
                        rmtree(f"{tmpfolder}/deb")

                    fname = PurePath(fpath).name
                    self.logger.log(f"Signing {fname}...", color=Colors.yellow)
                    print()

                    copy(fpath, f"{tmpfolder}/app.ipa")
                    self.unzip(tmpfolder)
                    out_dir = self.run(tmpfolder, ldid_in_path, dpkg_in_path, data_dir)
                    self.outputs.append(out_dir)
            elif option == "e":
                url = self.logger.ask("Paste in the *direct* path to an IPA online: ")

                if not url.endswith(".ipa"):
                    self.logger.error("URL provided is not an IPA, make sure to provide a direct link.")
                    exit(1)
                print()

                try:
                    res = requests.get(url, stream=True)
                    if res.status_code == 200:
                        self.logger.log(f"Downloading file...", color=Colors.yellow)

                        with open(f"{tmpfolder}/app.ipa", "wb") as f:
                            f.write(res.content)
                    else:
                        self.logger.error(f"URL provided is not reachable. Status code: {res.status_code}")
                        exit(1)
                except (NewConnectionError, ConnectionError, RequestException) as err:
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
                    path = self.logger.ask("Paste in the path to an IPA in your file system: ").strip('"').strip("'").strip()

                self.unpack(path, tmpfolder, dpkg_in_path)
            else:
                self.logger.error(f"That is not a valid option!")
                exit(1)

            is_installed = False
            if not self.args.folder:
                out_dir = self.run(tmpfolder, ldid_in_path, dpkg_in_path, data_dir)

                if self.args.install:
                    is_installed = self.install(out_dir)

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
                    final_outputs += f'{output}\n'
                self.logger.log(f"Output files:\n{final_outputs}", color=Colors.green)
            else:
                self.logger.log(f"Output file: {out_dir}", color=Colors.green)

    def checks(self, ldid_in_path, data_dir):
        # Check if codesign arg is added on Linux or iOS
        if self.args.codesign:
            if not self.utils.is_macos():
                self.logger.error(f"Codesign can only be used on macOS, remove the argument to use ldid instead.")
                exit(1)

        # Auto download ldid
        if not ldid_in_path and not self.args.nocheckldid:
            name = 'ldid'
            if self.utils.is_windows():
                name = 'ldid.exe'
            if Path(data_dir).joinpath(name).exists():
                ldid = Ldid(data_dir, name, self.args, self.utils, True)
            else:
                self.logger.log("ldid binary is not found, downloading latest binary.", color=Colors.yellow)
                ldid = Ldid(data_dir, name, self.args, self.utils, False)
            ldid.download()

    def install(self, out_dir):
        if not self.utils.is_ios():
            from .ps_installer import Installer

        if not self.utils.is_ios():
            installer = Installer(self.args, out_dir)
            is_installed = installer.install_deb()
        else:
            print("Checking if user is in sudoers")
            p = subprocess.run('sudo -nv'.split(),
                               capture_output=True)
            if p.returncode == 0 or 'password' in p.stderr.decode():
                print("User is in sudoers, using sudo command")
                self.logger.debug(f"Running command: sudo dpkg -i {out_dir}")

                subprocess.run(
                    ["sudo", "dpkg", "-i", f"{out_dir}"], capture_output=True)

                subprocess.run(
                    ['sudo', 'apt-get', 'install', '-f'], capture_output=True)

                is_installed = True
            else:
                print("User is not in sudoers, using su instead")
                self.logger.debug(f"Running command: su root -c 'dpkg -i {out_dir}")

                subprocess.run(
                    f"su root -c 'dpkg -i {out_dir}'".split(), capture_output=True)

                subprocess.run(
                    "su root -c 'apt-get install -f'".split(), capture_output=True)

                is_installed = True

        return is_installed

    def run(self, tmpfolder, ldid_in_path, dpkg_in_path, data_dir):
        # Read data from the plist
        app_dir = ''
        payload = Path(tmpfolder).joinpath('app').joinpath('Payload')
        if payload.exists():
            for fname in payload.rglob('*.app'):
                app_dir = fname
                break

            if app_dir == '':
                self.logger.error("Unable to find the application bundle")
                exit(1)
            print("Found app directory!")
        else:
            self.logger.error(f"IPA/deb is not valid!")
            exit(1)
        print()

        if Path(app_dir).joinpath('Info.plist').exists():
            self.logger.log(f"Reading plist...", color=Colors.yellow)
            with open(f'{app_dir}/Info.plist', 'rb') as f:
                info = plistlib.load(f)
                if self.args.name:
                    app_name = self.args.name
                else:
                    app_name = info["CFBundleName"]

                if self.args.bundleid:
                    app_bundle = self.args.bundleid
                else:
                    app_bundle = info["CFBundleIdentifier"]

                app_version = info["CFBundleShortVersionString"]

                if self.args.minver:
                    app_min_ios = self.args.minver
                else:
                    app_min_ios = info["MinimumOSVersion"]

                if self.args.author:
                    app_author = self.args.author
                else:
                    app_author = app_bundle.split(".")[1]

                app_executable = info["CFBundleExecutable"]
                print("Found information about the app!")
        else:
            self.logger.error("Unable to find Info.plist, can't read application data")
            exit(1)
        print()

        # Get the deb file ready
        self.logger.log(f"Preparing deb file...", color=Colors.yellow)
        print("Making directories...")
        Path(tmpfolder).joinpath('deb').joinpath('Applications').mkdir(exist_ok=False, parents=True)
        Path(tmpfolder).joinpath('deb').joinpath('DEBIAN').mkdir(exist_ok=False, parents=True)
        print("Copying deb file scripts and control...")
        copier = Copier(app_name, app_bundle, app_version, app_min_ios, app_author, self.in_package)
        prerm_path = PurePath(f'{tmpfolder}/deb/DEBIAN/prerm')
        postinsts_path = PurePath(f'{tmpfolder}/deb/DEBIAN/postinst')
        control_path = PurePath(f'{tmpfolder}/deb/DEBIAN/control')
        copier.copy_postinst(postinsts_path)
        copier.copy_control(control_path)
        copier.copy_prerm(prerm_path)
        print("Changing deb file scripts permissions...")
        self.utils.set_executable_permission(prerm_path)
        self.utils.set_executable_permission(postinsts_path)
        print("Copying app files...")
        full_app_path = PurePath(f"{tmpfolder}/deb/Applications/{app_dir.name}")
        copytree(app_dir, full_app_path)
        print("Changing app executable permissions...")
        self.utils.set_executable_permission(PurePath(f'{full_app_path}/{app_executable}'))
        print()

        # Sign the app
        self.logger.log(f"Signing app...", color=Colors.yellow)
        copier.copy_entitlements(f"{tmpfolder}/entitlements.plist")
        if self.in_package:
            cert_path = self.utils.get_resource_path(__name__, "data/certificate.p12")
        else:
            cert_path = PurePath(f'{Path.cwd()}/permasigner/data/certificate.p12')

        if self.args.codesign:
            print("Signing with codesign as it was specified...")
            subprocess.run(
                ['security', 'import', cert_path, '-P', 'password', '-A'], stdout=DEVNULL)

            subprocess.run(['codesign', '-s', 'We Do A Little Trolling iPhone OS Application Signing',
                            '--force', '--deep', '--preserve-metadata=entitlements', f'{full_app_path}'],
                           stdout=DEVNULL)
        else:
            print("Signing with ldid...")
            if ldid_in_path:
                ldid_cmd = 'ldid'
            else:
                ldid_cmd = PurePath(f'{data_dir}/ldid')

            self.logger.debug(
                f"Running command: {ldid_cmd} -S{PurePath(f'{tmpfolder}/entitlements.plist')} -M -K{cert_path} -Upassword '{full_app_path}'")

            subprocess.run([f'{ldid_cmd}', f'-S{tmpfolder}/entitlements.plist', '-M',
                            f'-K{cert_path}', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)

            if self.args.entitlements:
                self.logger.debug(f"Signing with extra entitlements located in {self.args.entitlements}")
                subprocess.run([f'{ldid_cmd}', f'-S{self.args.entitlements}', '-M',
                                f'-K{cert_path}', '-Upassword', f'{full_app_path}'], stdout=DEVNULL)
        print()

        # Package the deb file
        self.logger.log(f"Packaging the deb file...", color=Colors.yellow)
        if self.args.output:
            out_dir = self.args.output
            Path(out_dir).mkdir(exist_ok=True)
        elif self.in_package:
            Path(f"{data_dir}/output").mkdir(exist_ok=True)
            out_dir = PurePath(f"{data_dir}/output")
        else:
            Path("output").mkdir(exist_ok=True)
            out_dir = PurePath(f"{Path.cwd()}/output")

        if dpkg_in_path:
            out_path = PurePath(f"{out_dir}/{app_name.replace(' ', '') + f'_{app_version}' + '.deb'}")
            dpkg_cmd = f"dpkg-deb -Zxz --root-owner-group -b {tmpfolder}/deb {out_path}"
            self.logger.debug(f"Running command: {dpkg_cmd}")
            subprocess.run(dpkg_cmd.split(), stdout=DEVNULL)
            return out_path
        else:
            control = Control(app_bundle, app_version, app_min_ios, app_name, app_author, app_executable)
            deb = Deb(f"{tmpfolder}/deb/Applications/", out_dir, self.args)
            return deb.build(PurePath(f"{tmpfolder}/deb/DEBIAN/postinst"),
                             PurePath(f"{tmpfolder}/deb/DEBIAN/prerm"), control)


if __name__ == "__main__":
    main()
