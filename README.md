<h1 align="center">Permasigner</h1>
<p align="center">🖊 Permanently signs IPAs on jailbroken iDevices 14.0-14.8.1 (persists on stock).</p>

# How does it work?
In iOS 14.0-14.8.1, there is a bug where CoreTrust will allow any root certificate. Although the bug exists on iOS 15.0-15.4.1, it can not be abused (yet) since you need to be jailbroken at first to place the app in the /Applications folder. This bug does not exist on anything older than iOS 14.

This script makes a deb file for you based on an IPA. Tested only with Taurine, but should work with many others.

Based on the [resign_taurine branch of CoreTrustDemo](https://github.com/zhuowei/CoreTrustDemo/tree/resign_taurine), please note that certificates are not copyrightable.

**Note:** unc0ver will probably fail to jailbreak. It works for some people but not everyone.

# Prerequsites
1. A computer or jailbroken iDevice with Procursus
    - Mac OS X 10.5.0 (?) or later required.
    - (Basically) any Linux distro is supported.
    - A jailbroken iDevice using the Procursus bootstrap is supported.
2. Jailbroken "target" iDevice on 14.0-14.8.1
    - The device needs to be jailbroken at first to place the app in the /Applications folder. After installing it'll continue working on stock.

# Run on `iOS` (Procursus jailbreaks required)
## Shortcut
1. Import the shortcut from [here](https://routinehub.co/shortcut/12520/)
    - Make sure to pay attention to the import questions.
2. Run the shortcut
    - It may seem like it's frozen in some parts, but it isn't.
3. Choose one of the options and follow the prompts
4. The app will install if you choose!
    - If you choose not to, it's in /var/mobile/.permasigner/src/output.

## Manual
1. Install NewTerm 2 from [Chariz](https://repo.chariz.com) using your favorite package manager
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
    - If this fails, install git with `sudo apt install git`.
3. Install all requirements with `pip3 install -r requirements.txt`
    - If this fails, install python3 with `sudo apt install python3`.
4. [OPTIONAL] If you have extra entitlements, add them in `app.entitlements`
    - If not sure, keep it how it is.
5. Run the script with `python3 main.py`
    - If you get an error that curl isn't found, install it with `sudo apt install curl`.
6. Install the newly created deb file 
    - You can use something like Filza to find it, it's in /var/mobile/permasigner/output.
7. Reboot to stock, the app will still work!

# Run on `macOS`
1. Open Terminal from the Utilities folder or spotlight.
    - If you use a third-party terminal, it'll most likely work too.
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
    - If this fails, install git with Xcode dev tools on macOS.
3. Install dpkg using [brew](https://brew.sh) with `brew install dpkg`
4. Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
    - If this fails, install python3 using brew with `brew install python3`.
5. [OPTIONAL] If you have extra entitlements, add them in `app.entitlements`
    - If not sure, keep it how it is.
6. Run the script with `python main.py` or `python3 main.py`
    - If you'd like the script to use codesign instead of ldid, pass `-c` or `--codesign`.
7. Install the newly created deb file on your iDevice
    - Airdropping the file is probably the easiest.
8. Reboot to stock, the app will still work!

# Run on `Linux`
1. Open a terminal using Ctrl + Shift + T on most Linux distros
2. Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
    - If this fails, install git with your package manager of choice; ex. `sudo apt install git`.
3. Install all requirements with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
    - If this fails, install python3 with your package manager of choice; ex. `sudo apt install python3`.
4. [OPTIONAL] If you have extra entitlements, add them in `app.entitlements`
    - If not sure, keep it how it is.
5. Run the script with `python main.py` or `python3 main.py`
    - If you get an error that curl isn't found, install it with your package manager of choice; ex. `sudo apt install curl`.
6. Install the newly created deb file on your iDevice
    - You can use something like Dropbox or Mega; advanced users can use `openssh-sftp-server` from Procursus.
7. Reboot to stock, the app will still work!

# In Progress
View the [GitHub Projects board](https://github.com/users/itsnebulalol/projects/2/views/1)!

# Credits
- [Linus Henze](https://github.com/LinusHenze) for the bug
- [zhuowei](https://github.com/zhuowei) for the original Taurine script
- [RexSonic](https://github.com/RexSonic) for the fix and a lot of help
- [verygenericname](https://github.com/verygenericname) for the ldid downloader

+ anyone who sent a pull request or issue! Your contribution helps a lot!

# Other Stuff
- [Reddit Post](https://www.reddit.com/r/jailbreak/comments/vqnazh/free_release_permasigner_generate_a_permasigned)
