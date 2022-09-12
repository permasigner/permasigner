---
description: Run Permasigner on Debian based Linux distros.
---

## Run from Package

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Install bzip2 and binutils using your package manager of choice; ex. `sudo apt install bzip2 binutils`
* Install the package with `pip install -U permasigner` or `pip3 install -U permasigner`
    * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python -m permasigner` or `python3 -m permasigner`
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!

## Run from Source

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Install bzip2 and binutils using your package manager of choice; ex. `sudo apt install bzip2 binutils`
* Install permasigner with `pip install -U git+https://github.com/permasigner/permasigner`

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python -m permasigner` or `python3 -m permasigner`
    * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!
