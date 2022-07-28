---
description: Run Permasigner on a jailbroken iDevice using the Procursus bootstrap.
---

# Run on iOS

**Note:** A jailbreak using Procursus is required (eg. Taurine, odysseyra1n).

## Shortcut

1. Import the shortcut from [here](https://routinehub.co/shortcut/12520/)
   * Make sure to pay attention to the import questions.
2. Run the shortcut
   * It may seem like it's frozen in some parts, but it isn't.
3. Choose one of the options and follow the prompts
4. The app will install if you choose!
   * If you choose not to, it's in /var/mobile/.permasigner/src/output.

## Manual

1. Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with `sudo apt install git`.
3. Install all requirements with `python3 -m pip install -r ios_requirements.txt`
   * If this fails, install python3 with `sudo apt install python3`.
4. \[OPTIONAL] If you have extra entitlements, add them in `data/entitlements.plist`
   * If not sure, keep it how it is.
5. Run the script with `python3 main.py`
   * If you get an error that curl isn't found, install it with `sudo apt install curl`.
6. Install the newly created deb file
   * You can use something like Filza to find it, it's in /var/mobile/permasigner/output.
7. Reboot to stock, the app will still work!
