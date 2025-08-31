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

	// Write agency with padding
	WriteWithPadding(buf, mc.Agency, MessageGetWinnersAgencySize)

	return buf.Bytes()
}