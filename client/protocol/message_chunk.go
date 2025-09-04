package protocol

import (
	"bytes"
	"fmt"
)

const MaxBatchSizeBytes = 8192
const MessageBetChunkType byte = 3

type MessageBetChunk struct {
	totalBets 	int
	agency 		string
	bets 	 	[]MessageBet
}

func NewMessageBetChunk(agency string, bets []MessageBet) *MessageBetChunk {
	return &MessageBetChunk{
		totalBets: len(bets),
		agency: agency,
		bets: bets,
	}
}

// Field sizes in bytes
const MessageBetChunkAgencySize = MessageBetAgencySize

func (mc *MessageBetChunk) ToBytes() ([]byte, error) {
	buf := new(bytes.Buffer)
	buf.WriteByte(MessageBetChunkType)

	buf.WriteByte(byte(mc.totalBets))

	size := MessageBetChunkAgencySize

	// Write agency with padding
	WriteWithPadding(buf, mc.agency, size)

	// Write each bet
	for _, m := range mc.bets {
		betBytes := m.ToBytes()
		buf.Write(betBytes)
	}

	bytes_return := buf.Bytes()

	if len(bytes_return) > MaxBatchSizeBytes {
		return nil, fmt.Errorf("chunk size exceeds 8kB")
	}

	return buf.Bytes(), nil
}
