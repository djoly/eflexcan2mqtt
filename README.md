
# eFlex CAN to MQTT

**DISCLAIMER: This project is in no way affiliated with Fortress Power. It comes with no warrantees or guarantees. Use at your own risk.**

The intent of this project is to develop a means to harvest battery data from the Fortress eFlex batteries. This data can be saved to a timeseries database, such as InfluxDB, for visualization and analysis.

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

## Development and Testing

Volunteers with ready access to Fortress eFlex batteries are welcome to contribute to this project. There are quite a few bytes that I have not been able to decipher.

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
$ sudo ip link set can0 up type can bitrate 250000
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


Sample Regex to parse a can-utils candump log into named timestamp, id, and data parts.


```
\((\d{10}\.\d{6})\)\scan0\s(?<id>\d{2}[0-9A-Z]{1})#(?<b1>[0-9A-Z]{2})(?<b2>[0-9A-Z]{2})(?<b3>[0-9A-Z]{2})(?<b4>[0-9A-Z]{2})(?<b5>[0-9A-Z]{2})(?<b6>[0-9A-Z]{2})(?<b7>[0-9A-Z]{2})(?<b8>[0-9A-Z]{2})
```

And use the groups to create can.Message objects for each message:

```
Message(arbitration_id = 0x\2, timestamp = \1, data = [0x\3,0x\4,0x\5,0x\6,0x\7,0x\8,0x\9,0x\10]),
```

## References and Links

Documentation

- [Python struct](https://docs.python.org/3/library/struct.html)
- [Python-Can](https://python-can.readthedocs.io/en/stable/index.html)

Socketcan Utils and hardware

- [Socketcan compatible hardware](https://elinux.org/CAN_Bus)
- [CAN Utils elinux](http://elinux.org/CAN_Bus)
- [CAN Utils Git](https://github.com/linux-can/can-utils)
- [Waveshare 2-Channel Isolated CAN HAT for Raspberry Pi](https://www.waveshare.com/product/raspberry-pi/hats/2-ch-can-hat.htm)
- [Innomaker USB CAN Analyzer](https://www.inno-maker.com/product/usb2can-cable/)


Fortress Power BMS Software (select eFlex from menu)
- [Fortress BMS Software](https://www.fortresspower.com/firmware/)
- [CAN tool](https://www.amazon.com/Analyzer-Debugger-Compatible-Connect-Standard/dp/B07PHJR3YW)