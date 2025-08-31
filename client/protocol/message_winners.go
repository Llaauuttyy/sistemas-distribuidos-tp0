package protocol

import (
	"bytes"
	"fmt"
)

const MessageWinnersType byte = 6

// Flags for MessageWinners
const ReportWinners = 1
const NoLoteryYet = 2

type MessageWinners struct {
	TotalWinners 	int
	Flag			byte
	Winners 	 	[]string
}

// Each winner has the same length as Document in MessageBet
const WinnerLength = MessageBetDocumentSize

// Field sizes in bytes
const (
	MessageWinnersTotalWinnersSize	= 8
	MessageWinnersFlagSize			= 1
)

func NewMessageWinners(flag byte,  winners []string) *MessageWinners {
	return &MessageWinners{
		TotalWinners: len(winners),
		Flag: flag,
		Winners: winners,
	}
}

func MessageWinnersFromBytes(data []byte, totalWinners int) (*MessageWinners, error) {
	flag := data[0]

	winnersBytes := data[1:]
	
	if len(winnersBytes) < totalWinners * WinnerLength {
		return nil, fmt.Errorf("data too short for MessageWinners")
	}
	
	// Extract winners
	var winners []string

	start := 0
	end := WinnerLength
	for i := 0; i < totalWinners; i++ {
		winner := winnersBytes[start:end]
		
		// Trim null bytes
		winnerString := string(bytes.Trim(winner, "\x00"))

		winners = append(winners, winnerString)

		// Move to next winner
		start += WinnerLength
		end += WinnerLength
	}

	return &MessageWinners{
		TotalWinners: totalWinners,
		Flag: flag,
		Winners: winners,
	}, nil
}