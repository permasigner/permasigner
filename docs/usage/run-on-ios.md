---
description: Run Permasigner on a jailbroken iDevice.
---

{% hint style="info" %}
If asked, the default root password is `alpine`.
{% endhint %}

## Run from Package

* Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
* Install permasigner with `python3 -m pip install -U permasigner`
    * If this fails, install python3 with `su root -c apt install python3` and install pip with `python3 -m ensurepip`.

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb file automagically :)
{% endhint %}

* Run the script with `python3 -m permasigner`
* Install the newly created deb file
    * Find it in Filza at `/var/mobile/.permasigner/output`
* Reboot to stock, the app will still work!

## Run with Shortcut

{% hint style="warning" %}
This will only work on Procursus jailbreaks for now.
{% endhint %}

* Import the shortcut from [here](https://routinehub.co/shortcut/12520/)
    * Make sure to pay attention to the import questions.
* Run the shortcut
    * It may seem like it's frozen in some parts, but it isn't.
* Choose one of the options and follow the prompts
* The app will install if you choose!
    * If you choose not to, it's in /var/mobile/.permasigner/src/output.

## Run from Source

* Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
* Install permasigner with `pip install -U git+https://github.com/permasigner/permasigner`

{% hint style="info" %}
If you have extra entitlements, append the `-e` flag when running the script. If you don't know what this means, you can ignore this.

When running the script, you will notice the a `one of the arguments is required` error. You'll need to append the IPA to sign as an argument, like `-u https://example.com/app.ipa`, or `-p /Users/nebula/Downloads/app.ipa`, for example.

You may also pass the `-i` argument to install the created deb file automagically :)
{% endhint %}

* Run the script with `python3 -m permasigner`
    * If this fails, install python3 with `su root -c apt install python3` and pip with `python3 -m ensurepip`.
* Install the newly created deb file
    * You can use something like Filza to find it, it's in /var/mobile/permasigner/output.
* Reboot to stock, the app will still work!
