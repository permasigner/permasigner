import os

if os.name == 'nt':  # Only if we are running on Windows
    from ctypes import windll
    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)


colors = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "orange": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "lightgrey": "\033[37m",
    "darkgrey": "\033[90m",
    "lightred": "\033[91m",
    "lightgreen": "\033[92m",
    "yellow": "\033[93m",
    "lightblue": "\033[94m",
    "pink": "\033[95m",
    "lightcyan": "\033[96m",

    "reset": "\033[0m",
    "bold": "\033[01m",
    "disable": "\033[02m",
    "underline": "\033[04m",
    "reverse": "\033[07m",
    "strikethrough": "\033[09m",
    "invisible": "\033[08m"
}


def log(message, color=None):
    if color is None:
        print(f"{message}")
    else:
        print("\n" + color + colors["bold"] + "[*] " + colors["reset"] + color + f"{message}" + colors["reset"])


def debug(message, dbg):
    if dbg:
        print(colors["lightcyan"] + colors["bold"] + "[DEBUG] " + colors["reset"] + colors["lightcyan"] + f"{message}" + colors["reset"])


def error(message):
    print(colors["lightred"] + colors["bold"] + "[!] " + colors["reset"] + colors["lightred"] + f"{message}" + colors["reset"])


def ask(message):
    return input(colors["orange"] + colors["bold"] + "[?] " + colors["reset"] + colors["orange"] + f"{message}" + colors["reset"])


def info(message):
    print(colors["green"] + colors["bold"] + "[*] " + colors["reset"] + colors["green"] + f"{message}" + colors["reset"])
