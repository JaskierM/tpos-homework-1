#!/bin/bash
# install.sh

echo "Installing the dependencies in current Python environment"

pip3 install libtmux
pip3 install click
pip3 install tqdm

echo "Done"

exit 0
