---
description: Run Permasigner on macOS.
---

## Run from Package

* Open Terminal from the Utilities folder or spotlight.
   * If you use a third-party terminal, it'll most likely work too.
* Install dpkg using [brew](https://brew.sh) with `brew install dpkg`
* Install all requirements with `pip install permasigner` or `pip3 install permasigner`
   * If this fails, install python3 using brew with `brew install python3`.
* Run the script with `python -m permasigner` or `python3 -m permasigner`
* Install the newly created deb file on your iDevice
   * Airdropping the file is probably the easiest.
* Reboot to stock, the app will still work!

## Run from Source

* Open Terminal from the Utilities folder or spotlight.
   * If you use a third-party terminal, it'll most likely work too.
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with Xcode dev tools on macOS.
* Install dpkg using [brew](https://brew.sh) with `brew install dpkg`
* Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
   * If this fails, install python3 using brew with `brew install python3`.

{% hint style="info" %}
If you have extra entitlements, add them in `data/entitlements.xml`. If you don't know what this means, you can keep it as is.
{% endhint %}

* Run the script with `python main.py` or `python3 main.py`
* Install the newly created deb file on your iDevice
   * Airdropping the file is probably the easiest.
* Reboot to stock, the app will still work!
