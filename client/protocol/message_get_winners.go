package protocol

import (
	"bytes"
)

const MessageGetWinnersType byte = 5

type MessageGetWinners struct {
	Agency string
}

// Field sizes in bytes
const MessageGetWinnersAgencySize = MessageBetAgencySize

func NewMessageGetWinners(agency string) *MessageGetWinners {
	return &MessageGetWinners{
		Agency: agency,
	}
}

func (mc *MessageGetWinners) ToBytes() ([]byte) {
	buf := new(bytes.Buffer)
	buf.WriteByte(MessageGetWinnersType)

	// Convert string to byte slice
	data := []byte(mc.Agency)
	size := MessageGetWinnersAgencySize
	if len(data) < size {
		padding := make([]byte, size-len(data))
		// Fill up space left using null bytes
		data = append(data, padding...)
	}
	buf.Write(data)

	return buf.Bytes()
}