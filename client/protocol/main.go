package protocol

import (
	"encoding/binary"
	"bytes"
	"net"
	"fmt"
	"io"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type MessageBet struct {
	Agency    string
	FirstName string
	LastName  string
	Document  string
	Birthdate string
	Number    string
}

var MessageBetFieldSizes = map[string]int{
	"Agency":    20,
	"FirstName": 30,
	"LastName":  15,
	"Document":  8,
	"Birthdate": 10,
	"Number":    8,
}

const (
	MessageBetType byte = 2
)

type MessageAck struct {
	Number    string
}

var MessageAckFieldSizes = map[string]int{
	"Number":    8,
}

const ( 
	MessageAckType byte = 1
)

// Receive bytes without the type byte
func MessageAckFromBytes(data []byte) (*MessageAck, error) {
	if len(data) < MessageAckFieldSizes["Number"] {
		return nil, fmt.Errorf("data too short for MessageAck")
	}

	numberBytes := data[0 : MessageAckFieldSizes["Number"]]
	number := binary.BigEndian.Uint64(numberBytes)

	return &MessageAck{
		Number: fmt.Sprintf("%d", number),
	}, nil
}

func (m *MessageBet) ToBytes() []byte {
	buf := new(bytes.Buffer)

	buf.WriteByte(MessageBetType)

	writeParams := func(value string, size int) {
		data := []byte(value)
		if len(data) < size {
			padding := make([]byte, size-len(data))
			data = append(data, padding...)
		}
		buf.Write(data)
	}

	writeParams(m.Agency, MessageBetFieldSizes["Agency"])
	writeParams(m.FirstName, MessageBetFieldSizes["FirstName"])
	writeParams(m.LastName, MessageBetFieldSizes["LastName"])
	writeParams(m.Document, MessageBetFieldSizes["Document"])
	writeParams(m.Birthdate, MessageBetFieldSizes["Birthdate"])
	writeParams(m.Number, MessageBetFieldSizes["Number"])

	return buf.Bytes()
}

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

// Avois short-read: used ReafFull to ensure the entire message is received
func (cp *CommunicationProtocol) ReceiveExactBytes(size int) ([]byte, error) {
	buf := make([]byte, size)
	_, err := io.ReadFull(cp.conn, buf)
	if err != nil {
		return nil, fmt.Errorf("receiveMessage error: %w", err)
	}
	return buf, nil
}

func (cp *CommunicationProtocol) ReceiveAck() (*MessageAck, error) {
	// Receive the first byte to determine the message type
	typeByte, err := cp.ReceiveExactBytes(1)
    if err != nil {
        return nil, err
    }

	// Check the type of the message and process its bytes.
	switch typeByte[0] {
	case MessageAckType:
		ackBytes, err := cp.ReceiveExactBytes(MessageAckFieldSizes["Number"])
		if err != nil {
			return nil, fmt.Errorf("receiveMessage error: %w", err)
		}

		log.Infof("action: receive_ack | length: %v | type: %v",
			len(ackBytes),
			typeByte[0],
		)

		return MessageAckFromBytes(ackBytes)
	default:
		return nil, fmt.Errorf("unknown message type: %v", typeByte[0])
	}
}



