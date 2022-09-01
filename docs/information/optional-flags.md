---
description: Flags you can pass through to change options.
---

# Optional Flags

## Command Arguments

```
usage: [-h] (-f FOLDER | -u URL | -p PATH) [-d] [-c] [-i] [-o OUTPUT] [-b BUNDLEID] [-n NAME] [-a AUTHOR] [-m MINVER] [-l LDIDFORK] [-t TCPRELAY] [-e ENTITLEMENTS] [-z] [-v] [-P]

options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        sign multiple IPAs from a direct path to a folder
  -u URL, --url URL     the direct URL of the IPA to be signed
  -p PATH, --path PATH  the direct local path of the IPA to be signed
  -d, --debug           shows some debug info, only useful for testing
  -c, --codesign        uses codesign instead of ldid
  -i, --install         installs the application to your device
  -o OUTPUT, --output OUTPUT
                        specify output path
  -b BUNDLEID, --bundleid BUNDLEID
                        specify new bundle id
  -n NAME, --name NAME  specify new app name
  -a AUTHOR, --author AUTHOR
                        specify new app author
  -m MINVER, --minver MINVER
                        specify new minimum app version (14.0 recommended)
  -l LDIDFORK, --ldidfork LDIDFORK
                        specify a fork of ldid (eg. ProcursusTeam, permasigner [default])
  -t TCPRELAY, --tcprelay TCPRELAY
                        optional args for tcprelay (ex: 22:2222:localhost:/var/run/usbmuxd)
  -e ENTITLEMENTS, --entitlements ENTITLEMENTS
                        path to entitlements file
  -z, --no-ldid-check   disable ldid hash checking
  -v, --version         show current version and exit
```

## Docker Options

Use `-e ARGUMENTNAME="VALUE"` for strings, use `-e ARGUMENTNAME=1` to enable a flag.

### Currently supported arguments

```
DEBUG          shows some debug info, only useful for testing
URL            the direct URL of the IPA to be signed
BUNDLEID       specify new bundle id
NAME           specify new app name
MINVER         specify new minimum app version (14.0 recommended)
LDIDFORK       specify a fork of ldid (eg. ProcursusTeam, permasigner [default])
FOLDER         sign multiple IPAs from a direct path to a folder ("ipas" recommended)
TCPRELAY       optional args for tcprelay (ex: 22:2222:localhost:/var/run/usbmuxd)
ENTITLEMENTS   path to entitlements file
NO_LDID_CHECK  disable ldid hash checking
VERSION        show current version and exit
```
