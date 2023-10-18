#!/bin/bash
# install.sh

echo "Installing tmux and python3-venv"

apt-get update
apt-get -y updrade
apt-get install -y python3-venv python3-pip tmux

echo "Installing the dependencies in new Python environment"

python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install libtmux
python3 -m install click
python3 -m install tqdm

echo "Done"

exit 0
