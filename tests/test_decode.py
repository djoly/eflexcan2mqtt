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

def test_parse_temps(data60: List[int]):
    """Validate temp sensor values are parsed"""

    temps = decode.parse_temps(data60)
    assert 6 == len(temps)
    assert temps == {
        '1': 30,
        '2': 29,
        '3': 28,
        '4': 29,
        '5': 30,
        '6': 32,
    }

def test_parse_alarm_status_normal(data10: List[int]):
    """Verifies non-alarm is parsed as normal status"""
    assert 'Normal' == decode.parse_alarm_status(data10)

def test_parse_alarm_status_1(data10_level1_alarm: List[int]):
    """Verifies alarm level 1 is parsed as alarm status 1"""
    assert '1' == decode.parse_alarm_status(data10_level1_alarm)

def test_parse_charge_make_relay_status_alarm_normal(data10: List[int]):
    """Verifies charge relay status is parsed from 10X data when no fault exists."""
    assert 'Make' == decode.parse_charge_relay_status(data10)

def test_parse_charge_break_relay_status_alarm_level1(data10_level1_alarm: List[int]):
    """Verifies charge relay status is parsed from 10X data when level 1 fault exists."""
    assert 'Break' == decode.parse_charge_relay_status(data10_level1_alarm)

def test_parse_discharge_make_relay_status_alarm_normal(data10: List[int]):
    """Verifies discharge relay status is parsed from 10X data when no fault exists."""
    assert 'Make' == decode.parse_discharge_relay_status(data10)

def test_parse_discharge_break_relay_status_alarm_level1(data10_level1_alarm: List[int]):
    """Verifies discharge relay status is parsed from 10X data when level 1 fault exists."""
    assert 'Break' == decode.parse_charge_relay_status(data10_level1_alarm)

def test_parse_precharge_break_relay_status_alarm_normal(data10: List[int]):
    """Verifies prescharge relay status is parsed from 10X data when no fault exists."""
    assert 'Break' == decode.parse_precharge_relay_status(data10)

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
        'max_cell_voltage': 3320,
        'max_cell_voltage_num': 1,
        'min_cell_voltage': 3319,
        'min_cell_voltage_num': 6,
        'alarm_status': 'Normal',
        'charge_relay_status': 'Make',
        'discharge_relay_status': 'Make',
        'precharge_relay_status': 'Break',
        'system_average_voltage': 53.0,
        'pre_volt': 53.3,
        'insulation_resistance': 65535,
        'software_version' : 4006,
        'hardware_version' : "a",
        'lifetime_discharge_energy' : 194037,
        'cell_voltages' : [3322, 3322, 3322, 3322, 3322, 3322, 3322, 3322,
                                3322, 3322, 3322 ,3322, 3322, 3322, 3322, 3322],
        'temps': {'1': 30, '2': 29,'3': 28,'4': 29,'5': 30,'6': 32}
    }

    assert battery_data == expected
