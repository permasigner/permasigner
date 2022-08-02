---
description: >-
  Files and directories that will probably be useful to know what purpose they
  serve.
---

# Important Files

### The \`permasigner\` directory

The `permasigner` directory is where you're probably going to make changes.

* `__main__.py` is where Permasigner's main code is. This is where the script extracts, signs, and packages your apps.
* The main file also uses other modules which are prefixed with `ps_`.
  * The `copier` module copies the app's metadata, such as entitlements.
  * The `downloader` module downloads ldid and dpkg-deb (on Linux).
  * The `hash` module checks the hash of the local ldid and dpkg-deb against the remote versions to make sure they are always up to date.
  * The `installer` module is responsible for installing the app on your connected, jailbroken iDevice.
  * The `logger` module helps log progress data to console.
  * The `tcprelay` and `usbmux` modules open an SSH connection of the connected iOS device. They are required for the `installer` module to function.
  * The `utils` module contains miscellaneous functions.
* The `data` directory contains static files. Most of them are required by the `copier` module.
  * `certificate.p12` is the fake cert that your app is signed with. It was generated with OpenSSL3 from Procursus.
  * The `control` file houses the package's metadata, and is copied later by the `copier` module.
  * The `docker-entrypoint.sh` file is a script that handles environment variables for the production Docker container.
  * The `entitlements.plist` file is a list of entitlements that most apps will need, and is copied later by the `copier` module.
  * The `postinst` and `postrm` files runs uicache after installing/uninstalling. They are also copied later by the `copier` module.
