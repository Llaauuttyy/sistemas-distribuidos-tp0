
import logging
from server.common.utils import Bet

class Message:
    def __init__(self, message_type: int):
        self.message_type = message_type

class MessageACK(Message):
    TOTAL_BYTES = 1
    
    def __init__(self):
        super().__init__(1)

    def to_bytes(self):
        """
        Serialize MessageACK to bytes.
        """
        return self.message_type.to_bytes()

class MessageBet(Message):
    FIELD_SIZES = {
        "agency": 20,
        "first_name": 20,
        "last_name": 20,
        "document": 8,
        "birthdate": 10,
        "number": 8,
    }

    TOTAL_BYTES = sum(FIELD_SIZES.values())

    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        super().__init__(2)
        self.bet = Bet(agency, first_name, last_name, document, birthdate, number)

    @staticmethod
    def from_bytes(data: bytes) -> "MessageBet":
        """
        Deserialize bytes to MessageBet object.
        """
        sizes = MessageBet.FIELD_SIZES
        offset = 0
        fields = {}
        for key, size in sizes.items():
            raw = data[offset:offset+size]
            fields[key] = raw.decode("utf-8").strip()
            offset += size

        return MessageBet(
            fields["agency"],
            fields["first_name"],
            fields["last_name"],
            fields["document"],
            fields["birthdate"],
            fields["number"]
        )


class CommunicationProtocol:
    def __init__(self, socket):
        self.socket = socket

    def send_message(self, message: Message):
        """
        Send a message to the connected socket.
        """
        try:
            # Avoid short-writes: sendall method tries to send all data, and fails if it cannot.
            self.socket.sendall(message + b'\n')
        except OSError as e:
            logging.error(f"action: send_message | result: fail | error: {e}")

    def receive_message(self):
        """
        Receive a message from the connected socket.
        """
        try:
            data = self.socket.recv(1024).rstrip()
            if not data:
                return None
            return data.decode('utf-8')
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None