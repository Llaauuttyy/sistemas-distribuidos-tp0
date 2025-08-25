
import logging
from common.ack import MessageACK
from common.bet import MessageBet

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