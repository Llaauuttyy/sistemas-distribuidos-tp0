import socket
import logging
import signal

from protocol.protocol import CommunicationProtocol
from common.utils import store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._server_socket.settimeout(0.5)
        self._client_socket = None
        self._running = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            self._client_socket = self.__accept_new_connection()
            if self._client_socket:
                self.__handle_client_connection(self._client_socket)

        self._terminate()

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        # Create communication protocol instance
        communicator = CommunicationProtocol(client_sock)

        try:
            addr = client_sock.getpeername()

            # Get bet from the client
            bet_message = communicator.receive_message()
            if bet_message is None:
                raise Exception("Could not read message.")
            # logging.info(f'action: bet_received | result: success | ip: {addr[0]} | bet: {bet_message}')

            store_bets([bet_message])
            # Mixed languages in log to not modify tests.
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet_message.document} | numero: {bet_message.number}')

            # Send ACK to the client
            communicator.send_ack_message(bet_message.number)
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except socket.timeout:
            return None
    
    def _graceful_shutdown(self, _signum, _frame):
        logging.info("action: graceful_shutdown | result: in_progress")
        self._running = False

    def _terminate(self):
        if self._client_socket:
            logging.info("action: close_client_socket | result: in_progress")
            self._client_socket.close()
            logging.info("action: close_client_socket | result: success")

        self._server_socket.close()
        logging.info("action: close_server_socket | result: success")
        logging.info("action: graceful_shutdown | result: success")
