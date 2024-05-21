"""Test eFlex CAN data decode functions"""

from typing import List
from eflexcan2mqtt import decode

def test_parse_arbitration_id():
    """Tests the accuracy of the arbitration_id parser function."""

    assert ("101", "1", "10") == decode.parse_arbitration_id(0x101)
    assert ("10d", "13", "10") == decode.parse_arbitration_id(0x10D)
    assert ("601", "1", "60") == decode.parse_arbitration_id(0x601)
    assert ("604", "4", "60") == decode.parse_arbitration_id(0x604)


def test_parse_serial():
    """Verify the battery serial number is parsed from the CAN message bytes."""

    assert decode.parse_serial([0x22, 0x11, 0x00,
                                0x54, 0x46, 0x27, 0x0F]) == "2211054F9999"
    assert decode.parse_serial([0x22, 0x11, 0x00,
                                0x54, 0x46, 0x03, 0xE7]) == "2211054F0999"
    assert decode.parse_serial([0x22, 0x11, 0x00,
                                0x54, 0x46, 0x00, 0x03]) == "2211054F0003"
    assert decode.parse_serial([0x22, 0x05, 0x00,
                                0x54, 0x45, 0x00, 0x03]) == "2205054E0003"


def test_parse_cell_voltages(data60: List[int]):
    """Validate aggregated CAN message bytes are parsed as expected"""

    cell_voltages = decode.parse_cell_voltages(data60)

    assert 16 == len(cell_voltages)
    assert cell_voltages == [3322, 3322, 3322, 3322, 3322, 3322, 3322, 3322,
                             3322, 3322, 3322 ,3322, 3322, 3322, 3322, 3322]


def test_parse_battery_data(data10: List[int], data60: List[int]):
    """Verifies battery_data_parse function properly parses battery data."""

    battery_data = decode.parse_battery_data(data10, data60)

    expected = {
        'battery_id': "2211075F0964",
        'battery_number': 4, 
        'batteries_in_system': 14,
        'battery_soc': 80,
        'battery_voltage': 53.1,
        'battery_current': -0.5,
        'system_average_voltage': 53.0,
        'pre_volt': 53.3,
        'insulation_resistance': 65535,
        'software_version' : 4006,
        'hardware_version' : "a",
        'lifetime_discharge_energy' : 194037,
        'cell_voltages' : [3322, 3322, 3322, 3322, 3322, 3322, 3322, 3322,
                                3322, 3322, 3322 ,3322, 3322, 3322, 3322, 3322]
    }

    assert battery_data == expected
