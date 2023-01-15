#!/bin/bash

# Update the package list
sudo apt-get update

# Check if python3.11 is already installed
version=`python3 --version`
if [[ $version == *"3.11"* ]]; then
    echo "Python 3.11 is already installed."
else
    # Install dependencies
    sudo apt-get install -y build-essential checkinstall
    sudo apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

    # Download and extract Python 3.11 source code
    wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
    tar -xvf Python-3.11.0.tgz

    # Enter the extracted folder
    cd Python-3.11.0

    # Configure and make
    ./configure
    make

    # Install
    sudo checkinstall

# Update alternatives
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3 1

# Check the version
python3 --version

cd /

# Check if pip is installed
if command -v pip3 >/dev/null 2>&1; then
    echo "pip3 already installed"
else
    echo "Installing pip3"
    sudo apt-get install -y python3-pip
fi

# install the libraries
pip3 install flask flask_cors flask_socketio psutil aiohttp asyncio lockfile

# Download the zip file
wget https://github.com/jcined/CountWorker1.x/releases/download/v1.1/CountWorker.v1.1.zip

# Unzip the file to the root directory
unzip file.zip -d /

# remove the zip file after unzipping
rm file.zip

cd /countworker

nohup python3 app.py &

sleep 5

python3 sys.py

