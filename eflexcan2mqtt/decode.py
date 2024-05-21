"""
Utility methods for the decoding of eFlex battery CAN message data.
"""

import struct
from typing import List

def parse_arbitration_id(arbitration_id: int):
    """Parses the CAN message arbitration id.
    
    The battery number can be reliably determined by the last character of 
    hexidecimal arbitration id.
        - For example, message 0x101 is from battery number 1 (or node id 1).
        0x10D is battery number 13, etc.
        - The battery number or node id is NOT the serial number, which should be
        used as the battery unique id, in case battery order changes. Changing the 
        order of the batteries in the battery network will cause battery numbers to change.
    """
    message_id = hex(arbitration_id)[2:5]
    node_id = str(int(message_id[-1], base=16))
    message_type = message_id[0:2]
    return (message_id, node_id, message_type)

def parse_serial(serial_bytes: List) -> str:
    """Message 101#082211005446270F yields serial number 2211054F9999
    Bytes passed to this function: 2-8. The first byte marks is not to
    be sent to this function.
    Message 8 of 0x10X messages contains the serial number.
        - Byte 2: 22 -> 22
        - Byte 3: 11 -> 11
        - Byte 4: 00 -> 0
        - Byte 5: 54 -> 54
        - Byte 6: char value, 46 -> F
        - Bytes 7-8: parsed as two byte unsigned short/integer and zero filled to a 
        length of four (i.e 270F -> 9999, 03E7 -> 0999)
    """
    parts = struct.unpack(">cH", bytearray(serial_bytes[4:8]))
    return (hex(serial_bytes[0]).removeprefix('0x').zfill(2) 
    + hex(serial_bytes[1]).removeprefix('0x').zfill(2)
    + str(serial_bytes[2])
    + hex(serial_bytes[3]).removeprefix('0x').zfill(2)
    + str(parts[0], "UTF-8")
    + str(parts[1]).zfill(4)
    )


def parse_cell_voltages(data60) -> List[int]:
    """Parses cell voltages from combined data60 messages
    The cell voltage data appears to be little-endian, despite
    most being big-endien.
    """

    return list(struct.unpack('<HHHHHHHHHHHHHHHH', bytearray(data60[0:32])))

def parse_battery_data(data10: List[int], data60: List[int]) -> dict:
    """Processes and formats the battery data from the raw compiled message bytes."""

    battery_number, batteries_in_system, battery_voltage, battery_current, battery_soc = struct.unpack('>BBHhB', bytearray(data10[0:7]))
    average_system_voltage, = struct.unpack(">H", bytearray(data10[10:12]))
    software_version, hardware_version = struct.unpack('>Hc', bytearray(data10[46:49]))
    cell_voltages = parse_cell_voltages(data60)
    pre_volt, insulation_resistance = struct.unpack(">HH", bytearray(data10[35:39]))

    return {
        'battery_id': parse_serial(data10[49:56]),
        'battery_number': battery_number, 
        'batteries_in_system': batteries_in_system,
        'battery_soc': battery_soc,
        'battery_voltage': battery_voltage/10,
        'battery_current': battery_current/10,
        'system_average_voltage': average_system_voltage/10,
        'pre_volt': pre_volt/10,
        'insulation_resistance': insulation_resistance,
        'software_version' : software_version,
        'hardware_version' : str(hardware_version, 'UTF-8'),
        'lifetime_discharge_energy' : struct.unpack('>I', bytearray(data10[31:35]))[0],
        'cell_voltages' : cell_voltages
    }