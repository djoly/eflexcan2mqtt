import pytest
import logging
from typing import List
from can import Message
from eflexcan2mqtt.message_handler import MessageHandler

@pytest.fixture
def can_messages():
    """Dummy test messages. Generated from actual candump log. Serial bytes have been
    modified to hide actual serial numbers. The messages start and end with a partial
    group of messages so message handling logic can be verified to correctly aggregate
    and compile message data.
    """
    return [
        Message(arbitration_id = 0x101, timestamp = 1715987138.038647, data = [0x08,0x22,0x11,0x00,0x75,0x46,0x03,0xBB]),
        Message(arbitration_id = 0x101, timestamp = 1715987138.039210, data = [0x09,0x13,0x95,0xBA,0xEE,0x00,0x00,0x01]),
        Message(arbitration_id = 0x101, timestamp = 1715987138.039687, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x15]),
        Message(arbitration_id = 0x101, timestamp = 1715987138.042916, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.043252, data = [0x01,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.043804, data = [0x02,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.044287, data = [0x03,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.044657, data = [0x04,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.045220, data = [0x05,0xF7,0x0C,0xF7,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.045599, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x601, timestamp = 1715987138.046102, data = [0x11,0x41,0x40,0x3F,0x40,0x43,0x43,0x00]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.048410, data = [0x01,0x02,0x0E,0x02,0x13,0xFF,0xFD,0x45]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.048683, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.049224, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.049644, data = [0x04,0x0C,0xF9,0x01,0x0C,0xF9,0x01,0x64]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.050101, data = [0x05,0x43,0x40,0x26,0x00,0x02,0x33,0x0A]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.050677, data = [0x06,0x02,0x14,0xFF,0xFF,0x00,0x00,0x18]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.051174, data = [0x07,0x00,0x00,0x00,0x00,0x0F,0xA6,0x61]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.051659, data = [0x08,0x22,0x05,0x00,0x75,0x45,0x02,0x5C]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.052034, data = [0x09,0x12,0xAF,0x9B,0x12,0x00,0x00,0x01]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.052618, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x14]),
        Message(arbitration_id = 0x102, timestamp = 1715987138.053098, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.053541, data = [0x01,0xF9,0x0C,0xF9,0x0C,0xF8,0x0C,0xF9]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.053954, data = [0x02,0x0C,0xF9,0x0C,0xF9,0x0C,0xF8,0x0C]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.054489, data = [0x03,0xF9,0x0C,0xF9,0x0C,0xF9,0x0C,0xF9]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.054988, data = [0x04,0x0C,0xF9,0x0C,0xF9,0x0C,0xF9,0x0C]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.055466, data = [0x05,0xF9,0x0C,0xF9,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.055886, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x602, timestamp = 1715987138.056385, data = [0x11,0x41,0x40,0x40,0x40,0x41,0x44,0x00]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.068490, data = [0x01,0x03,0x0E,0x02,0x13,0xFF,0xFD,0x53]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.068723, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.069305, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.069682, data = [0x04,0x0C,0xF8,0x01,0x0C,0xF7,0x02,0x64]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.070137, data = [0x05,0x49,0x45,0x26,0x00,0x02,0x43,0x19]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.070724, data = [0x06,0x02,0x13,0xFF,0xFF,0x00,0x00,0x1E]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.071201, data = [0x07,0x00,0x00,0x00,0x00,0x0F,0xA6,0x61]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.071681, data = [0x08,0x22,0x05,0x00,0x75,0x45,0x00,0x70]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.072156, data = [0x09,0x14,0x93,0xFB,0x87,0x00,0x00,0x01]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.072634, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x14]),
        Message(arbitration_id = 0x103, timestamp = 1715987138.073120, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.073540, data = [0x01,0xF8,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.074023, data = [0x02,0x0C,0xF8,0x0C,0xF8,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.074476, data = [0x03,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.074954, data = [0x04,0x0C,0xF7,0x0C,0xF8,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.075505, data = [0x05,0xF8,0x0C,0xF7,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.075991, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x603, timestamp = 1715987138.076465, data = [0x11,0x47,0x45,0x45,0x45,0x46,0x49,0x00]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.048187, data = [0x01,0x01,0x0E,0x02,0x13,0xFF,0xFD,0x47]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.048532, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.049075, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.049539, data = [0x04,0x0C,0xF7,0x01,0x0C,0xF7,0x01,0x64]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.049982, data = [0x05,0x43,0x3F,0x35,0x00,0x02,0x7B,0xFA]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.050561, data = [0x06,0x02,0x15,0xFF,0xFF,0x00,0x00,0x19]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.051026, data = [0x07,0x00,0x00,0x00,0x00,0x0F,0xA6,0x61]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.051493, data = [0x08,0x22,0x11,0x00,0x75,0x46,0x03,0xBB]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.051970, data = [0x09,0x13,0x95,0xBA,0xEE,0x00,0x00,0x01]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.052414, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x15]),
        Message(arbitration_id = 0x101, timestamp = 1715987139.052901, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.053366, data = [0x01,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.053807, data = [0x02,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.054256, data = [0x03,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.054838, data = [0x04,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.055208, data = [0x05,0xF7,0x0C,0xF7,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.055707, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x601, timestamp = 1715987139.056208, data = [0x11,0x41,0x40,0x3F,0x40,0x43,0x43,0x00]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.061290, data = [0x01,0x02,0x0E,0x02,0x13,0xFF,0xFD,0x45]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.061584, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.062039, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.062504, data = [0x04,0x0C,0xF9,0x01,0x0C,0xF8,0x03,0x64]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.062983, data = [0x05,0x43,0x40,0x26,0x00,0x02,0x33,0x0A]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.063445, data = [0x06,0x02,0x14,0xFF,0xFF,0x00,0x00,0x18]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.064023, data = [0x07,0x00,0x00,0x00,0x00,0x0F,0xA6,0x61]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.064477, data = [0x08,0x22,0x05,0x00,0x75,0x45,0x02,0x5C]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.064961, data = [0x09,0x12,0xAF,0x9B,0x12,0x00,0x00,0x01]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.065425, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x14]),
        Message(arbitration_id = 0x102, timestamp = 1715987139.065888, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.066338, data = [0x01,0xF9,0x0C,0xF9,0x0C,0xF8,0x0C,0xF9]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.066927, data = [0x02,0x0C,0xF9,0x0C,0xF9,0x0C,0xF8,0x0C]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.067379, data = [0x03,0xF9,0x0C,0xF9,0x0C,0xF9,0x0C,0xF9]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.067830, data = [0x04,0x0C,0xF9,0x0C,0xF9,0x0C,0xF9,0x0C]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.068325, data = [0x05,0xF9,0x0C,0xF9,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.068823, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x602, timestamp = 1715987139.069323, data = [0x11,0x41,0x40,0x40,0x40,0x41,0x43,0x00]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.081321, data = [0x01,0x03,0x0E,0x02,0x13,0xFF,0xFD,0x53]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.081522, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.082070, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.082654, data = [0x04,0x0C,0xF8,0x01,0x0C,0xF7,0x02,0x64]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.083098, data = [0x05,0x49,0x45,0x26,0x00,0x02,0x43,0x19]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.083558, data = [0x06,0x02,0x13,0xFF,0xFF,0x00,0x00,0x1E]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.084076, data = [0x07,0x00,0x00,0x00,0x00,0x0F,0xA6,0x61]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.084526, data = [0x08,0x22,0x05,0x00,0x75,0x45,0x00,0x70]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.085018, data = [0x09,0x14,0x93,0xFB,0x87,0x00,0x00,0x01]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.085415, data = [0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x14]),
        Message(arbitration_id = 0x103, timestamp = 1715987139.085904, data = [0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x01]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.086371, data = [0x01,0xF8,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.086858, data = [0x02,0x0C,0xF8,0x0C,0xF8,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.087389, data = [0x03,0xF7,0x0C,0xF7,0x0C,0xF7,0x0C,0xF7]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.087870, data = [0x04,0x0C,0xF7,0x0C,0xF8,0x0C,0xF7,0x0C]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.088367, data = [0x05,0xF8,0x0C,0xF7,0x0C,0x00,0x00,0x00]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.088750, data = [0x06,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
        Message(arbitration_id = 0x603, timestamp = 1715987139.089255, data = [0x11,0x47,0x45,0x45,0x45,0x46,0x49,0x00]),
        Message(arbitration_id = 0x101, timestamp = 1715987140.060603, data = [0x02,0x03,0x00,0x00,0x02,0x12,0x01,0x01]),
        Message(arbitration_id = 0x101, timestamp = 1715987140.061063, data = [0x03,0x01,0xF4,0x02,0x58,0x00,0x01,0x2A]),
        Message(arbitration_id = 0x101, timestamp = 1715987140.061676, data = [0x04,0x0C,0xF7,0x01,0x0C,0xF7,0x01,0x64]),
    ]

@pytest.fixture
def message_handler(can_messages) -> MessageHandler:
    logger = logging.Logger(__name__)
    message_handler = MessageHandler(logger)
    for msg in can_messages:
        message_handler.on_message_received(msg)
    return message_handler

@pytest.fixture
def data10() -> List[int]:
    """Represents the compiled, aggregated bytes from a set of 10X messages."""
    return [
        0x04,0x0E,0x02,0x13,0xFF,0xFB,0x50,
        0x03,0x00,0x00,0x02,0x12,0x01,0x01,
        0x01,0xF4,0x02,0x58,0x00,0x01,0x2A,
        0x0C,0xF8,0x01,0x0C,0xF7,0x06,0x64,
        0x49,0x45,0x25,0x00,0x02,0xF5,0xF5,
        0x02,0x15,0xFF,0xFF,0x00,0x00,0x1E,
        0x00,0x00,0x00,0x00,0x0F,0xA6,0x61,
        0x22,0x11,0x00,0x75,0x46,0x03,0xC4,
        0x13,0x8E,0x3A,0xF7,0x00,0x00,0x01,
        0x00,0x00,0x00,0x00,0x00,0x02,0x16,
        0x00,0x00,0x00,0x00,0x00,0x00,0x01,
    ]

@pytest.fixture
def data60():
    """Represents the compiled, aggregated bytes from a set of 60X messages."""
    return [
        0xFA, 0x0C, 0xFA, 0x0C, 0xFA, 0x0C, 0xFA,
        0x0C, 0xFA, 0x0C, 0xFA, 0x0C, 0xFA, 0x0C,
        0xFA, 0x0C, 0xFA, 0x0C, 0xFA, 0x0C, 0xFA,
        0x0C, 0xFA, 0x0C, 0xFA, 0x0C, 0xFA, 0x0C,
        0xFA, 0x0C, 0xFA, 0x0C, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x46, 0x45, 0x44, 0x45, 0x46, 0x48, 0x00,
    ]
