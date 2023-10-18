#!/bin/bash
# install.sh

echo "Installing tmux and python3-venv"

apt-get update
apt-get -y updrade
apt-get install -y python3-venv python3-pip tmux

echo "Installing the dependencies in new Python environment"

python3 -m venv .venv && source .venv/bin/activate
pip3 install --upgrade pip
pip3 install libtmux
pip3 install click
pip3 install tqdm

echo "Done"

exit 0
