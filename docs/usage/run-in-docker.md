---
description: Run Permasigner in the official Docker container.
---

**TLDR:** The Docker command is `docker run -it --rm -v "$PWD/output":/usr/src/permasigner/output -v "$PWD/ipas":/usr/src/permasigner/ipas -e DEBUG=1 docker.io/itsnebulalol/permasigner` while in the cloned permasigner directory. Make sure you pull first to get the latest updates.

* [Install Docker](https://docs.docker.com/get-docker/)
* Open a terminal
   * \[Windows] Hold Win + R and type `cmd`.
   * \[macOS] Terminal from the Utilities folder or spotlight.
   * \[Linux] Ctrl + Shift + T on most distros.
* Clone this repository with `git clone https://github.com/itsnebulalol/permasigner && cd permasigner`
   * \[Windows] If this fails, install git from [here](https://git-scm.com/download/win).
   * \[macOS] If this fails, install git with Xcode dev tools.
   * \[Linux] If this fails, install git with your package manager of choice; ex. `sudo apt install git`.
* Pull the container with `docker pull docker.io/itsnebulalol/permasigner`
* Launch the Docker container with `docker run -it --rm -v "$PWD/output":/usr/src/permasigner/output -v "$PWD/ipas":/usr/src/permasigner/ipas docker.io/itsnebulalol/permasigner`
   * You **must** be in the permasigner directory (`cd permasigner`) if not already.
* Send the deb file to your iDevice
   * Airdropping the file is probably the easiest, but you can use something like Dropbox or Mega. Advanced users can use openssh-sftp-server from Procursus.
* Reboot to stock, the app will still work!
