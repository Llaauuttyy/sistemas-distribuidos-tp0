from protocol.base import Message

class MessageACK(Message):
    TYPE = 1
    FIELD_SIZES = {"number": 8}
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())
    
    def __init__(self, number: str):
        super().__init__(self.TYPE)
        self.number = int(number)

    def to_bytes(self) -> bytes:
        """
        Serialize MessageACK to bytes.
        """
        data = self.message_type.to_bytes(1, byteorder="big")
        data += self.number.to_bytes(self.FIELD_SIZES["number"], byteorder="big")
        return data
