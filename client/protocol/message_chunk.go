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

	log.Infof("Creating MessageBetChunk with %d bets for agency %s", mc.totalBets, mc.agency)

	// TODO: Convertir a una funcion en utils para usarla en varios lados está este código.
	// Convert string to byte slice
	data := []byte(mc.agency)
	size := MessageBetChunkAgencySize

	log.Infof("Agency byte size: %d, data size: %d, resta: %d", size, len(data), size - len(data))
	if len(data) < size {
		padding := make([]byte, size-len(data))
		// Fill up space left using null bytes
		data = append(data, padding...)
	}
	buf.Write(data)

	log.Infof("MessageBetChunk after writing agency has data in bytes: %d", data)

	for _, m := range mc.bets {
		betBytes := m.ToBytes()
		buf.Write(betBytes)
	}

	bytes_return := buf.Bytes()

	log.Infof("MessageBetChunk total size in bytes: %d", len(bytes_return))

	if len(bytes_return) > MaxBatchSizeBytes {
		return nil, fmt.Errorf("chunk size exceeds 8kB")
	}

	return buf.Bytes(), nil
}
