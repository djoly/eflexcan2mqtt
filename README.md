
# eFlex CAN to MQTT

**DISCLAIMER: This project is in no way affiliated with Fortress Power. It comes with no warrantees or guarantees. Use at your own risk.**

The intent of this project is to provide a means to harvest battery data from the Fortress Power eFlex batteries. This data can be saved to a timeseries database, such as InfluxDB, for visualization and analysis.

Example JSON published to MQTT:

```json
[
    {
        "battery_id": "2299075F9999",
        "battery_number": 1,
        "batteries_in_system": 14,
        "battery_soc": 71,
        "battery_voltage": 53.1,
        "battery_current": -0.3,
        "system_average_voltage": 53.0,
        "pre_volt": 53.3,
        "insulation_resistance": 65535,
        "software_version": 4006,
        "hardware_version": "a",
        "lifetime_discharge_energy": 162810,
        "cell_voltages": [
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319
        ],
        "time": 1715987139
    },
    {
        "battery_id": "2299075E0999",
        "battery_number": 2,
        "batteries_in_system": 14,
        "battery_soc": 69,
        "battery_voltage": 53.1,
        "battery_current": -0.3,
        "system_average_voltage": 53.0,
        "pre_volt": 53.2,
        "insulation_resistance": 65535,
        "software_version": 4006,
        "hardware_version": "a",
        "lifetime_discharge_energy": 144138,
        "cell_voltages": [
            3321,
            3321,
            3320,
            3321,
            3321,
            3321,
            3320,
            3321,
            3321,
            3321,
            3321,
            3321,
            3321,
            3321,
            3321,
            3321
        ],
        "time": 1715987139
    },
    {
        "battery_id": "2245075E0999",
        "battery_number": 3,
        "batteries_in_system": 14,
        "battery_soc": 83,
        "battery_voltage": 53.1,
        "battery_current": -0.3,
        "system_average_voltage": 53.0,
        "pre_volt": 53.1,
        "insulation_resistance": 65535,
        "software_version": 4006,
        "hardware_version": "a",
        "lifetime_discharge_energy": 148249,
        "cell_voltages": [
            3320,
            3319,
            3319,
            3319,
            3320,
            3320,
            3319,
            3319,
            3319,
            3319,
            3319,
            3319,
            3320,
            3319,
            3320,
            3319
        ],
        "time": 1715987139
    }
]
```

## Installing

This application can be installed as a systemd service. Distribution tarballs can be found in the ./dist directory. The tarballs contained
built output from PyInstaller, a eflexcan2mqtt.service file, a eflexcan2mqtt.ini file, and an install.sh shell script to install.

The installer script assumes the following:

1. Systemd configuration path at /etc/systemd/system
2. systemctl available at the command line

Download the distribution for your platform and run the install script.

```bash
$ wget https://github.com/djoly/eflexcan2mqtt/raw/main/dist/eflexcan2mqtt_x86_64.tgz
$ tar -xzf eflexcan2mqtt_x86_64.tgz
$ cd eflexcan2mqtt_x86_64
$ sudo ./install.sh
```

The installer script will copy the python app and dependencies to /usr/local/bin/eflexcan2mqtt.
The eflexcan2mqtt.service file will be copied to /etc/systemd/system/eflexcan2mqtt.service.
The eflexcan2mqtt.ini file will be copied to /etc/eflexcan2mqtt.ini.

Configuration changes can be made to the ini config file.

The installer will enable the eflexcan2mqtt.service, but it will not start the service. Before starting the service, make sure
the CAN interface is up.

You can run the following command to create a can0 interface, assuming socketcan compatible hardware is used.

```bash
$ sudo ip link set can0 up type can bitrate 250000 restart-ms 100
```

Alternately, you can use the networkd service to manage the can interface.

First, add the can0 interface to the network configuration.

```ini
# /etc/systemd/network/80-can0.network
[Match]
Name=can0

[CAN]
BitRate=250K
RestartSec=100ms
```

If the network service is not running, enable and start it:

```bash
$ sudo systemctl enable systemd-networkd
$ sudo systemctl start systemd-networkd
```

If it's already running, restart the service:

```bash
$ sudo systemctl restart systemd-networkd
```

Verify the can0 interface is up:

```bash
$ ifconfig
```

You should see a can0 interface:

