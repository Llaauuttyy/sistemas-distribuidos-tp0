from protocol.base import Message

class MessageGetWinners(Message):
    TYPE = 5
    FIELD_SIZES = {
        "agency": 8,
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())
    
    def __init__(self, agency: str):
        super().__init__(self.TYPE)
        self.agency = agency

    @staticmethod
    def from_bytes(data: bytes) -> "MessageGetWinners":
        """
        Deserialize bytes to MessageGetWinners object.
        """

        agency = data[0:8].decode("utf-8").rstrip("\x00")

        return MessageGetWinners(agency)