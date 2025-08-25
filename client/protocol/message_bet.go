package protocol

import (
	"bytes"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/bet"
)

const MessageBetType byte = 2

type MessageBet struct {
	Bet bet.Bet
}

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

	writeParams(m.Bet.Agency, MessageBetFieldSizes["Agency"])
	writeParams(m.Bet.FirstName, MessageBetFieldSizes["FirstName"])
	writeParams(m.Bet.LastName, MessageBetFieldSizes["LastName"])
	writeParams(m.Bet.Document, MessageBetFieldSizes["Document"])
	writeParams(m.Bet.Birthdate, MessageBetFieldSizes["Birthdate"])
	writeParams(m.Bet.Number, MessageBetFieldSizes["Number"])

	return buf.Bytes()
}
