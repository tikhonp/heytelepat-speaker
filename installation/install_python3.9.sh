#!/bin/bash

version="3.9.6"

sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev python3 python3-dev python3-venv python3-pip libffi-dev libtiff-dev autoconf libopenjp2-7 -y

wget -O /tmp/Python-$version.tar.xz https://www.python.org/ftp/python/$version/Python-$version.tar.xz

cd /tmp || exit

tar xf Python-$version.tar.xz

cd Python-$version || exit

./configure --enable-optimizations

sudo make altinstall

sudo apt -y autoremove

sudo rm -rf /tmp/Python-$version

rm /tmp/Python-$version.tar.xz

installed_version=$(python3.9 -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ "$installed_version" == "$version" ]]; then
  echo "Successfully installed python $version"
else
  echo "Failed to install python $version"
fi
