import argparse
import sys

from permasigner import Permasigner

path_options = [{
    "flags": ["-f", "--folder"],
    "args": {
        "type": str,
        "dest": "folder",
        "required": False,
        "help": "the direct path of a directory containing multiple ipas",
    }
}, {
    "flags": ["-u", "--url"],
    "args": {
        "type": str,
        "dest": "url",
        "required": False,
        "help": "the direct URL of the IPA"
    }
}, {
    "flags": ["-p", "--path"],
    "args": {
        "type": str,
        "dest": "path",
        "required": False,
        "help": "the direct path of the IPA"
    }
}]

options = [{
    "flags": ["-d", "--debug"],
    "args": {
        "action": "store_true",
        "dest": "debug",
        "required": False,
        "help": "show debug output, only useful for testing",
    }
}, {
    "flags": ["-c", "--codesign"],
    "args": {
        "action": "store_true",
        "dest": "codesign",
        "required": False,
        "help": "use codesign instead of ldid (only for macOS)"
    }
}, {
    "flags": ["-i", "--install"],
    "args": {
        "action": "store_true",
        "dest": "install",
        "required": False,
        "help": "install the application to your device"
    }
}, {
    "flags": ["-o", "--output"],
    "args": {
        "type": str,
        "dest": "output",
        "required": False,
        "help": "specify output path"
    }
}, {
    "flags": ["-b", "--bundle-id"],
    "args": {
        "type": str,
        "dest": "bundleid",
        "required": False,
        "help": "specify new bundle id"
    }
}, {
    "flags": ["-n", "--name"],
    "args": {
        "type": str,
        "dest": "name",
        "required": False,
        "help": "specify new app name"
    }
}, {
    "flags": ["-a", "--author"],
    "args": {
        "type": str,
        "dest": "author",
        "required": False,
        "help": "specify new app author"
    }
}, {
    "flags": ["-m", "--min-ver"],
    "args": {
        "type": str,
        "dest": "minver",
        "required": False,
        "help": "specify new minimum app version"
    }
}, {
    "flags": ["-l", "--ldid-fork"],
    "args": {
        "type": str,
        "dest": "ldidfork",
        "required": False,
        "help": "specify a fork of ldid"
    }
}, {
    "flags": ["-e", "--entitlements"],
    "args": {
        "type": str,
        "dest": "entitlements",
        "required": False,
        "help": "specify entitlements that will be merged"
    }
}, {
    "flags": ["-t", "--tcprelay"],
    "args": {
        "type": str,
        "dest": "tcprelay",
        "required": False,
        "help": "optional args for tcprelay (ex: 22:2222:localhost:/var/run/usbmuxd)"
    }
}, {
    "flags": ["-z", "--no-ldid-check"],
    "args": {
        "action": "store_true",
        "dest": "nocheckldid",
        "required": False,
        "help": "disable ldid hash checking"
    }
}, {
    "flags": ["-V", "--version"],
    "args": {
        "action": "version",
        "version": "Permasigner "
    }
}]


def main(argv=None, in_package=None) -> None:
    if argv is None:
        in_package = True

    in_package = False if in_package is None else in_package

    parser = argparse.ArgumentParser()
    path_group = parser.add_mutually_exclusive_group(required=True)

    for option in path_options:
        path_group.add_argument(*option.get("flags"), **option.get("args"))

    for option in options:
        parser.add_argument(*option.get("flags"), **option.get("args"))

    args = parser.parse_args()
    permasigner = Permasigner(in_package, args)
    permasigner.main()


if __name__ == "__main__":
    main()
