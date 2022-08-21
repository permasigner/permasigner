---
description: Run Permasigner on a jailbroken iDevice using the Procursus bootstrap.
---

**Note:** A jailbreak using Procursus is required (eg. Taurine, odysseyra1n).

## Run from Package

* Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
* Install permasigner with `python3 -m pip install permasigner`
   * If this fails, install python3 with `sudo apt install python3` and install pip with `python3 -m ensurepip`.
* Run the script with `python3 -m permasigner`
* Install the newly created deb file
   * Find it in Filza at `/var/mobile/.permasigner/output`
* Reboot to stock, the app will still work!

## Run with Shortcut

* Import the shortcut from [here](https://routinehub.co/shortcut/12520/)
   * Make sure to pay attention to the import questions.
* Run the shortcut
   * It may seem like it's frozen in some parts, but it isn't.
* Choose one of the options and follow the prompts
* The app will install if you choose!
   * If you choose not to, it's in /var/mobile/.permasigner/src/output.

## Run from Source

* Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * If this fails, install git with `sudo apt install git`.
* Run the script with `python3 -m permasigner`
   * If this fails, install python3 with `sudo apt install python3` and pip with `python3 -m ensurepip`.

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.
{% endhint %}

* Install the newly created deb file
   * You can use something like Filza to find it, it's in /var/mobile/permasigner/output.
* Reboot to stock, the app will still work!
