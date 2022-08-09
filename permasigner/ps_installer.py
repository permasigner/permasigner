import subprocess
import time
from getpass import getpass

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
from scp import SCPClient
from subprocess import DEVNULL, PIPE

from .ps_logger import Logger, Colors


class Installer:
    def __init__(self, args, path):
        self.args = args
        self.path = path

    def install_deb(self):
        Logger.log("Relaying TCP connection", color=Colors.pink)
        Logger.debug(f"Running command: ./permasigner/ps_tcprelay.py -t 22:2222", self.args)

        relay = subprocess.Popen(
            './permasigner/ps_tcprelay.py -t 22:2222'.split(), stdout=DEVNULL, stderr=PIPE)
        time.sleep(1)
        try:
            password = getpass(
                prompt="Please provide your user password (default = alpine): ")
            if len(password.strip()) == 0:
                password = 'alpine'
            with SSHClient() as client:
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect('localhost',
                               port=2222,
                               username='mobile',
                               password=f'{password}',
                               timeout=5000,
                               allow_agent=False,
                               look_for_keys=False,
                               compress=True)
                with SCPClient(client.get_transport()) as scp:
                    Logger.log(f"Sending {self.path} to device", color=Colors.pink)
                    filename = self.path.split("/")[-1]
                    Logger.debug(f"Copying via scp from {self.path} to /var/mobile/Documents/", self.args)

                    scp.put(f'{self.path}',
                            remote_path='/var/mobile/Documents')
                    Logger.debug(f"Running command: sudo -nv", self.args)

                    stdin, stdout, stderr = client.exec_command('sudo -nv')
                    status = stdout.channel.recv_exit_status()
                    out = stderr.read().decode()

                    if "password" in out:
                        command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                        Logger.debug(f"Running command: {command}", self.args)

                        stdin, stdout, stderr = client.exec_command(
                            f"{command}", get_pty=True)
                        time.sleep(0.2)
                        stdin.write(f'{password}\n')
                        stdin.flush()
                        Logger.log("Installing... this may take some time", color=Colors.pink)

                        Logger.debug(stdout.read().decode(), self.args)
                        Logger.debug(f"Running command: sudo apt-get install -f", self.args)

                        streams = client.exec_command(
                            'sudo apt-get install -f', get_pty=True)
                        time.sleep(0.2)
                        streams[0].write(f'{password}\n')
                        streams[0].flush()
                        Logger.debug(streams[1].read().decode(), self.args)
                    elif status == 0:
                        command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                        Logger.debug(f"Running command: {command}", self.args)

                        output = client.exec_command(f'{command}')[1]
                        Logger.log("Installing... this may take some time", color=Colors.pink)
                        Logger.debug(output.read().decode())
                        Logger.debug(f"Running command: sudo apt-get install -f", self.args)

                        output = client.exec_command(
                            'sudo apt-get install -f')[1]
                        Logger.debug(output.read().decode(), self.args)
                    else:
                        command = f"su root -c 'dpkg -i /var/mobile/Documents/{filename}'"
                        Logger.debug(f"Running command: {command}", self.args)

                        streams = client.exec_command(
                            f"{command}", get_pty=True)

                        output = streams[1].channel.recv(2048).decode()
                        if "password".encode() in output or "Password".encode() in output:
                            password = getpass()
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            Logger.log("Installing... this may take some time", color=Colors.pink)
                            Logger.debug(streams[1].read().decode(), self.args)
                            streams = client.exec_command(
                                "su root -c 'apt-get install -f'", get_pty=True)
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            Logger.debug(streams[1].channel.recv(2048).decode(), self.args)
                        else:
                            Logger.log("Installing... this may take some time", color=Colors.pink)
                            Logger.debug(streams[1].read().decode(), self.args)
                            Logger.debug(f"Running command: sudo apt-get install -f", self.args)

                            output = client.exec_command(
                                'sudo apt-get install -f')[1]
                            logger.debug(output.read().decode(), self.args)
                    return True
        except (SSHException, NoValidConnectionsError, AuthenticationException) as e:
            Logger.error(e)
            return False
        finally:
            relay.kill()
