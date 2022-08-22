import pkgutil
from urllib.parse import urlparse

WINDOWS_LINE_ENDING = b'\r\n'
UNIX_LINE_ENDING = b'\n'


class Copier:
    def __init__(self, app_name, app_bundle, app_version, app_min_ios, app_author, in_package):
        self.app_name = app_name
        self.app_bundle = app_bundle
        self.app_version = app_version
        self.app_min_ios = app_min_ios
        self.app_author = app_author
        self.in_package = in_package

    def copy_postinst(self, file_path):
        """Copy postinst file.

        Args:
            file_path (String): Path of the copy destination.
        """

        # Read the file
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/postinst")
        else:
            with open("permasigner/data/DEBIAN/postinst", 'rb') as file:
                filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.replace(' ', '').encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out again
        with open(file_path, 'wb') as file:
            for line in filedata.splitlines():
                file.write(line + b'\n')

    def copy_prerm(self, file_path):
        """Copy prerm file.

        Args:
            file_path (String): Path of the copy destination.
        """

        # Read the file
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/prerm")
        else:
            with open('permasigner/data/DEBIAN/prerm', 'rb') as file:
                filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.replace(' ', '').encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out again
        with open(file_path, 'wb') as file:
            file.write(filedata)

    def copy_control(self, file_path):
        """Copy control file.

        Args:
            file_path (String): Path of the copy destination.
        """

        # Read the file
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/DEBIAN/control")
        else:
            with open('permasigner/data/DEBIAN/control', 'rb') as file:
                filedata = file.read()

        # Replace the target strings
        filedata = filedata.replace(b"{APP_NAME}", self.app_name.encode())
        filedata = filedata.replace(b"{APP_NAME_ENCODED}", urlparse(self.app_name).path.encode())
        filedata = filedata.replace(b"{APP_BUNDLE}", self.app_bundle.encode())
        filedata = filedata.replace(b"{APP_VERSION}", self.app_version.encode())
        filedata = filedata.replace(b"{APP_MIN_IOS}", self.app_min_ios.encode())
        filedata = filedata.replace(b"{APP_AUTHOR}", self.app_author.encode())
        filedata = filedata.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        # Write the file out again
        with open(file_path, 'wb') as file:
            file.write(filedata)

    def copy_entitlements(self, file_path):
        """Copy entitlements file.

        Args:
            file_path (String): Path of the copy destination.
        """

        # Read the file
        if self.in_package:
            filedata = pkgutil.get_data(__name__, "data/entitlements.plist").decode('utf_8')
        else:
            with open('permasigner/data/entitlements.plist', 'r') as file:
                filedata = file.read()

        # Replace the target string
        if "science.xnu.undecimus" in self.app_bundle:
            filedata = filedata.replace("{APP_BUNDLE}", "8H69ZMY835.science.xnu.undecimus.8H69ZMY835")
            filedata = filedata.replace("{APP_KEYCHAIN_GROUPS}", "8H69ZMY835.*")
        else:
            filedata = filedata.replace("{APP_BUNDLE}", self.app_bundle)
            filedata = filedata.replace("{APP_KEYCHAIN_GROUPS}", self.app_bundle)

        # Write the file out again
        with open(file_path, 'w') as file:
            file.write(filedata)
