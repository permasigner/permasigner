import plistlib
import shutil
import subprocess as sp
import sys
import platform
import os
import importlib
import pkg_resources
from argparse import Namespace
from importlib import resources
from pathlib import Path
from typing import Union

from . import logger


def is_ios() -> bool:
    """Determine if current OS is iOS """
    if not sys.platform == "darwin":
        return False

    return platform.machine().startswith("i")


def is_macos() -> bool:
    """Determine if current OS is macOS"""
    if platform.machine().startswith("i"):
        return False

    return sys.platform == "darwin"


def is_linux() -> bool:
    """Determine if current OS is Linux"""
    return sys.platform == "linux"


def is_windows() -> bool:
    """Determine if current OS is Windows"""
    return sys.platform == "win32"


def is_freebsd() -> bool:
    """ Determine if current OS is FreeBSD"""
    return "freebsd" in sys.platform


def make_executable(path: Path) -> None:
    """Set chmod +x on a given path"""
    file = Path(path)
    mode = file.stat().st_mode
    mode |= (mode & 0o444) >> 2
    file.chmod(mode)


def set_plugin_permissions(payload: Path, debug: bool) -> set:

    plugins = set()

    for folder in Path(payload / "PlugIns").glob("*.appex"):
        plist_path = folder / "Info.plist"
        if plist_path.exists():
            with open(plist_path, 'rb') as plist:
                info = plistlib.load(plist)
            executable = info["CFBundleExecutable"]
            logger.debug(f"Settings chmod +x on {folder / executable}", debug)
            make_executable(folder / executable)

            if is_windows():
                plugins.add(f"./{payload.parent.name}/{payload.name}/{folder.parent.name}/{folder.name}/{executable}")

    return plugins


def cmd_in_path(cmd: str) -> Union[None, str]:
    """Check if command is in PATH"""
    path = shutil.which(cmd)

    if path is None:
        return None

    # Check if ldid is from procursus
    if cmd == "ldid":
        if "procursus" in sp.getoutput(path):
            return path
        return None

    return path


def get_storage_dir() -> Path:
    """ Get path to data directory"""

    # Get the value of PERMASIGNER_HOME variable and if it's exported use it as data directory
    ps_home = os.environ.get("PERMASIGNER_HOME")
    if ps_home:
        return Path(ps_home)

    # Get path to user's $HOME
    home = Path.home()

    # Check if OS is Linux or FreeBSD
    # then, use $XDG_DATA_HOME as data directory
    # otherwise, default to $HOME/.local/share
    if is_linux() or is_freebsd():
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data).joinpath("permasigner")
        return home / ".local/share/permasigner"
    # Check if OS is iOS or macOS
    # then, use $HOME/Library/Application Support/permasigner as data directory
    elif is_ios() or is_macos():
        return home / ".permasigner"
    # Check if OS is Windows
    # then, use %APPDATA%/permasigner as data directory
    elif is_windows():
        return home / "AppData/Roaming/permasigner"


def find_application_bundle(tmp: Path) -> Union[Path, str]:
    # Check if Payload directory contains an application bundle
    # then, itterate over it's content
    # otherwise, exit with an error
    bundle = ''
    payload = tmp / "app/Payload"
    if payload.exists():
        for folder in payload.rglob("*.app"):
            bundle = folder
            break

        if bundle == '':
            logger.error("Did not find application bundle")
            exit(1)
    else:
        logger.error(f"IPA/deb is not valid!")
        exit(1)

    return bundle


def read_plist(path: Path, args: Namespace) -> dict:
    # Read bundle information from Info.plist
    with open(path, 'rb') as f:

        bundle = {}
        info = plistlib.load(f)

        if args.name:
            bundle["name"] = args.name
        else:
            bundle["name"] = info["CFBundleName"]

        if args.bundleid:
            bundle["id"] = args.bundleid
        else:
            bundle["id"] = info["CFBundleIdentifier"]

        bundle["version"] = info["CFBundleShortVersionString"]

        if args.minver:
            bundle["min_ios"] = args.minver
        else:
            bundle["min_ios"] = info["MinimumOSVersion"]

        if args.author:
            bundle["author"] = args.author
        else:
            bundle["author"] = bundle["id"].split(".")[1]

        bundle["executable"] = info["CFBundleExecutable"]

    return bundle


def get_certificate_path(in_package: bool) -> Path:
    # Check if running from a package
    # then, get path to certificate resource
    # otherwise, get path of a ceritificate in working dir
    if in_package:
        return get_resources_dir(__package__) / "certificate.p12"
    else:
        return Path.cwd() / "permasigner/data/certificate.p12"


def get_version() -> str:
    # Check if running from a git repository,
    # then, construct version in the following format: version-branch-hash
    if Path('.git').exists():
        return f"{sp.getoutput('git rev-parse --abbrev-ref HEAD')}_{sp.getoutput('git rev-parse --short HEAD')}"
    else:
        return pkg_resources.get_distribution(__package__).version


def get_output_directory(data_dir: Path, in_package: bool, output_arg: str) -> Path:
    # Check if output arg was specified
    # then, return it's value as a Path
    if output_arg:
        return Path(output_arg)
    # Check if running in a git repository
    # or a tarball then, return path in current dir
    elif not in_package or Path('.git').exists():
        return Path.cwd() / "output"
    # Check if running from a package
    # then, return path to output dir in data dir
    elif in_package:
        return data_dir / "output"


def get_resources_dir(package: str) -> Path:
    if sys.version_info < (3, 9):
        with importlib.resources.path(package, '__init__.py') as r:
            res = r.parent
    else:
        res = importlib.resources.files(package)

    return res / "data"
