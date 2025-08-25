from common.base import Message

class MessageBet(Message):
    TYPE = 2
    FIELD_SIZES = {
        "agency": 20,
        "first_name": 30,
        "last_name": 15,
        "document": 8,
        "birthdate": 10,
        "number": 8,
    }
    PAYLOAD_BYTES = sum(FIELD_SIZES.values())

    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        super().__init__(self.TYPE)
        self.agency = agency
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = birthdate
        self.number = number

    def __str__(self):
        return (
            f"MessageBet(agency={self.agency}, first_name={self.first_name}, "
            f"last_name={self.last_name}, document={self.document}, "
            f"birthdate={self.birthdate}, number={self.number})"
        )
    
    @staticmethod
    def from_bytes(data: bytes) -> "MessageBet":
        """
        Deserialize bytes to MessageBet object.
        """
        sizes = MessageBet.FIELD_SIZES
        offset = 0
        fields = {}
        
        for key, size in sizes.items():
            raw = data[offset:offset+size]
            fields[key] = raw.decode("utf-8").rstrip("\x00")
            offset += size
        
        return MessageBet(
            fields["agency"],
            fields["first_name"],
            fields["last_name"],
            fields["document"],
            fields["birthdate"],
            fields["number"]
        )
