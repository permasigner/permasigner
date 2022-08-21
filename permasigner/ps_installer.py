import time
from getpass import getpass
from threading import Thread

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
from scp import SCPClient

from .ps_logger import Logger, Colors
from .ps_tcprelay import Relayer


class Installer:
    def __init__(self, args, path):
        self.args = args
        self.path = path
        self.logger = Logger(self.args)

    def install_deb(self):
        if self.args.tcprelay:
            split = self.args.tcprelay.split(':')
            values = dict(enumerate(split))
            rport = int(values.get(0))
            lport = int(values.get(1))
            host = values.get(2)
            socketpath = values.get(3)
        else:
            rport = 22
            lport = 2222
            host = 'localhost'
            socketpath = '/var/run/usbmuxd'

        relayer = Relayer(rport, lport, self.args, host, socketpath)
        thread = Thread(target=relayer.relay, daemon=True)
        thread.start()
        time.sleep(1)

        password = getpass(
            prompt="Please provide your user password (default = alpine): ")
        if len(password.strip()) == 0:
            password = 'alpine'

        with SSHClient() as client:
            client.set_missing_host_key_policy(AutoAddPolicy())
            try:
                client.connect(host or 'localhost',
                               port=lport,
                               username='mobile',
                               password=f'{password}',
                               timeout=5000,
                               allow_agent=False,
                               look_for_keys=False,
                               compress=True)
            except (SSHException, NoValidConnectionsError, AuthenticationException) as e:
                self.logger.error(e)
                return False

            with SCPClient(client.get_transport()) as scp:
                self.logger.log(f"Sending {self.path} to device", color=Colors.yellow)
                filename = self.path.name
                self.logger.debug(f"Copying via scp from {self.path} to /var/mobile/Documents/")
                scp.put(f'{self.path}',
                        remote_path='/var/mobile/Documents')

            self.logger.debug(f"Running command: sudo -nv")
            stdin, stdout, stderr = client.exec_command('sudo -nv')
            status = stdout.channel.recv_exit_status()
            out = stderr.read()

            if "password".encode() in out:
                command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                self.logger.debug(f"Running command: {command}")
                stdin, stdout, stderr = client.exec_command(
                    f"{command}", get_pty=True)
                time.sleep(0.2)
                stdin.write(f'{password}\n')
                stdin.flush()
                self.logger.log("Installing... this may take some time", color=Colors.yellow)

                self.logger.debug(stdout.read().decode())
                self.logger.debug(f"Running command: sudo apt-get install -f")

                streams = client.exec_command(
                    'sudo apt-get install -f', get_pty=True)
                time.sleep(0.2)
                streams[0].write(f'{password}\n')
                streams[0].flush()
                self.logger.debug(streams[1].read().decode())
            elif status == 0:
                command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                self.logger.debug(f"Running command: {command}")
                output = client.exec_command(f'{command}')[1]
                self.logger.log("Installing... this may take some time", color=Colors.yellow)
                self.logger.debug(output.read().decode())
                self.logger.debug(f"Running command: sudo apt-get install -f")

                output = client.exec_command(
                    'sudo apt-get install -f')[1]
                self.logger.debug(output.read().decode())
            else:
                command = f"su root -c 'dpkg -i /var/mobile/Documents/{filename}'"
                self.logger.debug(f"Running command: {command}")

                streams = client.exec_command(
                    f"{command}", get_pty=True)

                output = streams[1].channel.recv(2048)
                if "password".encode() in output or "Password".encode() in output:
                    password = getpass()
                    streams[0].write(f'{password}\n')
                    streams[0].flush()
                    self.logger.log("Installing... this may take some time", color=Colors.yellow)
                    self.logger.debug(streams[1].read().decode())
                    streams = client.exec_command(
                        "su root -c 'apt-get install -f'", get_pty=True)
                    time.sleep(0.2)
                    streams[0].write(f'{password}\n')
                    streams[0].flush()
                    self.logger.debug(streams[1].channel.recv(2048).decode())
                else:
                    self.logger.log("Installing... this may take some time", color=Colors.yellow)
                    self.logger.debug(streams[1].read().decode())
                    self.logger.debug(f"Running command: sudo apt-get install -f")

                    output = client.exec_command(
                        'sudo apt-get install -f')[1]
                    self.logger.debug(output.read().decode())
            return True
