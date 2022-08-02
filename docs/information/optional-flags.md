---
description: Flags you can pass through to change options.
---

# Optional Flags

## Command Arguments

```
usage: main.py [-h] [-c] [-d] [-u URL] [-p PATH] [-i] [-n] [-o OUTPUT] [-b BUNDLEID] [-N NAME]

optional arguments:
  -h, --help            show help message and exit
  -d, --debug           shows some debug info, only useful for testing
  -u URL, --url URL     the direct URL of the IPA to be signed
  -p PATH, --path PATH  the direct local path of the IPA to be signed
  -i, --install         installs the application to your device
  -n, --noinstall       skips the install prompt
  -o OUTPUT, --output OUTPUT
                        specify output file
  -b BUNDLEID, --bundleid BUNDLEID
                        specify new bundle id
  -N NAME, --name NAME  specify new app name
  -m MINVER, --minver MINVER
                        specify new minimum app version (14.0 recommended)
  -v, --version         show current version and exit
  -l LDIDFORK, --ldidfork LDIDFORK
                        specify a fork of ldid (eg. ProcursusTeam, itsnebulalol [default])
```

## Docker Options

Use `-e ARGUMENTNAME="VALUE"` for strings, use `-e ARGUMENTNAME=1` to enable a flag.

### Currently supported arguments

```
DEBUG     shows some debug info, only useful for testing
URL       the direct URL of the IPA to be signed
BUNDLEID  specify new bundle id
NAME      specify new app name
MINVER    specify new minimum app version (14.0 recommended)
LDIDFORK  specify a fork of ldid (eg. ProcursusTeam, itsnebulalol [default])
```
