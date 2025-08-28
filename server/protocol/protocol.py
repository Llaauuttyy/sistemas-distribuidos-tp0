
import logging
from protocol.ack import MessageACK
from protocol.bet import MessageBet
from protocol.chunk import MessageBetChunk
from protocol.chunk_error import MessageChunkError

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
            self._send_exact(ack_message.to_bytes())
        except OSError as e:
            logging.error(f"action: send_ack_message | result: fail | error: {e}")
            raise Exception(f"Could not send ACK message: {e}")
    
    def send_chunk_error_message(self, number):
        """
        Send a Chunk Error message to the connected socket.
        """
        try:
            chunk_error_message = MessageChunkError(number=number)
            self._send_exact(chunk_error_message.to_bytes())
        except OSError as e:
            logging.error(f"action: send_chunk_error_message | result: fail | error: {e}")
            raise Exception(f"Could not send Chunk Error message: {e}")

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
            
            elif message_code == MessageBetChunk.TYPE:
                # Read bets count
                logging.info("LLEGA ACA")
                total_bets_bytes = self._receive_exact(1)
                total_bets = int.from_bytes(total_bets_bytes, byteorder="big")
                
                bets = []
                # TODO: PREGUNTAR: Mejor obtener todos los bytes de una vez y luego ir particionando para crear los bets. Es mejor así o leer de a uno?

                # Read all bets data
                total_bets_bytes = self._receive_exact(total_bets * (1 + MessageBet.PAYLOAD_BYTES))

                # Parse each bet
                bet_start = 1
                bet_end = bet_start + MessageBet.PAYLOAD_BYTES
                for _ in range(total_bets):
                    bet_bytes = total_bets_bytes[bet_start:bet_end]
                    bets.append(MessageBet.from_bytes(bet_bytes))

                    # Move to next bet
                    bet_start = bet_end + 1
                    bet_end = bet_start + MessageBet.PAYLOAD_BYTES
                
                return MessageBetChunk(bets)
            
            else: 
                logging.error(f"action: receive_message | result: fail | error: Unknown message type {message_code}")
                return None

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None