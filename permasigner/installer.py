import subprocess
from argparse import Namespace
from subprocess import PIPE
from pathlib import Path
from . import logger
from .logger import colors


def install_on_ios(output_path: Path, debug: bool) -> bool:
    # Check if user is in sudoers file by running sudo -nv
    logger.debug("Checking if user is in sudoers file", debug)
    process = subprocess.run('sudo -nv'.split(), capture_output=True)

    # Exit status 0: user has sudo rights, no password is required
    # Error starts with 'sudo:', has sudo rights, needs a password
    if process.returncode == 0 or 'sudo:' in process.stderr.decode():
        return install_with_sudo_on_ios(output_path, debug)
    # User does not have sudo rights
    # Install with su
    else:
        return install_with_su_on_ios(output_path, debug)


def install_with_sudo_on_ios(output_path: Path, debug: bool) -> bool:
    # User is in sudoers file therefore we invoke dpkg with sudo
    logger.debug("User is in sudoers file", debug)
    logger.debug(f"Running command: sudo dpkg -i {output_path}", debug)

    subprocess.run(["sudo", "dpkg", "-i", f"{output_path}"], stdin=PIPE, capture_output=True)

    # This is needed on elucuratus bootstrap
    # Otherwise the package will end up in a half installed state
    logger.debug(f"Running command: sudo apt-get install -f", debug)
    subprocess.run(['sudo', 'apt-get', 'install', '-f'], stdin=PIPE, capture_output=True)

    return True


def install_with_su_on_ios(output_path: Path, debug: bool) -> bool:
    # User is not in sudoers file therefore we invoke dpkg with su as root user
    logger.debug("User is not in sudoers, will use su instead", debug)

    logger.debug(f"Running command: su root -c 'dpkg -i {output_path}'", debug)
    subprocess.run(f"su root -c 'dpkg -i {output_path}'".split(), stdin=PIPE, capture_output=True)

    # This is needed on elucuratus bootstrap
    # Otherwise the package will end up in half installed state
    logger.debug(f"Running command: su root -c 'apt-get install -f'", debug)
    subprocess.run("su root -c 'apt-get install -f'".split(), stdin=PIPE, capture_output=True)

    return True


