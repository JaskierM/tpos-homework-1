import socket
import click
import libtmux
import random

from tqdm import tqdm
from libtmux.exc import LibTmuxException
from libtmux._internal.query_list import ObjectDoesNotExist
from pathlib import Path
import shutil



IP = 'localhost'
HASH_SIZE = 128


def get_available_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


@click.group()
def venvs():
    pass


@click.command()
@click.argument('n', type=click.INT)
def start(n, root_dir='./'):
    """
    @:param n: Number of environments created
    @:param root_dir: Root directory where information about sessions and environments will be stored
    """
    server = libtmux.Server()
    session = server.new_session()

    path = Path(root_dir + 'session_' + session.session_name)
    path.mkdir(exist_ok=True)

    print(f'Created session "{session.session_name}"')

    for _ in tqdm(range(int(n))):
        window = session.new_window(attach=False)
        pane = window.split_window(attach=False)

        port = get_available_port()
        token = session.session_name + window.window_id[1:] + str(port) + str(random.getrandbits(HASH_SIZE))

        pane.send_keys(f'cd {path} && mkdir window_{window.window_id[1:]}')
        pane.send_keys(f'jupyter notebook --ip {IP} --port {port} --no-browser --NotebookApp.token={token} '
                       f'--NotebookApp.notebook_dir=window_{window.window_id[1:]}')

        print(f'Created window "{window.window_id[1:]}" port: "{port}" token: "{token}"')


@click.command()
@click.argument('session_name', type=click.STRING)
@click.argument('window_name', type=click.STRING)
def stop(session_name, window_name):
    """
    @:param session_name: Name of the tmux session in which the environments are running
    @:param window_name: environment number to kill
    """
    server = libtmux.Server()
    try:
        session = server.sessions.get(session_name=session_name)
        window = session.windows.get(window_id=f'@{window_name}')
        path = Path(f'session_{session_name}/window_{window_name}')
        shutil.rmtree(path)
        window.kill_window()

        print(f'Window "{window_name}" in session "{session_name}" was removed')
    except (LibTmuxException, ObjectDoesNotExist, FileNotFoundError):
        print(f'Can\'t find session/window')


@click.command()
@click.argument('session_name', type=click.STRING)
def stop_all(session_name):
    """
    @:param session_name: Name of the tmux session in which the environments are running
    """
    server = libtmux.Server()
    try:
        path = Path(f'session_{session_name}')
        shutil.rmtree(path)
        server.kill_session(session_name)
        print(f'Session "{session_name}" was killed')
    except LibTmuxException:
        print(f'Can\'t find session')


if __name__ == '__main__':
    venvs.add_command(start)
    venvs.add_command(stop)
    venvs.add_command(stop_all)
    venvs()

