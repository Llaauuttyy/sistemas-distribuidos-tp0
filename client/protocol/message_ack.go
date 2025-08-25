package protocol

import (
	"encoding/binary"
	"fmt"
)

const MessageAckType byte = 1

type MessageAck struct {
	Number string
}

var MessageAckFieldSizes = map[string]int{
	"Number": 8,
}

func MessageAckFromBytes(data []byte) (*MessageAck, error) {
	if len(data) < MessageAckFieldSizes["Number"] {
		return nil, fmt.Errorf("data too short for MessageAck")
	}

	numberBytes := data[:MessageAckFieldSizes["Number"]]
	number := binary.BigEndian.Uint64(numberBytes)

	return &MessageAck{
		Number: fmt.Sprintf("%d", number),
	}, nil
}
