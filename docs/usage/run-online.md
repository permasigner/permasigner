---
description: Run Permasigner with a GitHub workflow.
---

**NOTE**: This method is in progress. Give it a try, it'll probably work! If you run into any issues, please open a GitHub issue and specify you're using the action. This will work on the device as well, no need for a PC.

* Click fork on the top right, then click create fork
   * A GitHub account is required, it's free!
> ![image](https://user-images.githubusercontent.com/18669106/180668388-fea832be-dd8d-4387-bb00-64637ec8c4a5.png)\
> ![image](https://user-images.githubusercontent.com/18669106/180667994-4f5e257d-a701-43a3-9613-f860c3990f44.png)

* If you have made a fork before, click fetch upstream then fetch and merge
   * This should be done every time you sign an app
> ![image](https://user-images.githubusercontent.com/18669106/180668039-895bf508-34ba-4f68-84c2-9dd86b068efa.png)

* Click Actions on the top, then enable actions
> ![image](https://user-images.githubusercontent.com/18669106/180668059-cbfb4099-e40c-4828-b505-1532c6ae326f.png)

* Click run script on the left, then click run workflow on the right
> ![image](https://user-images.githubusercontent.com/18669106/180668091-29077082-8738-4b00-85a2-93b24c97b1b4.png)

* Paste in the **direct** URL to an IPA file in the box, then press run workflow
> ![image](https://user-images.githubusercontent.com/18669106/180668191-318d1098-fa80-4e34-ab69-94e02df56975.png)

* Wait for the workflow to be finished, then click on it
> ![image](https://user-images.githubusercontent.com/18669106/180668274-44ec62d7-0be2-47c7-a8ac-ed19fb5e4c5f.png)

* Download the artifact, unzip it, and send the deb file to your iDevice!
   * Airdropping the file is probably the easiest, but you can use something like Dropbox or Mega. Advanced users can use openssh-sftp-server from Procursus. If you're running this on the device, just unzip it and install it!
> ![image](https://user-images.githubusercontent.com/18669106/180668328-12083245-2ef8-43e1-8622-42acbe6dc33c.png)
