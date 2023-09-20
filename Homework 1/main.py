import click
import libtmux

from tqdm import tqdm
from libtmux.exc import LibTmuxException
from libtmux._internal.query_list import ObjectDoesNotExist


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
    print(f'Created session "{session.session_name}"')

    for _ in tqdm(range(int(n))):
        session.new_window(attach=False)


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
        session = server.sessions.get(session_id=f'${session_name}')
        session.kill_window(window_name)
        print(f'Window "{window_name}" in session "{session_name}" was removed')
    except ObjectDoesNotExist:
        print(f'Can\'t find session "{session_name}"')
    except LibTmuxException:
        print(f'Can\'t find window "{window_name}" in session "{session_name}"')


@click.command()
@click.argument('session_name', type=click.STRING)
def stop_all(session_name):
    """
    @:param session_name: Name of the tmux session in which the environments are running
    """
    server = libtmux.Server()
    try:
        server.kill_session(session_name)
        print(f'Session "{session_name}" was killed')
    except LibTmuxException:
        print(f'Can\'t find session "{session_name}"')


if __name__ == '__main__':
    venvs.add_command(start)
    venvs.add_command(stop)
    venvs.add_command(stop_all)
    venvs()

