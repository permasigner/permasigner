---
description: Run Permasigner on Linux.
---

# Run on Linux

1. Open a terminal using Ctrl + Shift + T on most Linux distros
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with your package manager of choice; ex. `sudo apt install git`.
3. Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
   * If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.

{% hint style="info" %}
If you have extra entitlements, add them in `data/entitlements.xml`. If you don't know what this means, you can keep it as is.
{% endhint %}

4\. Run the script with `python main.py` or `python3 main.py`

* If you get an error that curl isn't found, install it with your package manager of choice; ex. `sudo apt install curl`.

5\. Install the newly created deb file on your iDevice

* You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.

6\. Reboot to stock, the app will still work!
