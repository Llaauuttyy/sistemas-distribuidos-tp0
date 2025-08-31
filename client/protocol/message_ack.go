package protocol

import (
	"encoding/binary"
	"fmt"
)

const MessageAckType byte = 1

type MessageAck struct {
	Number string
}

// Field sizes in bytes
const MessageAckNumberSize = 8

func MessageAckFromBytes(data []byte) (*MessageAck, error) {
	if len(data) < MessageAckNumberSize {
		return nil, fmt.Errorf("data too short for MessageAck")
	}

	numberBytes := data[:MessageAckNumberSize]

	// Convert bytes to number
	number := binary.BigEndian.Uint64(numberBytes)

	return &MessageAck{
		Number: fmt.Sprintf("%d", number),
	}, nil
}
