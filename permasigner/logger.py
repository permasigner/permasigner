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
    def log(message):
        print(f"[*] {message}")
        
    def debug(message):
        print(Colors.lightblue + Colors.bold + f"[DEBUG] " + Colors.reset + Colors.lightblue + message + Colors.reset)
        
    def error(message):
        print(Colors.lightred + Colors.bold + f"[!] " + Colors.reset + Colors.lightred + message + Colors.reset)