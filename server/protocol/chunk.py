from protocol.base import Message
from protocol.bet import MessageBet

import logging

class MessageBetChunk(Message):
    TYPE = 3
    FIELD_SIZES = {
        "agency": 8,
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())

    def __init__(self, agency: str, bets: list[MessageBet]):
        super().__init__(self.TYPE)
        self.totalBets = len(bets)
        self.agency = agency
        self.bets = bets

    @staticmethod
    def from_bytes(data: bytes, total_bets: int) -> "MessageBetChunk":
        """
        Deserialize bytes to MessageBetChunk object.
        """

        agency = data[0:MessageBetChunk.FIELD_SIZES["agency"]].decode("utf-8").rstrip("\x00")

        bets = []

        # Parse each bet
        bet_start = 1 + MessageBetChunk.FIELD_SIZES["agency"]
        bet_end = bet_start + MessageBet.PAYLOAD_BYTES
        for _ in range(total_bets):
            bet_bytes = data[bet_start:bet_end]
            bets.append(MessageBet.from_bytes(bet_bytes))

            # logging.info(f"APUESTA: {bets[-1]}")
            # Move to next bet
            bet_start = bet_end + 1
            bet_end = bet_start + MessageBet.PAYLOAD_BYTES


        return MessageBetChunk(agency, bets)