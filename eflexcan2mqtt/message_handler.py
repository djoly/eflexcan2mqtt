"""
Handles CAN messages as they are received from the eFlex batteries
"""
from typing import List
from logging import Logger
from can.listener import Listener
from can.message import Message
from .decode import parse_arbitration_id

# 0x10X messages are sent by each battery, 11 messages in a row.
MSG_ID_10X_COUNT = 11

# 0x60X messages are sent by each battery, 7 messages in a row.
MSG_ID_60X_COUNT = 7

MSG_TYPE_10 = '10'
MSG_TYPE_60 = '60'

Message.__lt__ = lambda self, other: self.data[0] < other.data[0]

class MessageHandler(Listener):
    """The is an implementation of can.listener.Listener. It is registered
with the can.Notifier class in the implementing code.

Messages are handled by the on_message_received method, where they are aggregated
for later decoding and publishing.
"""
    _logger: Logger

    # Contains the relevant bytes from the most recently aggregated messages.
    # The keys are the arbitration id (i.e. 0x101, 0x601, etc)
    _compiled_message10X_data: dict[str, List[int]] = {}
    _compiled_message60X_data: dict[str, List[int]] = {}

    # Contains lists for each 0x10X and 0x60X messages. The message data is compiled and saved to
    # the compiled_message_data map when complete and the aggregation list cleared.
    _aggregated_messages: dict[str, Message] = {}

    #Timestamp of last aggregated messages. Key is the node_id or battery number.
    _timestamps: dict[str, float] = {}

    def __init__(self, logger: Logger):
        self._logger = logger

    def on_message_received(self, msg: Message) -> None:
        """CAN Notifier callback listener. Handles messages, aggregates and compiles
        the data when all are received into a single array of bytes for processing.
        """

        message_id, node_id, message_type = parse_arbitration_id(msg.arbitration_id)

        # If this is not a 10X or 60X message, ignore it.
        if message_type not in (MSG_TYPE_10, MSG_TYPE_60):
            return

        # Initialize a list for this message id if it's the first message.
        if msg.data[0] == 0x01:
            self._aggregated_messages[message_id] = []
            
        # If this is not the first message, and the aggregated list does not exist,
        # ignore this message. This can happen on startup of the script. For example,
        # message 101#08 may be the first message to be received. In this case,
        # we want to wait for the message 101#01 before aggregating this message.
        elif message_id not in self._aggregated_messages.keys():
            return
        
        self._aggregated_messages[message_id].append(msg)

        message_count = len(self._aggregated_messages[message_id])

        if (message_type == MSG_TYPE_10 and message_count == MSG_ID_10X_COUNT
            or message_type == MSG_TYPE_60 and message_count == MSG_ID_60X_COUNT
            ):

            # Ensure messages are sorted by the first data byte
            sorted_messages: List[Message] = sorted(self._aggregated_messages[message_id])
            compiled_data = []

            # Compile data bytes into single list and update compiled message data for the node id.
            for message in sorted_messages:
                compiled_data += message.data[1:8]

            # TODO: validate first bytes to ensure each message is there
            if message_type == MSG_TYPE_10:
                self._compiled_message10X_data[node_id] = compiled_data

            if message_type == MSG_TYPE_60:
                self._compiled_message60X_data[node_id] = compiled_data
                self._timestamps[node_id] = msg.timestamp

            # Reset aggregated message list to empty
            self._aggregated_messages[message_id] = []

        return

    def on_error(self, exc: Exception) -> None:
        self._logger.error(msg = "MessageHandler encountered an exception.", exc_info = exc)

    @property
    def compiled_message10X_data(self):
        return self._compiled_message10X_data
    
    @property
    def compiled_message60X_data(self):
        return self._compiled_message60X_data
    
    @property
    def timestamps(self):
        return self._timestamps
