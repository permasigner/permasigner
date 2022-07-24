from utils.usbmux import USBMux
from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
from scp import SCPClient


class Installer:
    def get_shell_output(args, shell):
        out = ''
        time.sleep(1)
        while shell.recv_ready():
            out += shell.recv(2048).decode()
        return out

    def treat_shell_output(args, shell):
        s_output = get_shell_output(args, shell)
        if 'password' in s_output.lower():
            shell.send((getpass() + '\n').encode())
            s_output = Installer.get_shell_output(args, shell)
        for line in s_output.splitlines():
            print(line)

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
                error = stderr.readline()
                status = stdout.channel.recv_exit_status()
                shell = client.invoke_shell()
                if status == 0 or 'password' in error:
                    print("User is in sudoers, using sudo")
                    if args.output:
                        shell.send(
                            f"sudo dpkg -i /var/mobile/Documents/{args.output.split('/')[-1].replace('.deb', '')}.deb\n".encode())
                    else:
                        shell.send(
                            f"sudo dpkg -i /var/mobile/Documents/{out_deb_name}.deb\n".encode())

                    Installer.treat_shell_output(args, shell)
                    shell.send(f"sudo apt -f install\n".encode())
                    Installer.treat_shell_output(args, shell)
                else:
                    print("User is not in sudoers, using su instead")
                    if args.output:
                        shell.send(
                            f"su root -c 'dpkg -i /var/mobile/Documents/{args.output.split('/')[-1].replace('.deb', '')}.deb'\n".encode())
                    else:
                        shell.send(
                            f"su root -c 'dpkg -i /var/mobile/Documents/{out_deb_name}.deb'\n".encode())

                    Installer.treat_shell_output(args, shell)
                    shell.send(f"su root -c 'apt -f install'\n".encode())
                    Installer.treat_shell_output(args, shell)
        except (SSHException, NoValidConnectionsError, AuthenticationException) as e:
            print(e)
        finally:
            shell.close()
            relay.kill()
