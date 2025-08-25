package protocol

import (
	"bytes"
)

type MessageBet struct {
	Agency    string
	FirstName string
	LastName  string
	Document  string
	Birthdate string
	Number    string
}

const (
	MessageBetType byte = 2
)

const ( 
	MessageAckType byte = 1
)

var MessageBetFieldSizes = map[string]int{
	"Agency":    20,
	"FirstName": 30,
	"LastName":  15,
	"Document":  8,
	"Birthdate": 10,
	"Number":    8,
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

