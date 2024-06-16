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

# Expected order of first bytes. Only the first six messages of 60X message types are
# tested due to the typically observed value of the 7th message being 0x11, which
# is not known.
MSG_10X_FIRST_BYTE_ORDER = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B]
MSG_60X_FIRST_BYTE_ORDER = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

MSG_TYPE_10 = '10'
MSG_TYPE_60 = '60'

Message.__lt__ = lambda self, other: self.data[0] < other.data[0]


def _all_messages_received(message_type: int, aggregated_messages: dict[str, List[Message]]) -> bool:

    """Checks the provided aggregated messages to verify they are present.
    The first byte of all 11 10X messages are checked to confirm each message
    is present and they are in the expected order.
    The first six of the 60X messages are checked. The first byte of the 7th
    60X message is ignored, as it does not follow the convention of the other messages.
    """

    message_count = len(aggregated_messages)

    if (message_type == MSG_TYPE_10):
        if (message_count != MSG_ID_10X_COUNT):
            return False
        
        for i, msg in enumerate(aggregated_messages):
            if msg.data[0] != MSG_10X_FIRST_BYTE_ORDER[i]:
                return False
        return True
    
    elif (message_type == MSG_TYPE_60):
        if (message_count != MSG_ID_60X_COUNT):
            return False
        
        for i, msg in enumerate(aggregated_messages):
            if i < MSG_ID_60X_COUNT - 1:
                if msg.data[0] != MSG_60X_FIRST_BYTE_ORDER[i]:
                    return False
        return True
    else:
        raise ValueError("The argument message_type expected to either be %s or %s", MSG_TYPE_10, MSG_TYPE_60)

class MessageHandler(Listener):
    """The is an implementation of can.listener.Listener. It is registered
with the can.Notifier class in the implementing code.

Messages are handled by the on_message_received method, where they are aggregated
for later decoding and publishing.
"""
    _logger: Logger

    # Contains the relevant bytes from the most recently aggregated messages.
    # The keys are the node ids (i.e. 1, 2, 5, 13 etc)
    _compiled_message10X_data: dict[str, List[int]] = {}
    _compiled_message60X_data: dict[str, List[int]] = {}

    # Contains lists for each 0x10X and 0x60X messages. The message data is compiled and saved to
    # the compiled_message_data map when complete and the aggregation list cleared.
    _aggregated_messages: dict[str, List[Message]] = {}

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
        # we want to wait for the message 101#01 before we start aggregating this message.
        elif message_id not in self._aggregated_messages.keys():
            return
        
        self._aggregated_messages[message_id].append(msg)

        # If all the messages of this type have been received from this battery/node,
        # aggregate the data bytes.
        if _all_messages_received(message_type, self._aggregated_messages[message_id]):
            compiled_data = []

            # Compile data bytes into single list and update compiled message data for the node id.
            for message in self._aggregated_messages[message_id]:
                compiled_data += message.data[1:8]

            if message_type == MSG_TYPE_10:
                self._compiled_message10X_data[node_id] = compiled_data

            if message_type == MSG_TYPE_60:
                self._compiled_message60X_data[node_id] = compiled_data
                # Since the 60X messages are the last messages to be received by a node/battery
                # we will use the last message timestamp to mark the time the data was
                # collected.
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
