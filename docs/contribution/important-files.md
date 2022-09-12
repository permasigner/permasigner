---
description: >-
  Files and directories that will probably be useful to know what purpose they
  serve.
---

# Important Files

### The \`permasigner\` directory

The `permasigner` directory is where you're probably going to make changes.

* The `permasigner` module is called by `__main__.py`, and it's where Permasigner's main code is. This is where the script extracts, signs, and packages your apps.
* The `permasigner` module also uses other modules.
  * The `copy` module copies the app's metadata, such as entitlements.
  * The `dpkg` module packages the app into a deb, using dpkg-deb (if available), or constrictor.
  * The `installer` module is responsible for installing the app on your connected, jailbroken iDevice.
  * The `logger` module helps log progress data to console.
  * The `sign` module downloads ldid and uses it to sign the apps.
  * The `tcprelay` module opens a SSH connection of the connected iOS device. They are required for the `installer` module to function.
  * The `utils` module contains miscellaneous functions.
* The `bundled` directory contains other packages we modified.
* The `data` directory contains static files. Most of them are required by the `copier` module.
  * `certificate.p12` is the fake cert that your app is signed with. It was generated with OpenSSL3 from Procursus.
  * The `control` file houses the package's metadata, and is copied later by the `copier` module.
  * The `entitlements.plist` file is a list of entitlements that most apps will need, and is copied later by the `copier` module.
  * The `postinst` and `postrm` files runs uicache after installing/uninstalling. They are also copied later by the `copier` module.
* The `docker/entrypoint.sh` file is a script that handles environment variables for the production Docker container.
