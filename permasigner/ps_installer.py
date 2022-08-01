import subprocess
import time
from getpass import getpass

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
from scp import SCPClient
from subprocess import DEVNULL, PIPE

from .ps_logger import Logger, Colors


class Installer:
    def install_deb(args, path_to_deb):
        Logger.log(f'Installing {path_to_deb} to the device', color=Colors.pink)
        print("Relaying TCP connection")
        if args.debug:
            Logger.debug(f"Running command: ./utils/tcprelay.py -t 22:2222")

        relay = subprocess.Popen(
            './utils/tcprelay.py -t 22:2222'.split(), stdout=DEVNULL, stderr=PIPE)
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
                    print(f"Sending {path_to_deb} to device")
                    filename = path_to_deb.split("/")[-1]
                    if args.debug:
                        Logger.debug(f"Copying via scp from {path_to_deb} to /var/mobile/Documents/")

                    scp.put(f'{path_to_deb}',
                            remote_path='/var/mobile/Documents')
                    if args.debug:
                        Logger.debug(f"Running command: sudo -nv")

                    stdin, stdout, stderr = client.exec_command('sudo -nv')
                    status = stdout.channel.recv_exit_status()
                    out = stderr.read().decode()

                    if "password" in out:
                        print("User is in sudoers, using sudo")
                        command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                        if args.debug:
                            Logger.debug(f"Running command: {command}")

                        stdin, stdout, stderr = client.exec_command(
                            f"{command}", get_pty=True)
                        stdin.write(f'{password}\n')
                        stdin.flush()
                        print("Installing... this may take some time")
                        print(stdout.read().decode())

                        if args.debug:
                            Logger.debug(f"Running command: sudo apt-get install -f")
                        # for elucubratus bootstrap
                        streams = client.exec_command(
                            'sudo apt-get install -f', get_pty=True)
                        streams[0].write(f'{password}\n')
                        streams[0].flush()
                        print(streams[1].read().decode())
                    elif status == 0:
                        print('User has nopasswd set')
                        command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
                        if args.debug:
                            Logger.debug(f"Running command: {command}")

                        output = client.exec_command(f'{command}')[1]

                        print("Installing... this may take some time")
                        print(output.read().decode())
                        if args.debug:
                            Logger.debug(f"Running command: sudo apt-get install -f")

                        output = client.exec_command(
                            'sudo apt-get install -f')[1]
                        print(output.read().decode())
                    else:
                        print('Using su command')
                        command = f"su root -c 'dpkg -i /var/mobile/Documents/{filename}'"
                        if args.debug:
                            Logger.debug(f"Running command: {command}")

                        streams = client.exec_command(
                            f"{command}", get_pty=True)

                        output = streams[1].channel.recv(2048).decode()
                        if "password" in output.lower():
                            password = getpass()
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            print("Installing... this may take some time")
                            print(streams[1].read().decode())
                            # for elucubratus bootstrap
                            streams = client.exec_command(
                                "su root -c 'apt-get install -f'", get_pty=True)
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            print(streams[1].channel.recv(2048).decode())
                        else:
                            print("Installing... this may take some time")
                            print(streams[1].read().decode())
                            if args.debug:
                                Logger.debug(f"Running command: sudo apt-get install -f")

                            output = client.exec_command(
                                'sudo apt-get install -f')[1]
                            print(output.read().decode())
        except (SSHException, NoValidConnectionsError, AuthenticationException) as e:
            Logger.error(e)
        finally:
            relay.kill()
