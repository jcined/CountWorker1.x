#!/bin/bash

# Update package list and upgrade existing packages
sudo apt-get update

# Check if python3.11 is already installed
version=`python3 --version`
if [[ $version == *"3.11"* ]]; then
    echo "Python 3.11 is already installed."
else
    sudo apt-get remove python3

    sudo apt-get install -y software-properties-common

    # Add the deadsnakes PPA to get access to the latest versions of Python
    sudo add-apt-repository ppa:deadsnakes/ppa

    # Install Python 3.11
    sudo apt-get install -y python3.11 python3.11-dev python3.11-venv

    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
fi

cd /

# Check if pip is installed
if command -v pip3 >/dev/null 2>&1; then
    echo "pip3 already installed"
else
    echo "Installing pip3"
    sudo apt-get install -y python3-pip
fi

# install the libraries
pip3 install flask flask_cors flask_socketio simple-websocket requests psutil aiohttp asyncio lockfile

# Download the zip file
wget https://github.com/jcined/CountWorker1.x/releases/download/v1.1/CountWorker.v1.1.zip

# Unzip the file to the root directory
apt-get install unzip

unzip CountWorker.v1.1.zip -d /

# remove the zip file after unzipping
rm CountWorker.v1.1.zip

cd /countworker

nohup python3 app.py &

sudo ufw disable

sleep 5

python3 sys.py