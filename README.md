<p align="center">
  <img src="https://static.itsnebula.net/permasigner-title.png" width="240" />
</p>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/made%20with-love-E760A4.svg" alt="Made with love">
  </a>
  <a href="https://github.com/itsnebulalol/permasigner/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/itsnebulalol/permasigner.svg" alt="License">
  </a>
  <a href="https://github.com/itsnebulalol/permasigner/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors/itsnebulalol/permasigner.svg" alt="Contributors">
  </a>
  <a href="https://github.com/itsnebulalol/permasigner/commits/main" target="_blank">
    <img src="https://img.shields.io/github/commit-activity/w/itsnebulalol/permasigner.svg" alt="Commits">
  </a>
  <a href="https://dsc.gg/permasigner" target="_blank">
    <img src="https://img.shields.io/discord/1001905994458206229?label=discord" alt="Discord">
  </a>
  <a href="https://github.com/itsnebulalol/permasigner/actions" target="_blank">
    <img src="https://img.shields.io/github/workflow/status/itsnebulalol/permasigner/Test%20script/main.svg" alt="Test status">
  </a>
</p>

<p align="center">
Permanently sign IPAs on jailbroken iDevices 14.0-14.8.1 (persists on stock)
</p>

---

# How does it work?

In iOS 14.0-14.8.1, there is a bug where CoreTrust will allow any root certificate. Although the bug exists on iOS 15.0-15.4.1, it can not be abused (yet) since you need to be jailbroken at first to place the app in the /Applications folder. This bug does not exist on anything older than iOS 14.

This script makes a deb file for you based on an IPA. Tested only with Taurine, but should work with many others.

Based on the [resign_taurine branch of CoreTrustDemo](https://github.com/zhuowei/CoreTrustDemo/tree/resign_taurine), please note that certificates are not copyrightable.

# Prerequsites

1. A computer or jailbroken iDevice with Procursus
    - Mac OS X 10.5.0 (?) or later required.
    - (Basically) any Linux distro is supported.
    - A jailbroken iDevice using the Procursus bootstrap is supported.
2. Jailbroken "target" iDevice on 14.0-14.8.1
    - The device needs to be jailbroken at first to place the app in the /Applications folder. After installing it'll continue working on stock.

# Tutorials

-   [Run Online](https://permasigner.itsnebula.net/usage/run-online)
-   [Run in Docker](https://permasigner.itsnebula.net/usage/run-in-docker)
-   [Run on iOS](https://permasigner.itsnebula.net/usage/run-on-ios)
-   [Run on macOS](https://permasigner.itsnebula.net/usage/run-on-macos)
-   [Run on Linux](https://permasigner.itsnebula.net/usage/run-on-linux)
-   [Run on FreeBSD](https://permasigner.itsnebula.net/usage/run-on-linux)
-   [Run on Windows](https://permasigner.itsnebula.net/usage/run-on-windows)

# In Progress

View the [GitHub Projects board](https://github.com/users/itsnebulalol/projects/2/views/1)!

# Credits

-   [Linus Henze](https://github.com/LinusHenze) for the bug
-   [zhuowei](https://github.com/zhuowei) for the original Taurine script
-   [RexSonic](https://github.com/RexSonic) for the fix and a lot of help
-   [superrnovae](https://github.com/superrnovae) for contributing lots of fixes and features
-   [verygenericname](https://github.com/verygenericname) for the ldid downloader and support
-   the [Procursus Team](https://github.com/ProcursusTeam) for the amazing bootstrap and the ldid fork

Plus, big thanks to all of the contributors that made this project possible.

<a href="https://github.com/itsnebulalol/permasigner/graphs/contributors"><img src="https://contributors-img.web.app/image?repo=itsnebulalol/permasigner" /></a>

# Other Stuff

-   [Reddit Post](https://www.reddit.com/r/jailbreak/comments/vqnazh/free_release_permasigner_generate_a_permasigned)
