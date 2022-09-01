import argparse
import permasigner
from . import utils


def main(argv=None, in_package=None) -> None:
    if argv is None:
        in_package = True

    in_package = False if in_package is None else in_package

    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument('-f', '--folder', type=str,
                             help="sign multiple IPAs from a direct path to a folder")
    input_group.add_argument('-u', '--url', type=str,
                             help="the direct URL of the IPA to be signed")
    input_group.add_argument('-p', '--path', type=str,
                             help="the direct local path of the IPA to be signed")

    parser.add_argument('-d', '--debug', action='store_true',
                        help="shows some debug info, only useful for testing")
    parser.add_argument('-c', '--codesign', action='store_true',
                        help="uses codesign instead of ldid")
    parser.add_argument('-i', '--install', action='store_true',
                        help="installs the application to your device")
    parser.add_argument('-o', '--output', type=str,
                        help="specify output path")
    parser.add_argument('-b', '--bundleid', type=str,
                        help="specify new bundle id")
    parser.add_argument('-n', '--name', type=str,
                        help="specify new app name")
    parser.add_argument('-a', '--author', type=str,
                        help="specify new app author")
    parser.add_argument('-m', '--minver', type=str,
                        help="specify new minimum app version (14.0 recommended)")
    parser.add_argument('-l', '--ldidfork', type=str,
                        help="specify a fork of ldid (eg. ProcursusTeam, permasigner [default])")
    parser.add_argument('-t', '--tcprelay', type=str,
                        help="optional args for tcprelay (ex: 22:2222:localhost:/var/run/usbmuxd)")
    parser.add_argument('-e', '--entitlements', type=str,
                        help="path to entitlements file")
    parser.add_argument('-z', '--no-ldid-check', action='store_true',
                        help="disable ldid hash checking")
    parser.add_argument('-v', '--version', action='version', version=f'Permasigner v{utils.get_version()}',
                        help='show current version and exit')
    args = parser.parse_args()

    ps = permasigner.Permasigner(in_package, args)
    ps.main()


if __name__ == "__main__":
    main()
