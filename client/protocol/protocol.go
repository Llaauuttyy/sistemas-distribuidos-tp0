package protocol

import (
	"net"
	"fmt"
	"io"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type CommunicationProtocol struct {
	conn net.Conn
}

func NewCommunicationProtocol(conn net.Conn) *CommunicationProtocol {
	return &CommunicationProtocol{conn: conn}
}

func (cp *CommunicationProtocol) ProcessChunk(bets []MessageBet) (error) {
	// Create chunk
	chunk := NewMessageBetChunk(bets)
	chunkBytes, err := chunk.ToBytes()
	
	if err != nil {
		return fmt.Errorf("error creating MessageBetChunk: %w", err)
	}

	// Send chunk
	if err := cp.SendMessage(chunkBytes); err != nil {
		return fmt.Errorf("error sending MessageBetChunk: %w", err)
	}

	return nil
}

// Avoid short-write: writes until the entire message is sent
func (cp *CommunicationProtocol) SendMessage(msg []byte) error {
	totalSent := 0
	for totalSent < len(msg) {
		n, err := cp.conn.Write(msg[totalSent:])
		if err != nil {
			return fmt.Errorf("sendMessage error: %w", err)
		}
		totalSent += n
	}
	return nil
}

// Avois short-read: used ReadFull to ensure the entire message is received
func (cp *CommunicationProtocol) ReceiveExactBytes(size int) ([]byte, error) {
	buf := make([]byte, size)
	_, err := io.ReadFull(cp.conn, buf)
	if err != nil {
		return nil, fmt.Errorf("receiveMessage error: %w", err)
	}
	return buf, nil
}

func (cp *CommunicationProtocol) SendBet(bet MessageBet) error {
	return cp.SendMessage(bet.ToBytes())
}

func (cp *CommunicationProtocol) ReceiveAck(number string) (error, byte) {
	// Receive the first byte to determine the message type
	typeByte, err := cp.ReceiveExactBytes(1)
    if err != nil {
        return err, 0
    }

	// Check the type of the message and process its bytes.
	switch typeByte[0] {
	case MessageAckType:
		ackBytes, err := cp.ReceiveExactBytes(MessageAckFieldSizes["Number"])
		if err != nil {
			return fmt.Errorf("receiveMessage error: %w", err), 0
		}

		// Parse the ack message
		ack, err := MessageAckFromBytes(ackBytes)
		if err != nil {
			return fmt.Errorf("error parsing MessageAck: %w", err), 0
		}

		// Validate that the ack number matches the sent bet number
		if number != ack.Number {
			return fmt.Errorf("invalid ack message: expected %v, received %v", number, ack.Number), 0
		}

		return nil, 0

	case MessageChunkErrorType:
		errorBytes, err := cp.ReceiveExactBytes(MessageChunkErrorFieldSizes["Number"])
		if err != nil {
			return fmt.Errorf("receiveMessage error: %w", err), 0
		}

		chunkError, err := MessageChunkErrorFromBytes(errorBytes)
		if err != nil {
			return fmt.Errorf("error parsing MessageChunkError: %w", err), 0
		}

		return fmt.Errorf("server reported chunk error for bet number: %v", chunkError.Number), MessageChunkErrorType
	default:
		return fmt.Errorf("unknown message type: %v", typeByte[0]), 0
	}
}



