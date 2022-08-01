---
description: Run Permasigner on a jailbroken iDevice using the Procursus bootstrap.
---

**Note:** A jailbreak using Procursus is required (eg. Taurine, odysseyra1n).

## Shortcut

* Import the shortcut from [here](https://routinehub.co/shortcut/12520/)
   * Make sure to pay attention to the import questions.
* Run the shortcut
   * It may seem like it's frozen in some parts, but it isn't.
* Choose one of the options and follow the prompts
* The app will install if you choose!
   * If you choose not to, it's in /var/mobile/.permasigner/src/output.

## Manual

* Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with `sudo apt install git`.
* Install all requirements with `python3 -m pip install -r ios_requirements.txt`
   * If this fails, install python3 with `sudo apt install python3`.

{% hint style="info" %}
If you have extra entitlements, add them in `data/entitlements.xml`. If you don't know what this means, you can keep it as is.
{% endhint %}

* Run the script with `python3 main.py`
   * If you get an error that curl isn't found, install it with `sudo apt install curl`.
* Install the newly created deb file
   * You can use something like Filza to find it, it's in /var/mobile/permasigner/output.
* Reboot to stock, the app will still work!
