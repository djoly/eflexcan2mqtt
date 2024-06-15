#!/bin/bash

# Run this script using sudo, or as root, from this directory to install.
# $ cd <path to this directory>
# $ sudo ./install.sh

cp ./eflexcan2mqtt.service /etc/systemd/system
cp ./eflexcan2mqtt.ini /etc
cp -r ./eflexcan2mqtt /usr/local/bin/

systemctl enable eflexcan2mqtt