```bash
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
RX packets 0  bytes 0 (0.0 B)
RX errors 0  dropped 0  overruns 0  frame 0
TX packets 0  bytes 0 (0.0 B)
TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Use candump to verify the CAN messages are being received:

```bash
$ candump can0
```

You should see CAN arbitration IDs starting with 10 and 60. Each battery in the network will send a set of 11 10X messages and a set of seven 60X messages. The batteries are numbered in the network, and they send the messages in order (at least in my system), from 101 and 601, 102 and 602, to the final battery. If you have more than nine batteries, you will see A for 10, B for 11, etc, as the numbers are in hexadecimal. After the last battery sends its messages, the first will start over again.

Make sure you have the mosquitto MQTT server reachable, and you should be all set to start publishing battery data.


## Development and Testing

Volunteers with ready access to Fortress Power eFlex batteries are welcome to contribute to this project. There are quite a few bytes that have not yet been decoded.

TO-DOs

1. Charge Relay Status (Make/Break or Close/Open)
2. Discharge Relay Status (Make/Break or Close/Open)
3. All warnings and faults
4. Temperature probe values

### Suggested setup

Testing and development is easier with good tooling. Socketcan and can-tools are freely available on Linux. Installing can-tools provides candump, canplayer, and cansniffer utilities to aid in development and testing.

1. Linux computer/server 
2. can-tools installed
3. CAN hardware natively supported by socketcan

To dump real CAN messages, establish a can interface:

```bash
$ sudo ip link set can0 up type can bitrate 250000 restart-ms 100
```

Then use candump to dump the CAN messages to a log file:

```bash
$ candump -L can0 > messages.log
```

These messages can then be replayed to a virtual can channel (e.g. vcan0) on a separate machine with no CAN hardware.

```bash
$ sudo modprobe vcan
$ sudo ip link add dev vcan0 type vcan
$ sudo ip link set vcan0 up
$ canplayer -l i -I messages.log vcan0=can0
```

Run the command line script:

```bash
$ python3 main.py
```

Use mosquitto_sub to receive published battery data.

```bash
$ mosquito_sub -h localhost -p 1883 -t eflexbatteries
```


It is ideal to also have a Windows computer with the Fortress BMS software installed, using the Fortress recommended CAN-tool that is compatible with the BMS software. The BMS software can be used to verify this eflexcan2mqtt is properly decoding the CAN data.

### Running Unit Tests

This project uses poetry for dependencies and pytest.

```bash
$ cd eflexcan2mqtt
$ pytest
```
Tests can also be run from within Visual Studio Code

#### Creating CAN Message Test Fixtures

If more CAN bus test fixtures are required, they can be created using a regex find/replace in a capable text editor.
Here is a sample regex to parse a can-utils candump log into named timestamp, id, and data byte parts in the Xed text editor.

*NOTE: Depending on the regex engine used by your text editor, this regex may need to change.*

Run a search for the regex. This should match every line in the log produced by candump.

```
\((\d{10}\.\d{6})\)\scan0\s(?<id>\d{2}[0-9A-Z]{1})#(?<b1>[0-9A-Z]{2})(?<b2>[0-9A-Z]{2})(?<b3>[0-9A-Z]{2})(?<b4>[0-9A-Z]{2})(?<b5>[0-9A-Z]{2})(?<b6>[0-9A-Z]{2})(?<b7>[0-9A-Z]{2})(?<b8>[0-9A-Z]{2})
```

Then replace the log entries with can.Message objects by using the following replacement:

```
Message(arbitration_id = 0x\2, timestamp = \1, data = [0x\3,0x\4,0x\5,0x\6,0x\7,0x\8,0x\9,0x\10]),
```

*CAUTION: CAN message logs can get big fast! You may want to copy a subset of messages to another file before running a find/replace.*

## References and Links

### Documentation

- [Python struct](https://docs.python.org/3/library/struct.html)
- [Python-Can](https://python-can.readthedocs.io/en/stable/index.html)

### Socketcan Utils and hardware

- [Socketcan compatible hardware](https://elinux.org/CAN_Bus)
- [CAN Utils elinux](http://elinux.org/CAN_Bus)
- [CAN Utils Git](https://github.com/linux-can/can-utils)
- [Waveshare 2-Channel Isolated CAN HAT for Raspberry Pi](https://www.waveshare.com/product/raspberry-pi/hats/2-ch-can-hat.htm)
- [Innomaker USB CAN Analyzer](https://www.inno-maker.com/product/usb2can-cable/)


### Fortress Power BMS Software

The Fortress BMS software can be downloaded by following the link below and selecting "eFlex" from the menu.
The software is for Windows. The firmware update instructions show how to install the BMS software. You don't
need to update the firmware, nor should you unless instructed to by Fortress Power tech support.

- [Fortress BMS Software](https://www.fortresspower.com/firmware/)
- [CAN tool](https://www.amazon.com/Analyzer-Debugger-Compatible-Connect-Standard/dp/B07PHJR3YW)