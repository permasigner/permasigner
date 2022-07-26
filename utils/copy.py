class Copy:
    def copy_postinst(file_path, app_name):
        """Copy postinst file.

        Args:
            file_path (String): Path of the copy destination.
            app_name (String): Name of the app being processed.
        """

        # Read the file
        with open("data/postinst", 'r') as file:
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
        with open('data/postrm', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("{APP_NAME}", app_name)

        # Write the file out again
        with open(file_path, 'w') as file:
            file.write(filedata)

    def copy_control(
            file_path,
            app_name,
            app_bundle,
            app_version,
            app_min_ios,
            app_author):
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
        with open('data/control', 'r') as file:
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

    def copy_entitlements(file_path, app_bundle):
        """Copy entitlements file.

        Args:
            file_path (String): Path of the copy destination.
            app_bundle (String): Bundle ID of the app being processed.
        """

        # Read the file
        with open('data/entitlements.plist', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("{APP_BUNDLE}", app_bundle)

        # Write the file out again
        with open(file_path, 'w') as file:
            file.write(filedata)
