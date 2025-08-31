import socket
import logging
import signal

from protocol.protocol import CommunicationProtocol
from common.utils import store_bets, load_bets, has_won
from common.utils import Bet

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
        self._active_agencies = set()
        self._lottery_finished = False

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

    def __handle_store_bets(self, communicator: CommunicationProtocol, bets: list[Bet]):
        try:
            store_bets(bets)
        except Exception as e:
            logging.error(f'action: apuesta_recibida | result: fail | cantidad: {len(bets)}')
            
            # Send Chunk Error message to the client
            communicator.send_chunk_error_message(bets[0].number)
            
            raise Exception("Could not store bets.")

    # TODO: Ej7 notes -------------------------------------------------------------------------------------------------
    # - Que el mensaje de Chunk tenga un param is_last_chunk y en caso de serlo
    # el server ya sabe que esa agencia ya terminó de mandar apuestas, 
    # manda ACK normal y anota que esa agencia ya terminó. O mejor mando totalBets en 0 y con eso determino que terminó!!!.
    # - En ese momento el Cliente recibe el ACK y empieza un loop enviando mensaje para
    # consultar ganadores y si el servidor lo recibe y faltan agencias por terminar,
    # responde con un winner in progress o algo así para que el cliente espere y vuelva a consultar.
    # - El Chunk también debería tener el ID del agencia, así el server puede
    # identificar qué agencias ya terminaron de mandar apuestas en un array/dict.
    # - Recordar no editar el utils.py. En caso de crear funciones creo un nuevo utils.py o lo hago acá.
    # - El mensaje de obtener Winners puede tener un flag de obtener ganadores o consultar ganadores. Para no tener 2 mensajes diferentes.
    # ------------------------------------------------------------------------------------------------------------------

    def __add_if_new_active_agency(self, agency: str):
        if agency not in self._active_agencies:
            self._active_agencies.add(agency)
            logging.info(f"action: new_active_agency | result: success | agency: {agency}")

        logging.info(f"action: total_active_agencies | result: success | agencies: {self._active_agencies}")

    def __set_agency_as_finished(self, agency: str):
        self._active_agencies.remove(agency)
        logging.info(f"action: agency_finished | result: success | agency: {agency}")

        if not self._active_agencies:
            self._lottery_finished = True
            logging.info("action: sorteo | result: success")

    def __get_winners(self, agency: str) -> list[str]:
        bets_stored = load_bets()

        winners = []

        for bet in bets_stored:
            if has_won(bet) and bet.agency == int(agency):
                winners.append(bet.document)

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

            # TODO: Remover constante hardcodeada.
            if message.message_type == 3: 
                bet_chunk_message = message
                if bet_chunk_message is None:
                    raise Exception("Could not read message.")
                
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
            
            # TODO: Remover constantes hardcodeadas.
            elif message.message_type == 5:
                if self._lottery_finished:
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
        if self._client_socket:
            logging.info("action: close_client_socket | result: in_progress")
            self._client_socket.close()
            logging.info("action: close_client_socket | result: success")

        self._server_socket.close()
        logging.info("action: close_server_socket | result: success")
        logging.info("action: graceful_shutdown | result: success")
