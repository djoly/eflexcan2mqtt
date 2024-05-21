import logging
from .mock_mqtt_client import MockMQTTClient
from eflexcan2mqtt.mqtt_publisher import MQTTPublisher
from eflexcan2mqtt.message_handler import MessageHandler

logger = logging.getLogger(__name__)

def test_publish_data(message_handler: MessageHandler):
    mqtt_client = MockMQTTClient()

    publisher = MQTTPublisher(logger = logger, message_handler = message_handler, mqtt_client = mqtt_client)
    publisher.publish_data()

    assert EXPECTED_PAYLOAD == mqtt_client.payload


EXPECTED_PAYLOAD = [
    {
        "battery_id": "2205075E0604",
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
        "cell_voltages": [3321, 3321, 3320, 3321, 3321, 3321, 3320, 3321, 3321, 3321, 3321, 3321, 3321, 3321, 3321, 3321],
        "time": 1715987139
    },
    {
        "battery_id": "2205075E0112",
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
        "cell_voltages": [3320, 3319, 3319, 3319, 3320, 3320, 3319, 3319, 3319, 3319, 3319, 3319, 3320, 3319, 3320, 3319],
        "time": 1715987139
    },
    {
        "battery_id": "2211075F0955", 
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
        "cell_voltages": [3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319, 3319], 
        "time": 1715987139
    }
]
