from protocol.base import Message
from protocol.bet import MessageBet

class MessageBetChunk(Message):
    TYPE = 3

    def __init__(self, bets: list[MessageBet]):
        super().__init__(self.TYPE)
        self.totalBets = len(bets)
        self.bets = bets