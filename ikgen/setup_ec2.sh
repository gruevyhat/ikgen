#!/bin/sh

sudo apt-get update
sudo apt-get install build-essential gfortran gcc g++ python-dev git python-pip
sudo pip install bottle docopt numpy pandas

git clone https://github.com/gruevyhat/ikgen.git
