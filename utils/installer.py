import subprocess
import time
from getpass import getpass

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
from scp import SCPClient
from subprocess import DEVNULL, PIPE


class Installer:

    def install_deb(args, out_deb_name):
        print(f'[*] Installing {out_deb_name} to the device')
        print("Relaying TCP connection")
        if args.debug:
            print("[DEBUG] Running command: ./utils/tcprelay.py -t 22:2222")
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
                    if args.output:
                        print(
                            f"Sending {args.output.split('/')[-1]} to device")
                        scp.put(f'{args.output}',
                                remote_path='/var/mobile/Documents')
                    else:
                        print(f"Sending {out_deb_name}.deb to device")
                        scp.put(f'output/{out_deb_name}.deb',
                                remote_path='/var/mobile/Documents')

                    stdin, stdout, stderr = client.exec_command('sudo -nv')
                    status = stdout.channel.recv_exit_status()
                    out = stderr.read().decode()

                    if "password" in out:
                        print("User is in sudoers, using sudo")
                        if args.output:
                            stdin, stdout, stderr = client.exec_command(
                                f"sudo dpkg -i /var/mobile/Documents/{args.output.split('/')[-1].replace('.deb', '')}.deb",
                                get_pty=True)
                        else:
                            stdin, stdout, stderr = client.exec_command(f'sudo dpkg -i /var/mobile/Documents/{out_deb_name}.deb',
                                                                    get_pty=True)
                        password = getpass()
                        stdin.write(f'{password}\n')
                        stdin.flush()
                        print("Installing... this may take some time")
                        print(stdout.read().decode())
                        # for elucubratus bootstrap
                        streams = client.exec_command('sudo apt -f install', get_pty=True)
                        streams[0].write(f'{password}\n')
                        streams[0].flush()
                        print(streams[1].read().decode())
                    elif status == 0:
                        print('User has nopasswd set')
                        if args.output:
                            output = client.exec_command(f"sudo dpkg -i /var/mobile/Documents/{args.output.split('/')[-1].replace('.deb', '')}.deb")[1]
                        else:
                            output = client.exec_command(f'sudo dpkg -i /var/mobile/Documents/{out_deb_name}.deb')[1]
                        print("Installing... this may take some time")
                        print(output.read().decode())
                        output = client.exec_command('sudo apt -f install')[1].read().decode()
                        print(output)
                    else:
                        print('Using su command')
                        if args.output:
                            streams = client.exec_command(f"su root -c 'dpkg -i /var/mobile/Documents/{args.output.split('/')[-1].replace('.deb', '')}.deb'",
                                                      get_pty=True)
                        else:
                            streams = client.exec_command(
                                f"su root -c 'dpkg -i /var/mobile/Documents/{out_deb_name}.deb'",
                                get_pty=True)
                        output = streams[1].channel.recv(2048).decode()
                        if "password" in output.lower():
                            password = getpass()
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            print("Installing... this may take some time")
                            print(streams[1].read().decode())
                            # for elucubratus bootstrap
                            streams = client.exec_command("su root -c 'apt -f install'", get_pty=True)
                            streams[0].write(f'{password}\n')
                            streams[0].flush()
                            print(streams[1].channel.recv(2048).decode())
                        else:
                            print("Installing... this may take some time")
                            print(streams[1].read().decode())
                            streams = client.exec_command('sudo apt -f install')
                            print(streams[1].read().decode())
        except (SSHException, NoValidConnectionsError, AuthenticationException) as e:
            print(e)
        finally:
            relay.kill()
