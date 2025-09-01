import socket
import logging
import signal

from protocol.protocol import CommunicationProtocol
from protocol.chunk import MessageBetChunk
from protocol.get_winners import MessageGetWinners
from common.utils import store_bets, load_bets, has_won
from common.utils import Bet

from multiprocessing import Process, Lock, Manager

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._server_socket.settimeout(0.5)
        # self._client_socket = None
        
        self._running = True

        self._manager = Manager()
        self._active_agencies = self._manager.list()

        # Shared value to indicate if the lottery has finished
        self._lottery_finished = self._manager.Value('b', False)
        self._winners_by_agency = self._manager.dict()

        self._handle_bets = Lock()
        self._handle_agencies = Lock()
        self._childs = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            client_socket = self.__accept_new_connection()
            if client_socket:
                # self.__handle_client_connection(self._client_socket)
                new_child_process = Process(target=self.__handle_client_connection, args=(client_socket,))
                new_child_process.start()

                self._childs.append(new_child_process)

        self._terminate()

    def __handle_store_bets(self, communicator: CommunicationProtocol, bets: list[Bet]):
        with self._handle_bets:
            try:
                store_bets(bets)
            except Exception as e:
                logging.error(f'action: apuesta_recibida | result: fail | cantidad: {len(bets)}')
                
                # Send Chunk Error message to the client
                communicator.send_chunk_error_message(bets[0].number)
                
                raise Exception("Could not store bets.")

    def __add_if_new_active_agency(self, agency: str):
        with self._handle_agencies:
            if agency not in self._active_agencies:
                self._active_agencies.append(agency)
                logging.info(f"action: new_active_agency | result: success | agency: {agency}")

            logging.info(f"action: total_active_agencies | result: success | agencies: {self._active_agencies}")

    def __handle_lottery(self):
        with self._handle_bets:
            bets_stored = load_bets()

            for bet in bets_stored:
                if bet.agency not in self._winners_by_agency:
                    self._winners_by_agency[bet.agency] = self._manager.list()
                
                if has_won(bet):
                    # logging.info(f"action: WINNER | result: success | agency: {bet.agency} | document: {bet.document} | number: {bet.number}")
                    self._winners_by_agency[bet.agency].append(bet.document)
            
            # logging.info(f"action: lottery_handled | result: success | winners_by_agency: {dict(self._winners_by_agency)}")

    def __set_agency_as_finished(self, agency: str):
        lottery = False
        with self._handle_agencies:
            self._active_agencies.remove(agency)
            logging.info(f"action: agency_finished | result: success | agency: {agency}")

            if not self._active_agencies:
                # Avoid lock annidation.
                lottery = True

        if lottery:
            self.__handle_lottery()

            # Lottery has finished, so agencies can request winners
            self._lottery_finished.value = True
            logging.info("action: sorteo | result: success")

    def __get_winners(self, agency: str) -> list[str]:
        agency = int(agency)
        if agency not in self._winners_by_agency.keys():
            raise Exception("Agency has not sent any bets.")
        
        winners = []
        for winner in self._winners_by_agency[agency]:
            winners.append(winner)

        return winners

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        # Create communication protocol instance
        communicator = CommunicationProtocol(client_sock)

        try:
            # Get bet from the client
            message = communicator.receive_message()

            if message.message_type == MessageBetChunk.TYPE: 
                bet_chunk_message = message
                if bet_chunk_message is None:
                    raise Exception("Could not read message chunk.")
                
                # Track active agencies
                self.__add_if_new_active_agency(bet_chunk_message.agency)

                ack_number = bet_chunk_message.bets[0].number if bet_chunk_message.bets else 0
                
                if not bet_chunk_message.bets:
                    # No bets in chunk means agency is done sending bets.
                    self.__set_agency_as_finished(bet_chunk_message.agency)

                else:
                    bets = []
                    for bet in bet_chunk_message.bets:
                        # logging.info(f'action: bet_received | result: success | ip: {addr[0]} | bet: {bet}')
                        bets.append(Bet(bet.agency, bet.first_name, bet.last_name, bet.document, bet.birthdate, bet.number))

                    self.__handle_store_bets(communicator, bets)

                    # Mixed languages in log to not modify tests.
                    logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bet_chunk_message.bets)}')
                    
                # Send ACK to the client
                communicator.send_ack_message(ack_number)
            
            elif message.message_type == MessageGetWinners.TYPE:
                if self._lottery_finished.value:
                    winners = self.__get_winners(message.agency)

                    communicator.send_winners_message(winners)
                else:
                    communicator.send_winners_message(no_lottery_yet=True)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | error: Exception: {e}")
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
        self._server_socket.close()
        logging.info("action: close_server_socket | result: success")

        for child in self._childs:
            if child.is_alive():
                child.join()
            logging.info(f"action: child_process_terminated | result: success | pid: {child.pid}")
        
        logging.info("action: graceful_shutdown | result: success")
