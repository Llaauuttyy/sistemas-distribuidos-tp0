package protocol

import (
	"encoding/binary"
	"fmt"
)

const MessageChunkErrorType byte = 4

type MessageChunkError struct {
	Number string
}

// Field sizes in bytes
const MessageChunkErrorNumberSize = 8

func MessageChunkErrorFromBytes(data []byte) (*MessageChunkError, error) {
	if len(data) < MessageChunkErrorNumberSize {
		return nil, fmt.Errorf("data too short for MessageChunkError")
	}

	numberBytes := data[:MessageChunkErrorNumberSize]

	// Convert bytes to number
	number := binary.BigEndian.Uint64(numberBytes)

	return &MessageChunkError{
		Number: fmt.Sprintf("%d", number),
	}, nil
}
