---
description: Get your development environment set up!
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

On Windows, you'll need [Docker](https://www.docker.com/products/docker-desktop/) and [Visual Studio Code](https://code.visualstudio.com/). Although we recommend VSCode on every platform, it's necessary for Windows as you can run "dev containers."&#x20;

On macOS and Linux, you can use Docker and VSCode if you'd like, but it's not strictly necessary. For this tutorial, you should install VSCode. On macOS, install dpkg with brew (`brew install dpkg`). For advanced users, use Procursus.

On all platforms, [Python](https://www.python.org/) is **required**. You can use the latest 3.x version. On macOS, you can install it with brew (`brew install python@3.10`), and a CLI package manager on Linux (eg. `apt install python3`).

## Choose your next path

Since instructions are different for other platforms, choose the one you'll be using.

* [macOS and Linux](develop-on-macos-linux.md)
* Windows
