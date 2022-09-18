---
description: Run Permasigner in the official Docker container.
---

* [Install Docker](https://docs.docker.com/get-docker/)
* Open a terminal
	*  \[Windows] Hold Win + R and type `powershell`.
	*  \[macOS] Terminal from the Utilities folder or spotlight.
	*  \[Linux] Ctrl + Shift + T on most distros.
* Pull the container with `docker pull ghcr.io/permasigner/permasigner`
* Create `output` and `ipas` directories.
* Launch the Docker container with:
	*  \[Windows] `docker run -it --rm -v ${pwd}/output:/app/output -v ${pwd}/ipas:/app/ipas permasigner/permasigner -d`.
	*  \[Linux/macOS] `docker run -it --rm -v "$PWD/output":/app/output -v "$PWD/ipas":/app/ipas permasigner/permasigner -d`\
		* Append additional script arguments at the end of the command.

* It is possible to deploy produced deb to device and install it from within the docker container. For that pass additonal arguments to docker command.
	*  \[Windows] `no additional arguments are required`.
	*  \[Linux/macOS] `--privileged -p 2222:2222 -v /var/run/usbmuxd:/var/run/usbmuxd`
* Send the deb file to your iDevice
    * The script can do that for you, you will be asked to input the user password for ssh access.
    * Airdropping the file is probably the easiest, but you can use something like Dropbox or Mega. Advanced users can use openssh-sftp-server from Procursus.
* Reboot to stock, the app will still work!