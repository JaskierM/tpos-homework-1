import socket
import click
import libtmux
import random
import shutil

from tqdm import tqdm
from libtmux.exc import LibTmuxException
from libtmux._internal.query_list import ObjectDoesNotExist
from pathlib import Path


IP = 'localhost'
HASH_SIZE = 128
MAX_WINDOWS_TO_CREATE = 100

session = None


def get_available_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


def set_env(pane, session_path, window_id, port, token):
    pane.send_keys(f'cd {session_path}')
    pane.send_keys('mkdir .venv && python3 -m venv .venv')
    pane.send_keys('source .venv/bin/activate')
    pane.send_keys(f'jupyter notebook --ip {IP} --port {port} --no-browser --NotebookApp.token={token} '
                   f'--NotebookApp.notebook_dir=./')


@click.group()
def venvs():
    pass


@venvs.command('start')
@click.argument('n', type=click.IntRange(1, MAX_WINDOWS_TO_CREATE))
def start(n):
    """
    @:param n: Number of environments created
    """
    last_window = len(session.windows) - 1

    for i in tqdm(range(int(n))):
        path = Path(f'dir{last_window + i}')
        path.mkdir(exist_ok=True)

        window = session.new_window(attach=False)
        pane = window.split_window(attach=False)

        port = get_available_port()
        token = session.session_name + window.window_id[1:] + str(port) + str(random.getrandbits(HASH_SIZE))
        set_env(pane, path, window.window_id, port, token)

        click.echo(f'Created window "{window.window_id[1:]}" port: "{port}" token: "{token}"')


def stop_window(window_name):
    """
    @:param session_name: Name of the tmux session in which the environments are running
    """
    try:
        try:
            path = Path(f'dir{window_name}')
            shutil.rmtree(path, ignore_errors=True)
        except FileNotFoundError:
            pass

        session.kill_window(str(int(window_name) + 1))
        click.echo(f'Window "{window_name}" was killed')
    except (LibTmuxException, ObjectDoesNotExist):
        click.echo(f'Can\'t find window')


@venvs.command('stop')
@click.argument('window_name', type=click.STRING)
def stop(window_name):
    """
    @:param window_name: Name of the tmux window in which the environments are running
    """
    stop_window(window_name)


@venvs.command('stop_all')
def stop_all():
    windows = [str(int(window.window_id[1:]) - 1) for window in session.windows]

    if not windows:
        click.echo("No windows to kill")
        return

    for window in windows:
        stop_window(window)
    click.echo('All windows were killed')


if __name__ == '__main__':
    server = libtmux.Server()

    if not server.sessions:
        session = server.new_session()
        click.echo(f'Session "{session.name}" created and connected')
    else:
        session = server.sessions[-1]
        click.echo(f'Current session is "{session.name}"')

    venvs()
