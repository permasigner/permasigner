# Permasigner
🖊 Permanently signs IPAs on jailbroken iDevices (persists on stock).

# NOTE: Currently broken, apps won't launch

# How does it work?
In 14.0-15.4.1, there is a bug where CoreTrust will allow any root certificate. 

# How to use
1. Clone this repository: `git clone https://github.com/itsnebulalol/permasigner --depth=1`
2. Edit the app's entitlements in `app.entitlements`
3. Install dpkg using brew
4. Run the script
5. Install the newly created deb file
6. Reboot to stock, the app will still work!
7. ??
8. Profit?

# Credits
- [Linus Henze](https://github.com/LinusHenze) for the bug
- [zhuowei](https://github.com/zhuowei) for the original Taurine script (included as a submodule for the certs)
