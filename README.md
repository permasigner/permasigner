<h1 align="center">Permasigner</h1>
<p align="center">🖊 Permanently signs IPAs on jailbroken iDevices 14.0-14.8.1 (persists on stock).</p>

# How does it work?
In 14.0-15.4.1, there is a bug where CoreTrust will allow any root certificate. 

This script makes a deb file for you based on an IPA. Tested with Taurine and Odyssey, but should work with many others.

This is especially useful for 14.0-14.2.1 users who don't have a permanently signed jailbreak (eg. unc0ver + Fugu14).

# Prerequsites
1. Mac OS X 10.5.0 (?) or later, personally tested on macOS 13.0
    - Both codesign and ldid can be used. If you prefer ldid, download a binary from [here](https://github.com/ProcursusTeam/ldid/actions) and place it in the directory where the script is. A GitHub account is required.
    - Linux support may be possible, if someone edits the script and tries it with ldid, please tell me!
2. Jailbroken iDevice on 14.0-14.8.1

# How to use
1. Clone this repository: `git clone https://github.com/itsnebulalol/permasigner`
2. Install all requirements: `pip install -r requirements.txt`
3. Edit the app's entitlements in `app.entitlements`
    - If not sure, keep it how it is, it may work.
    - Some apps like Dolphin have custom entitlements to use.
4. Install dpkg using brew
5. Run the script
6. Install the newly created deb file
7. Reboot to stock, the app will still work!
8. ??
9. Profit?

# In Progress
- [ ] Ask to install automatically on connected device
    - Would require using something like iProxy
- [x] Switch to ldid for possible Linux support
    - Maybe Procursus strapped iDevices too, if necessary pip packages are compiled for iPhoneOS

# Credits
- [Linus Henze](https://github.com/LinusHenze) for the bug
- [zhuowei](https://github.com/zhuowei) for the original Taurine script
- [RexSonic](https://github.com/RexSonic) for the fix

# Other Stuff
[Reddit Post](https://www.reddit.com/r/jailbreak/comments/vqnazh/free_release_permasigner_generate_a_permasigned)