#!/bin/bash

# Run this script using sudo, or as root, from this directory to install.
# $ cd <path to this directory>
# $ sudo ./install.sh

UPGRADE=0
if [ -f /etc/systemd/system/eflexcan2mqtt.service ]; then UPGRADE=1; fi

if [ $(systemctl is-active eflexcan2mqtt.service) == "active" ]; then
    echo "Stopping existing active eflexcan2mqtt service...";
    systemctl stop eflexcan2mqtt.service;
fi

INSTALL_PATH=/usr/local/bin/eflexcan2mqtt

cp ./eflexcan2mqtt.service /etc/systemd/system

if [ ! -f /etc/eflexcan2mqtt.ini ]; then
    echo "Installing config file at /etc/eflexcan2mqtt.ini...";
    cp ./eflexcan2mqtt.ini /etc;
else
    echo "Found existing config file at /etc/eflexcan2mqtt.ini, will not replace.";
fi

if [ -a $INSTALL_PATH ]; then
    echo "Removing existing files at ${INSTALL_PATH}..." 
    rm -rf ${INSTALL_PATH};
fi

echo "Copying files to ${INSTALL_PATH}..."
cp -r ./eflexcan2mqtt /usr/local/bin/

systemctl enable eflexcan2mqtt.service

if [ $UPGRADE == 1 ]; then
    echo "Starting eflexcan2mqtt service...";
    systemctl start eflexcan2mqtt.service;
else
    echo "Done. Verify the CAN network interface is available and ensure the /etc/eflexcan2mqtt.ini"
    echo "config file settings are correct. Then run 'sudo systemctl start eflexcan2mqtt.service'."
fi

