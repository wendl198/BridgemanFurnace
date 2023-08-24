#!/usr/bin/bash
sudo apt-get install python3.9
sudo apt-get install git
sudo apt-get install python3-pip
sudo apt-get install tmux
sudo pip install Phidget22
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&sudo apt-get install -y libphidget22
git clone https://github.com/wendl198/BridgemanFurnace/
