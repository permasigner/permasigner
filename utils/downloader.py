import requests
import subprocess

class DpkgDeb:
    def download_linux_64():
        res = requests.get("http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.20.9_amd64.deb", stream=True)
        try:
            if res.status_code == 200:
                with open(f"dpkg.deb", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] dpkg download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] dpkg download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"ar x dpkg.deb".split(), stdout=subprocess.DEVNULL)
        subprocess.run(f"tar -xf data.tar.xz".split(), stdout=subprocess.DEVNULL)
        copy("usr/bin/dpkg-deb", "dpkg-deb")
        subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
        os.remove("data.tar.xz")
        os.remove("control.tar.xz")
        os.remove("debian-binary")
        os.remove("dpkg.deb")
        rmtree("etc")
        rmtree("sbin")
        rmtree("usr")
        rmtree("var")
        
    def download_linux_arm64():
        res = requests.get("http://ftp.us.debian.org/debian/pool/main/d/dpkg/dpkg_1.20.9_arm64.deb", stream=True)
        try:
            if res.status_code == 200:
                with open(f"dpkg.deb", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] dpkg download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] dpkg download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"ar x dpkg.deb".split(), stdout=subprocess.DEVNULL)
        subprocess.run(f"tar -xf data.tar.xz".split(), stdout=subprocess.DEVNULL)
        copy("usr/bin/dpkg-deb", "dpkg-deb")
        subprocess.run(f"chmod +x dpkg-deb".split(), stdout=subprocess.DEVNULL)
        os.remove("data.tar.xz")
        os.remove("control.tar.xz")
        os.remove("debian-binary")
        os.remove("dpkg.deb")
        rmtree("etc")
        rmtree("sbin")
        rmtree("usr")
        rmtree("var")
       
        
class Ldid:
    linux_64_url = "https://github.com/ProcursusTeam/ldid/releases/latest/download/ldid_linux_x86_64"
    linux_arm64_url = "https://github.com/ProcursusTeam/ldid/releases/latest/download/ldid_linux_aarch64"
    macos_64_url = "https://github.com/ProcursusTeam/ldid/releases/latest/download/ldid_macos_x86_64"
    macos_arm64_url = "https://github.com/ProcursusTeam/ldid/releases/latest/download/ldid_macos_arm64"
    
    def download_linux_64():
        res = requests.get(Ldid.linux_64_url, stream=True)
        try:
            if res.status_code == 200:
                with open(f"ldid", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] ldid download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] ldid download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        
    def download_linux_arm64():
        res = requests.get(Ldid.linux_arm64_url, stream=True)
        try:
            if res.status_code == 200:
                with open(f"ldid", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] ldid download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] ldid download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        
    def download_macos_64():
        res = requests.get(Ldid.macos_64_url, stream=True)
        try:
            if res.status_code == 200:
                with open(f"ldid", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] ldid download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] ldid download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)
        
    def download_macos_arm64():
        res = requests.get(Ldid.macos_arm64_url, stream=True)
        try:
            if res.status_code == 200:
                with open(f"ldid", "wb") as f:
                    f.write(res.content)
            else:
                print(f"[-] ldid download URL is not reachable. Status code: {res.status_code}")
                exit(1)
        except requests.exceptions.RequestException as err:
            print(f"[-] ldid download URL is not reachable. Error: {err}")
            exit(1)
            
        subprocess.run(f"chmod +x ldid".split(), stdout=subprocess.DEVNULL)