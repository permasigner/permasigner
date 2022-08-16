import os

if os.name == 'nt':  # Only if we are running on Windows
    from ctypes import windll
    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)


class Colors:
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'

    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'


class Logger:
    def __init__(self, args):
        self.args = args

    def log(self, message, color=None):
        if color is None:
            print(f"[*] {message}")
        else:
            print(color + Colors.bold + "[*] " + Colors.reset + color + f"{message}" + Colors.reset)

    def debug(self, message):
        if self.args.debug:
            print(
                Colors.lightcyan + Colors.bold + "[DEBUG] " + Colors.reset + Colors.lightcyan + f"{message}" + Colors.reset)

    def error(self, message):
        print(Colors.lightred + Colors.bold + "[!] " + Colors.reset + Colors.lightred + f"{message}" + Colors.reset)

    def ask(self, message):
        return input(Colors.orange + Colors.bold + "[?] " + Colors.reset + Colors.orange + f"{message}" + Colors.reset)
