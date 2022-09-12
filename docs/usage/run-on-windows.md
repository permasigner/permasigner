---
description: Run Permasigner on Windows natively, with WSL, or with Docker.
---

## Run from Package (Recommended)

* Open a Powershell window from the start menu
* Install the package with `python -m pip install -U permasigner`
    * If this fails, install the latest Python 3 version from [here](https://python.org).

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python -m permasigner`
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!

## Run from Source

* Open a Powershell window from the start menu
* Install permasigner with `pip install -U git+https://github.com/permasigner/permasigner`

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python -m permasigner`
    * If this fails, install the latest Python 3 version from [here](https://python.org).
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!
