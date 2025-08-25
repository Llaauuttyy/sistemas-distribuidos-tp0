
import logging
from common.utils import Bet

class Message:
    def __init__(self, message_type: int):
        self.message_type = message_type

class MessageACK(Message):
    TYPE = 1
    FIELD_SIZES = {
        "number": 8,
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())
    
    def __init__(self, number: str):
        super().__init__(self.TYPE)
        self.number = int(number)

    def to_bytes(self):
        """
        Serialize MessageACK to bytes.
        """
        data = self.message_type.to_bytes(1, byteorder="big")
        data +=  self.number.to_bytes(self.FIELD_SIZES["number"], byteorder="big")

        return data

class MessageBet(Message):
    TYPE = 2
    FIELD_SIZES = {
        "agency": 20,
        "first_name": 30,
        "last_name": 15,
        "document": 8,
        "birthdate": 10,
        "number": 8,
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())

    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        super().__init__(self.TYPE)
        self.agency = agency
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = birthdate
        self.number = number

    def __str__(self):
        return f"MessageBet(agency={self.agency}, first_name={self.first_name}, " \
               f"last_name={self.last_name}, document={self.document}, " \
               f"birthdate={self.birthdate}, number={self.number})"
    
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
            fields[key] = raw.decode("utf-8").rstrip("\x00")
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

    def _send_exact(self, bytes: bytes):
        # Avoid short-writes: sendall method tries to send all data, and fails if it cannot.
        self.socket.sendall(bytes + b'\n')

    def _receive_exact(self, size: int) -> bytes:
        """
        Receive exactly `size` bytes from the socket.
        """
        # Avoid short-reads: read until it has the exact number of bytes or returns exception.
        data = bytearray()
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                raise OSError("Connection closed or could not read exact bytes")
            data.extend(chunk)
        return bytes(data)
    
    def send_ack_message(self, number):
        """
        Send an ACK message to the connected socket.
        """
        try:
            ack_message = MessageACK(number=number)
            # logging.info(f"MANDANDO ACK MESSAGE DE TAMANIO: {len(ack_message.to_bytes())}")
            self._send_exact(ack_message.to_bytes())
        except OSError as e:
            logging.error(f"action: send_ack_message | result: fail | error: {e}")
            raise Exception(f"Could not send ACK message: {e}")
    
    def receive_message(self):
        """
        Receive a message from the connected socket.
        """
        try:
            # Read message typr code
            message_code_byte = self._receive_exact(1)
            message_code = int.from_bytes(message_code_byte, byteorder="big")

            if message_code == MessageBet.TYPE:
                # Read the full message size
                message_size = MessageBet.PAYLOAD_BYTES
                message_data = self._receive_exact(message_size)
                return MessageBet.from_bytes(message_data)
            
            else: 
                logging.error(f"action: receive_message | result: fail | error: Unknown message type {message_code}")
                return None

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None