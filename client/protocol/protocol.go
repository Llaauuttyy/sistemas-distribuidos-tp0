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

func (cp *CommunicationProtocol) ReceiveAck(number string) (error) {
	// Receive the first byte to determine the message type
	typeByte, err := cp.ReceiveExactBytes(1)
    if err != nil {
        return err
    }

	// Check the type of the message and process its bytes.
	switch typeByte[0] {
	case MessageAckType:
		ackBytes, err := cp.ReceiveExactBytes(MessageAckFieldSizes["Number"])
		if err != nil {
			return fmt.Errorf("receiveMessage error: %w", err)
		}

		log.Infof("action: receive_ack | length: %v | type: %v",
			len(ackBytes),
			typeByte[0],
		)

		// Parse the ack message
		ack, err := MessageAckFromBytes(ackBytes)
		if err != nil {
			return fmt.Errorf("error parsing MessageAck: %w", err)
		}

		// Validate that the ack number matches the sent bet number
		if number != ack.Number {
			return fmt.Errorf("invalid ack message: expected %v, received %v", number, ack.Number)
		}

		return nil
	default:
		return fmt.Errorf("unknown message type: %v", typeByte[0])
	}
}