def install_from_pc(path: Path, args: Namespace) -> bool:

    try:
        from paramiko.client import AutoAddPolicy, SSHClient
        from paramiko.ssh_exception import AuthenticationException, SSHException
        from scp import SCPClient
        import time
        from getpass import getpass
        from threading import Thread
        from . import tcprelay
    except ModuleNotFoundError:
        logger.error('Installer dependencies are missing. Install them with:')
        logger.error("pip install 'permasigner[installer]' if using pip")
        logger.error("poetry install --all-extras if using poetry")
        exit(1)

    # Set tcprelay arguments based on whether the flag was passed or not
    if args.tcprelay:
        split = args.tcprelay.split(':')
        values = dict(enumerate(split))
        rport = int(values.get(0))
        lport = int(values.get(1))
        host = values.get(2)
        socketpath = values.get(3)
    # If no tcprelay argument is present,
    # then, use default values:
    # remote port = 22
    # local port = 2222
    # host = "localhost"
    # path to usbmuxd socket = "var/run/usbmuxd"
    else:
        rport = 22
        lport = 2222
        host = 'localhost'
        socketpath = '/var/run/usbmuxd'

    # Start TCPRelay in a separate thread
    relayer = tcprelay.Relayer(rport, lport, host, socketpath)
    thread = Thread(target=relayer.relay, daemon=True)
    thread.start()
    time.sleep(1)

    # Get user password to establish the SSH connection
    password = getpass(prompt="Please provide your user password (default = alpine): ")

    # Default to 'alpine' on empty input
    if len(password.strip()) == 0:
        password = 'alpine'

    # Connect to device via SSHClient
    with SSHClient() as client:
        client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            client.connect(host or 'localhost',
                           port=lport,
                           username='mobile',
                           password=f'{password}',
                           timeout=20,
                           allow_agent=False,
                           look_for_keys=False,
                           compress=True)

        except (SSHException, AuthenticationException) as e:
            logger.error(e)
            return False

        # Send deb file to device using SCP
        # Default destination is /var/mobile/Documents
        with SCPClient(client.get_transport()) as scp:
            logger.log(f"Sending {path} to device", color=colors["yellow"])
            filename = path.name
            logger.debug(f"Copying via scp from {path} to /var/mobile/Documents/", args.debug)
            scp.put(f'{path}',
                    remote_path='/var/mobile/Documents')

        # Check if user is in sudoers file by running sudo -nv
        logger.debug(f"Running command: sudo -nv", args.debug)
        stdin, stdout, stderr = client.exec_command('sudo -nv')
        status = stdout.channel.recv_exit_status()

        # Password required prompt: user has sudo rights but password is required
        if "password" in stderr.read().decode():
            command = f"sudo dpkg -i /var/mobile/Documents/{filename}"
            logger.debug(f"Running command: {command}", args.debug)
            stdin, stdout, stderr = client.exec_command(f"{command}", get_pty=True)

            # Sleep to prevent echoing password
            time.sleep(0.2)

            # Write password to stdin
            stdin.write(f'{password}\n')
            stdin.flush()

            logger.log("Installing... this may take some time", color=colors["yellow"])

            # Read output from stdout
            output = stdout.read().decode()
            logger.debug(output, args.debug)

            # Is needed on elucubratus
            # so that the package does not end up
            # in half-installed state
            logger.debug(f"Running command: sudo apt-get install -f", args.debug)
            stdin, stdout, stderr = client.exec_command('sudo apt-get install -f', get_pty=True)

            # Sleep to prevent echoing password
            time.sleep(0.2)

            # Write password to stdin
            stdin.write(f'{password}\n')
            stdin.flush()

            # Read output from stdout
            output = stdout.read().decode()

            logger.debug(output, args.debug)
        # Exit status 0: user has sudo rights and NOPASSWD
        elif status == 0:
            # Install by invoking dpkg with sudo
            logger.debug(f"Running command: sudo dpkg -i /var/mobile/Documents/{filename}", args.debug)
            stdin, stdout, stderr = client.exec_command(f"sudo dpkg -i /var/mobile/Documents/{filename}")

            logger.log("Installing... this may take some time", color=colors["yellow"])

            # Block until we can read the output from stdout
            output = stdout.read().decode()
            logger.debug(output, args.debug)

            # Needed on elucuratus
            # to prevent half-installed state
            logger.debug(f"Running command: sudo apt-get install -f", args.debug)
            stdin, stdout, stderr = client.exec_command('sudo apt-get install -f')

            logger.debug(stdout.read().decode(), args.debug)
        # User does not have sudo rights
        # Fallback to su
        else:
            # Install with dpkg by invoking su as root user
            logger.debug(f"Running command: su root -c 'dpkg -i /var/mobile/Documents/{filename}", args.debug)
            stdin, stdout, stderr = client.exec_command(f"su root -c 'dpkg -i /var/mobile/Documents/{filename}'", get_pty=True)

            # Read output from the channel
            output = stdout.channel.recv(2048)

            # Check if we got a password prompt
            if "password".encode() in output or "Password".encode() in output:
                # Read password from cli
                # and write it to stdin
                password = getpass()
                stdin.write(f'{password}\n')
                stdin.flush()

                logger.log("Installing... this may take some time", color=colors["yellow"])

                # Block until we can read the output from stdout
                output = stdout.read().decode()
                logger.debug(output, args.debug)

                # Needed on elucuratus
                # to prevent half-installed state
                stdin, stdout, stderr = client.exec_command("su root -c 'apt-get install -f'", get_pty=True)
                time.sleep(0.2)

                # Write password to stdin
                stdin.write(f'{password}\n')
                stdin.flush()

                # Block until we can read the output from the channel
                output = stdout.channel.recv(2048).decode()

                logger.debug(output, args.debug)
            else:
                logger.log("Installing... this may take some time", color=colors["yellow"])

                # Block until we can read the output from stdout
                output = stdout.read().decode()
                logger.debug(output, args.debug)

                # Needed on elucuratus
                # to prevent half-installed state
                logger.debug(f"Running command: sudo apt-get install -f", args.debug)
                stdin, stdout, stderr = client.exec_command('sudo apt-get install -f')

                # Block until we can read the output from stdout
                output = stdout.read().decode()

                logger.debug(output, args.debug)

        return True
