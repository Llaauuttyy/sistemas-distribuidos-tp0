from protocol.base import Message
from protocol.bet import MessageBet

import logging

# TODO: Que haya un flag que tenga lo valores:
# 1: Devuelve ganadores.
# 2: Informa que todavia no hay sorteo.
# Despues tengo funcion en el server para informar que no hay sorteo.
# y manda este mensaje con flag 2, y del cliente leo este byte para definir si es 1 o 2.
# Si es 2 intento mas tarde y si es 1 termino.

REPORT_WINNERS = 1
NO_LOTTERY_YET = 2

class MessageWinners(Message):
    TYPE = 6
    FIELD_SIZES = {
        "flag": 1,
        "total_winners": 8,
        "document": MessageBet.FIELD_SIZES["document"]
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())
    
    def __init__(self, flag: int, winners: list[str]):
        super().__init__(self.TYPE)
        self.total_winners = len(winners)
        self.flag = flag
        self.winners = winners

    def to_bytes(self) -> bytes:
        """
        Serialize MessageACK to bytes.
        """
        data = self.message_type.to_bytes(1, byteorder="big")

        data += self.total_winners.to_bytes(self.FIELD_SIZES["total_winners"], byteorder="big")
        
        data += self.flag.to_bytes(self.FIELD_SIZES["flag"], byteorder="big")

        if self.flag == REPORT_WINNERS:
            for winner in self.winners:
                data += winner.encode("utf-8").ljust(self.FIELD_SIZES["document"], b"\x00")
        
        return data
