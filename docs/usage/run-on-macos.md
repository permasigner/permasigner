---
description: Run Permasigner on macOS.
---

## Run from Package

* Open Terminal from the Utilities folder or spotlight.
   * If you use a third-party terminal, it'll most likely work too.
* Install dpkg using [brew](https://brew.sh) with `brew install dpkg`
* Install all requirements with `pip install -U permasigner` or `pip3 install -U permasigner`
    * If this fails, install python3 using brew with `brew install python3`.

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python -m permasigner` or `python3 -m permasigner`
* Install the newly created deb file on your iDevice
    * Airdropping the file is probably the easiest.
* Reboot to stock, the app will still work!

## Run from Source

* Open Terminal from the Utilities folder or spotlight.
    * If you use a third-party terminal, it'll most likely work too.
* Install permasigner with `pip install -U git+https://github.com/permasigner/permasigner`
* Install dpkg using [brew](https://brew.sh) with `brew install dpkg`

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb on your connected device file automagically :)
{% endhint %}

* Run the script with `python main.py` or `python3 main.py`
* Install the newly created deb file on your iDevice
    * Airdropping the file is probably the easiest.
* Reboot to stock, the app will still work!
