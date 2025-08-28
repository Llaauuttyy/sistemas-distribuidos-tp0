package protocol

import (
	"bytes"
	"fmt"
)

const MessageBetChunkType byte = 3

type MessageBetChunk struct {
	totalBets 	int
	bets 	 	[]MessageBet
}

func NewMessageBetChunk(bets []MessageBet) *MessageBetChunk {
	return &MessageBetChunk{
		totalBets: len(bets),
		bets: bets,
	}
}

func (mc *MessageBetChunk) ToBytes() ([]byte, error) {
	buf := new(bytes.Buffer)
	buf.WriteByte(MessageBetChunkType)

	buf.WriteByte(byte(mc.totalBets))

	for _, m := range mc.bets {
		betBytes := m.ToBytes()
		buf.Write(betBytes)
	}

	bytes_return := buf.Bytes()
	if len(bytes_return) > 8000 {
		return nil, fmt.Errorf("chunk size exceeds 8kB")
	}

	return buf.Bytes(), nil
}
