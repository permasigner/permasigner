---
description: Run Permasigner on Windows using WSL or Docker.
---

## Run from Package (Recommended)

* Open a Powershell window from the start menu
* Install the package with `python -m pip install permasigner`
    * If this fails, install the latest Python 3 version from [here](https://python.org).
* Run the script with `python -m permasigner`
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!

## Run from Source

* Open a Powershell window from the start menu
* Clone this repository with `git clone https://github.com/permasigner/permasigner && cd permasigner`
    * If this fails, install git for Windows from [here](https://git-scm.com/download/win).

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.
{% endhint %}

* Run the script with `python -m permasigner`
    * If this fails, install the latest Python 3 version from [here](https://python.org).
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!
