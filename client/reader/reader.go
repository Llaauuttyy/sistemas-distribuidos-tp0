package reader

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/bet"
)

type BetReader struct {
	file      	*os.File
	scanner   	*bufio.Scanner
	path 	  	string
	rowNum  	int
	maxFields	int
}

func NewBetReader(path string) (*BetReader, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}

	return &BetReader{
		file:    file,
		scanner: bufio.NewScanner(file),
		path:    path,
		rowNum: 0,
		maxFields: 5,
	}, nil
}

func (br *BetReader) ReadBets(n int) ([]bet.Bet, error) {
	var bets []bet.Bet

	// Read each line of the file until n or EOF.
	for i := 0; i < n && br.scanner.Scan(); i++ {
		br.rowNum++
		line := br.scanner.Text()
		fields := strings.Split(line, ",")
		if len(fields) != br.maxFields {
			return bets, fmt.Errorf("invalid line format (line %d): %s", br.rowNum, line)
		}

		// Append bet to slice
		bets = append(bets, bet.Bet{
			FirstName: fields[0],
			LastName:  fields[1],
			Document:  fields[2],
			Birthdate: fields[3],
			Number:    fields[4],
		})
	}
	
	if err := br.scanner.Err(); err != nil {
		return bets, err
	}

	return bets, nil
}

func (br *BetReader) Close() error {
	// Close the file
	return br.file.Close()
}