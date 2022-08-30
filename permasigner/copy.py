import pkgutil
from pathlib import Path
from urllib.parse import urlparse

WINDOWS_LINE_ENDING = b'\r\n'
UNIX_LINE_ENDING = b'\n'


class Copier:
    def __init__(self, bundle: dict, in_package: bool) -> None:
        self.app_name = bundle["name"]
        self.app_version = bundle["version"]
        self.app_min_ios = bundle["min_ios"]
        self.app_author = bundle["author"]
        self.bundle_id = bundle["id"]
        self.in_package = in_package

    def copy_postinst(self, filepath: Path) -> None:
        # Read postinst script's content
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/postinst")
        else:
            with open("permasigner/data/DEBIAN/postinst", 'rb') as file:
                filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.replace(' ', '').encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out to tmp dir
        with open(filepath, 'wb') as file:
            for line in filedata.splitlines():
                file.write(line + b'\n')

    def copy_prerm(self, filepath: Path) -> None:
        # Read prerm script's content
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/prerm")
        else:
            with open('permasigner/data/DEBIAN/prerm', 'rb') as file:
                filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.replace(' ', '').encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out to tmp dir
        with open(filepath, 'wb') as file:
            file.write(filedata)

    def copy_control(self, file_path: Path) -> None:
        # Read control fine content
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/control")
        else:
            with open('permasigner/data/DEBIAN/control', 'rb') as file:
                filedata = file.read()

        # Replace target strings
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.encode())
        filedata = filedata.replace(b"{APP_NAME_ENCODED}", urlparse(self.app_name).path.encode())
        filedata = filedata.replace(b"{APP_BUNDLE}", self.bundle_id.encode())
        filedata = filedata.replace(b"{APP_VERSION}", self.app_version.encode())
        filedata = filedata.replace(b"{APP_MIN_IOS}", self.app_min_ios.encode())
        filedata = filedata.replace(b"{APP_AUTHOR}", self.app_author.encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out to tmp dir
        with open(file_path, 'wb') as file:
            file.write(filedata)

    def copy_entitlements(self, file_path: Path) -> None:
        # Check if running from a package
        # then, read the content of the
        # entitlements file using pkgutil's get_data method
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/entitlements.plist").decode('utf_8')
        # Otherwise, read from a subdirectory in working dir
        else:
            with open('permasigner/data/entitlements.plist', 'r') as file:
                filedata = file.read()

        # Replace target strings in filedata read from entitlements
        if "science.xnu.undecimus" in self.bundle_id:
            filedata = filedata.replace("{APP_BUNDLE}", "8H69ZMY835.science.xnu.undecimus.8H69ZMY835")
            filedata = filedata.replace("{APP_KEYCHAIN_GROUPS}", "8H69ZMY835.*")
        else:
            filedata = filedata.replace("{APP_BUNDLE}", self.bundle_id)
            filedata = filedata.replace("{APP_KEYCHAIN_GROUPS}", self.bundle_id)

        # Write the filedata out to a new file
        with open(file_path, 'w') as file:
            file.write(filedata)
