---
description: Run Permasigner on Debian based Linux distros.
---

## Run from Package

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Install bzip2 and binutils using your package manager of choice; ex. `sudo apt install bzip2 binutils`
* Install the package with `pip install permasigner` or `pip3 install permasigner`
   * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.
* Run the script with `python -m permasigner` or `python3 -m permasigner`
* Install the newly created deb file on your iDevice
   * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!

## Run from Source

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Install bzip2 and binutils using your package manager of choice; ex. `sudo apt install bzip2 binutils`
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with your package manager of choice; ex. `sudo apt install git`.
* Run the script with `python -m permasigner` or `python3 -m permasigner`
   * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.
{% endhint %}

* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!
