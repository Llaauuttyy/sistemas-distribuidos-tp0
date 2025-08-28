package protocol

import (
	"encoding/binary"
	"fmt"
)

const MessageChunkErrorType byte = 4

type MessageChunkError struct {
	Number string
}

var MessageChunkErrorFieldSizes = map[string]int{
	"Number": 8,
}

func MessageChunkErrorFromBytes(data []byte) (*MessageChunkError, error) {
	if len(data) < MessageAckFieldSizes["Number"] {
		return nil, fmt.Errorf("data too short for MessageAck")
	}

	numberBytes := data[:MessageAckFieldSizes["Number"]]

	// Convert bytes to number
	number := binary.BigEndian.Uint64(numberBytes)

	return &MessageChunkError{
		Number: fmt.Sprintf("%d", number),
	}, nil
}
