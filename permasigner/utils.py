import plistlib
import shutil
import subprocess
import sys
import platform
import os
import importlib
from importlib import util
from pathlib import PurePath, Path
from typing import Union

from .__version__ import __version__


def is_ios() -> bool:
    """ Determine if current OS is iOS """
    if not sys.platform == "darwin":
        return False

    return platform.machine().startswith("i")


def is_macos() -> bool:
    """ Determine if current OS is macOS"""
    if platform.machine().startswith("i"):
        return False

    return sys.platform == "darwin"


def is_linux() -> bool:
    """ Determine if current OS is Linux"""
    return sys.platform == "linux"


def is_windows() -> bool:
    """ Determine if current OS is Windows"""
    return sys.platform == "win32"


def is_freebsd() -> bool:
    """ Determine if current OS is FreeBSD"""
    return "freebsd" in sys.platform


def make_executable(path: Path) -> None:
    """Set chmod 755 on a given path"""
    Path(path).chmod(0o755)


def cmd_in_path(cmd: str) -> Union[bool, str]:
    # Check if command is in PATH
    path = shutil.which(cmd)

    # If command was not found in Path return False
    if path is None:
        return False

    # Check if ldid is from procursus
    if cmd == "ldid":
        if "procursus" in subprocess.getoutput(path):
            return path
        return False

    # Return True if command was found in PATH
    return path


def get_data_directory() -> Path:
    """ Get path to data directory"""

    # Get the value of PERMASIGNER_HOME variable and if it's exported use it as data directory
    ps_home = os.environ.get("PERMASIGNER_HOME")
    if ps_home:
        return ps_home

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
            exit("Did not find application bundle")
    else:
        exit(f"IPA/deb is not valid!")

    return bundle


def read_plist(path, args) -> dict:
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
        return resource_path(__name__, "data/certificate.p12")
    else:
        return Path.cwd() / "permasigner/data/certificate.p12"


def get_version(in_package: bool) -> str:
    version = __version__
    # Check if running module as a script
    # then, return version from __version__
    if in_package:
        return version
    # Check if running from a git repository,
    # then, construct version in the following format: version-branch-hash
    if Path('.git').resolve().exists():
        git = cmd_in_path("git")
        if git:
            version = f"{version}_{subprocess.check_output([f'{git}', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()}_{subprocess.check_output([f'{git}', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()}"
    else:
        # Check if running from a Docker container
        # then, get version from pre-exported environment variable
        if os.environ.get('IS_DOCKER_CONTAINER'):
            version = os.environ.get('VERSION', False)

    return version


def get_output_directory(data_dir, in_package, output_arg: str) -> Path:
    # Check if output arg was specified
    # then, return it's value
    if output_arg:
        return output_arg
    # Check if running from a package
    # then, create output dir in data dir
    # if it doesn't exist yet
    elif in_package:
        return data_dir / "output"
    # Create output dir in current working directory
    # if it doesn't exist yet
    else:
        return Path.cwd() / "output"


def resource_path(package: str, resource: str):
    # Get path to resource in the package
    spec = importlib.util.find_spec(package)
    if spec is None:
        return None
    loader = spec.loader
    if loader is None or not hasattr(loader, 'get_data'):
        return None
    mod = (sys.modules.get(package) or
           importlib._bootstrap._load(spec))
    if mod is None or not hasattr(mod, '__file__'):
        return None

    parts = resource.split('/')
    parts.insert(0, PurePath(mod.__file__).parent)
    return PurePath(*parts)
