package protocol

import (
	"bytes"
)

const MessageBetType byte = 2

type MessageBet struct {
	Agency    string
	FirstName string
	LastName  string
	Document  string
	Birthdate string
	Number    string
}

// Field sizes in bytes
const (
	MessageBetAgencySize	= 8
	MessageBetFirstNameSize	= 30
	MessageBetLastNameSize	= 15
	MessageBetDocumentSize	= 8
	MessageBetBirthdateSize	= 10
	MessageBetNumberSize	= 8
)

func (m *MessageBet) ToBytes() []byte {
	buf := new(bytes.Buffer)
	buf.WriteByte(MessageBetType)

	writeParams := func(value string, size int) {
		// Convert string to byte slice
		data := []byte(value)
		if len(data) < size {
			padding := make([]byte, size-len(data))
			// Fill up space left using null bytes
			data = append(data, padding...)
		}
		buf.Write(data)
	}

	writeParams(m.Agency, MessageBetAgencySize)
	writeParams(m.FirstName, MessageBetFirstNameSize)
	writeParams(m.LastName, MessageBetLastNameSize)
	writeParams(m.Document, MessageBetDocumentSize)
	writeParams(m.Birthdate, MessageBetBirthdateSize)
	writeParams(m.Number, MessageBetNumberSize)

	return buf.Bytes()
}
