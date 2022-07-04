<h1 align="center">Permasigner</h1>
<p align="center">🖊 Permanently signs IPAs on jailbroken iDevices 14.0-14.8.1 (persists on stock).</p>

# How does it work?
In iOS 14.0-14.8.1, there is a bug where CoreTrust will allow any root certificate. 
    - Although the bug exists on iOS 15.0-15.4.1, it can not be abused since you need to be jailbroken at first to place the app in the /Applications folder. 
    - This bug does not exist on anything older than iOS 14.

This script makes a deb file for you based on an IPA. Tested only with Taurine, but should work with many others.

**Note:** unc0ver will probably fail to jailbreak. It works for some people but not everyone.

# Prerequsites
1. Mac OS X 10.5.0 (?) or later, or Linux
    - Both codesign and ldid can be used on macOS.
2. Jailbroken iDevice on 14.0-14.8.1
    - The device needs to be jailbroken at first to place the app in the /Applications folder. After installing it'll continue working on stock.
3. Python 3 installed on the PC
    - This can be installed with brew on macOS (`brew install python3`), and your favorite package manager on Linux (`sudo apt install python3`).

# How to use
1. Open a terminal
    - Terminal in the Utilities folder/spotlight on macOS if not sure.
    - Ctrl + Shift + T to open up a terminal on most Linux distros.
2. Clone this repository: `git clone https://github.com/itsnebulalol/permasigner`
    - If this fails, install git with Xcode dev tools on macOS; install it with your favorite package manager on Linux (`sudo apt install git`).
3. Install all requirements: `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
4. [OPTIONAL] If you have extra entitlements, add them in `app.entitlements`
    - If not sure, keep it how it is.
5. Run the script: `python main.py` or `python3 main.py`
    - [macOS only] If you'd like the script to use codesign instead, pass `-c` or `--codesign`.
    - [Linux only] If you get an error that curl isn't found, install it using your favorite package manager. Ex. `sudo apt install curl`.
6. Install the newly created deb file
    - macOS users, airdropping the file is probably the easiest.
    - Linux users can use something like Dropbox or Mega; Advanced users can use `openssh-sftp-server` from Procursus.
7. Reboot to stock, the app will still work!

# In Progress
- [x] Pull entitlements from binary
    - Only works on signed binaries...
    - EDIT: Merging entitlements instead... seems like a better idea
- [x] Download dpkg-deb like how we did with ldid so it works with other Linux distros
- [ ] Ask to install automatically on connected device
    - Would require using something like iProxy
- [x] Switch to ldid for possible Linux support
    - Maybe Procursus strapped iDevices too, if necessary pip packages are compiled for iPhoneOS

# Credits
- [Linus Henze](https://github.com/LinusHenze) for the bug
- [zhuowei](https://github.com/zhuowei) for the original Taurine script
- [RexSonic](https://github.com/RexSonic) for the fix and a lot of help
- [verygenericname](https://github.com/verygenericname) for the ldid downloader
+ anyone who sent a pull request or issue! Your contribution helps a lot!

# Other Stuff
- [Reddit Post](https://www.reddit.com/r/jailbreak/comments/vqnazh/free_release_permasigner_generate_a_permasigned)
