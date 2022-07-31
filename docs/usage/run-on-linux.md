---
description: Run Permasigner on Linux.
---

## Run from Package

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Install all requirements with `pip install permasigner` or `pip3 install permasigner`
   * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.
* Run the script with `python -m permasigner` or `python3 -m permasigner`
* Install the newly created deb file on your iDevice
   * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!

## Run from Source

* Open a terminal using Ctrl + Shift + T on most Linux distros
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with your package manager of choice; ex. `sudo apt install git`.
* Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
   * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.

{% hint style="info" %}
If you have extra entitlements, add them in `data/entitlements.xml`. If you don't know what this means, you can keep it as is.
{% endhint %}

* Run the script with `python main.py` or `python3 main.py`
* Install the newly created deb file on your iDevice
    * You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
* Reboot to stock, the app will still work!
