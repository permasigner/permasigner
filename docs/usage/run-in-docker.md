---
description: Run Permasigner in the official Docker container.
---

**TLDR:** The Docker commands are:
* Pull the container with `docker pull ghcr.io/permasigner/permasigner`
* To permasign:
	*  \[Windows] `docker run -it --rm -v ${pwd}/output:/permasigner/output -v ${pwd}/ipas:/permasigner/ipas permasigner/permasigner`
	*  \[Linux/macOS] `docker run -it --rm -v "$PWD/output":/permasigner/output -v "$PWD/ipas":/permasigner/ipas -e DEBUG=1 permasigner/permasigner`
* To permasign and install produced deb to your device (must be connected):
	*  \[Windows] `docker run -it --rm -v ${pwd}/output:/permasigner/output -v ${pwd}/ipas:/permasigner/ipas -e DEBUG=1 -e WINDOWS=1 -e INSTALL=1 permasigner/permasigner`
	*  \[Linux/macOS] `docker run -it --privileged --rm -p 2222:2222 -v /var/run/usbmuxd:/var/run/usbmuxd -v "$PWD/output":/permasigner/output -v "$PWD/ipas":/permasigner/ipas -e DEBUG=1 -e INSTALL=1 permasigner/permasigner`

  ---

* [Install Docker](https://docs.docker.com/get-docker/)
* Open a terminal
	*  \[Windows] Hold Win + R and type `powershell`.
	*  \[macOS] Terminal from the Utilities folder or spotlight.
	*  \[Linux] Ctrl + Shift + T on most distros.
* Pull the container with `docker pull ghcr.io/permasigner/permasigner`
* Create `output` and `ipas` directories.
* Launch the Docker container with:
	* To permasign:
		*  \[Windows] `docker run -it --rm -v ${pwd}/output:/permasigner/output -v ${pwd}/ipas:/permasigner/ipas permasigner/permasigner`.
		*  \[Linux/macOS] `docker run -it --rm -v "$PWD/output":/permasigner/output -v "$PWD/ipas":/permasigner/ipas permasigner/permasigner`
	* To permasign and install produced deb to your device (must be connected):
		*  \[Windows] `docker run -it --rm -v ${pwd}/output:/permasigner/output -v ${pwd}/ipas:/permasigner/ipas -e DEBUG=1 -e WINDOWS=1 -e INSTALL=1 permasigner/permasigner`
		*  \[Linux/macOS] `docker run -it --privileged --rm -p 2222:2222 -v /var/run/usbmuxd:/var/run/usbmuxd -v "$PWD/output":/permasigner/output -v "$PWD/ipas":/permasigner/ipas -e DEBUG=1 -e INSTALL=1 permasigner/permasigner`
* Send the deb file to your iDevice
    * The script can do that for you, you will be asked to input the user password for ssh access.
    * Airdropping the file is probably the easiest, but you can use something like Dropbox or Mega. Advanced users can use openssh-sftp-server from Procursus.
* Reboot to stock, the app will still work!

