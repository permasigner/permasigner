---
description: Get your development environment set up and start programming!
---

# Getting Started

Do you want to contribute to Permasigner but don't know where to start? These guides will help you get set up so you can start helping out!

We highly recommend using macOS or Linux to develop, but Windows will work too via Docker.

## Make a fork of the repo

To make any changes, you need to make a fork of the Permasigner repo.

* Sign up for GitHub if you haven't already, you'll need it to contribute
* Go to [this link](https://github.com/permasigner/permasigner/fork), and create the fork
* We recommend enabling Actions to test and lint your code, so click the Actions tab, and click the "I know what I'm doing" button

Congrats! You now have your own copy of Permasigner! Now, you can clone it to your local machine.

## Cloning your fork

First, we're going to start by getting the source of Permasigner from GitHub.

* Clone this repository with `git clone https://github.com/<your username here>/permasigner && cd permasigner`
  * \[Windows] If this fails, install git from [here](https://git-scm.com/download/win).
  * \[macOS] If this fails, install git with Xcode dev tools.
  * \[Linux] If this fails, install git with your package manager of choice; ex. `sudo apt install git`.

Now that you have the source cloned locally, we'll need to install packages and tools required.&#x20;

You can use VSCode if you'd like, but it's not strictly necessary. For this tutorial, you should install VSCode.

[Python](https://www.python.org/) and Poetry (`pip install poetry`) are **required**. You can use the latest 3.x version of Python. On macOS, you can install it with brew (`brew install python@3.10`), and a CLI package manager on Linux (eg. `apt install python3`).

## Open Cloned Repo in VSCode

Since we're using VSCode in this tutorial, we'll show you how to set it up.

* Open up VSCode, click the open folder button, and select the directory you cloned earlier
* Follow [VSCode Setup](visual-studio-code-setup.md), then come back

You can use `poetry run python3 main.py` in the cloned directory to start Permasigner. We recommend using VSCode's integrated terminal.

Check out [Important Files](important-files.md) to see which files handle what, and look at [Committing and making a Pull Request](committing-and-making-a-pull-request.md) for your next steps.
