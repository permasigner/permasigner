---
description: Run Permasigner on macOS.
---

# Run on macOS

1. Open Terminal from the Utilities folder or spotlight.
   * If you use a third-party terminal, it'll most likely work too.
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with Xcode dev tools on macOS.
3. Install dpkg using [brew](https://brew.sh) with `brew install dpkg`
4. Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
   * If this fails, install python3 using brew with `brew install python3`.
5. \[OPTIONAL] If you have extra entitlements, add them in `data/entitlements.xml`
   * If not sure, keep it how it is.
6. Run the script with `python main.py` or `python3 main.py`
7. Install the newly created deb file on your iDevice
   * Airdropping the file is probably the easiest.
8. Reboot to stock, the app will still work!
