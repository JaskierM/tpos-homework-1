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
session_just_created = False


def get_available_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


def set_env(pane, window_path, port, token):
    pane.send_keys(f'cd {window_path}')
    pane.send_keys('python3 -m venv venv')
    pane.send_keys('source /venv/bin/activate')
    pane.send_keys(f'jupyter notebook --ip {IP} --port {port} --no-browser --NotebookApp.token={token} '
                   f'--NotebookApp.notebook_dir=./')


def set_pane(window, path):
    pane = window.split_window()

    port = get_available_port()
    token = session.session_name + window.window_name + str(port) + str(random.getrandbits(HASH_SIZE))
    set_env(pane, path, port, token)

    click.echo(f'Created window "{window.window_name}" port: "{port}" token: "{token}"')


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

        session.kill_window(window_name)
        click.echo(f'Window "{window_name}" was killed')
    except (LibTmuxException, ObjectDoesNotExist):
        click.echo(f'Can\'t find window')


@click.group()
def venvs():
    pass


@venvs.command('start')
@click.argument('n', type=click.IntRange(1, MAX_WINDOWS_TO_CREATE))
def start(n):
    """
    @:param n: Number of environments created
    """
    global session_just_created

    if session_just_created:
        path = Path(f'dir0')
        path.mkdir(exist_ok=True)
        window = session.windows[-1]
        set_pane(window, path)

        session_just_created = False
        n -= 1

    last_window = int(session.windows[-1].window_name) + 1

    for i in tqdm(range(int(n))):
        window_name = str(last_window + i)

        path = Path(f'dir{window_name}')
        path.mkdir(exist_ok=True)
        window = session.new_window(attach=False, window_name=window_name)
        set_pane(window, path)


@venvs.command('stop')
@click.argument('window_name', type=click.STRING)
def stop(window_name):
    """
    @:param window_name: Name of the tmux window in which the environments are running
    """
    stop_window(window_name)


@venvs.command('stop_all')
def stop_all():
    windows = [str(int(window.window_name)) for window in session.windows]

    if not windows:
        click.echo("No windows to kill")
        return

    for window in windows:
        stop_window(window)
    click.echo('All windows were killed')


if __name__ == '__main__':
    server = libtmux.Server()

    if not server.sessions:
        session = libtmux.Server().new_session(window_name='0')
        session_just_created = True
        click.echo(f'Session "{session.name}" created and connected')
    else:
        session = server.sessions[-1]
        click.echo(f'Current session is "{session.name}"')

    venvs()
