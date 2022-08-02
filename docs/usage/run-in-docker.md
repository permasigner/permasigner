---
description: Run Permasigner in the official Docker container.
---

**TLDR:** The Docker command is:
*  \[Windows] `docker run -it --rm -v ${pwd}/output:/usr/src/permasigner/output -v ${pwd}/ipas:/usr/src/permasigner/ipas itsnebulalol/permasigner`
*  \[Linux/macOS] `docker run -it --rm -v "$PWD/output":/usr/src/permasigner/output -v "$PWD/ipas":/usr/src/permasigner/ipas -e DEBUG=1 itsnebulalol/permasigner`

  ---

* [Install Docker](https://docs.docker.com/get-docker/)
* Open a terminal
	*  \[Windows] Hold Win + R and type `powershell`.
	*  \[macOS] Terminal from the Utilities folder or spotlight.
	*  \[Linux] Ctrl + Shift + T on most distros.
* Pull the container with `docker pull docker.io/itsnebulalol/permasigner`
* Create `output` and `ipas` directories.
* Launch the Docker container with:
	*  \[Windows] `docker run -it --rm -v ${pwd}/output:/usr/src/permasigner/output -v ${pwd}/ipas:/usr/src/permasigner/ipas itsnebulalol/permasigner`.
	*  \[Linux/macOS] `docker run -it --rm -v "$PWD/output":/usr/src/permasigner/output -v "$PWD/ipas":/usr/src/permasigner/ipas itsnebulalol/permasigner`
* Send the deb file to your iDevice
    * The script can do that for you, you will be asked to input the user password for ssh access.
    * Airdropping the file is probably the easiest, but you can use something like Dropbox or Mega. Advanced users can use openssh-sftp-server from Procursus.
* Reboot to stock, the app will still work!

