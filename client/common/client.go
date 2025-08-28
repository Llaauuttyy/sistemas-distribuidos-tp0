package common

import (
	// "bufio"
	// "fmt"
	"os"
    "os/signal"
    "syscall"
	"net"
	"time"
	
	"github.com/op/go-logging"
	// "github.com/spf13/viper"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/protocol"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/bet"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/reader"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config  ClientConfig
	conn    net.Conn
	reader *reader.BetReader
	running bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		running: true,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// CreateClientReader Initializes client reader.
func (c *Client) createClientReader(filePath string) error {
	betReader, err := reader.NewBetReader(filePath)
	if err != nil {
		log.Criticalf(
			"action: reader | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.reader = betReader
	return nil
}

func (c *Client) CloseIfNoMoreBets(bets []bet.Bet) bool {
	if len(bets) == 0 {
		c.Close()
		return true
	}

	return false
}

func (c *Client) PrepareBetsToBeSent(bets []bet.Bet) []protocol.MessageBet {
	messageBets := []protocol.MessageBet{}
	for i := range bets {
		messageBets = append(messageBets, protocol.MessageBet{
			Agency:    c.config.ID,
			FirstName: bets[i].FirstName,
			LastName:  bets[i].LastName,
			Document:  bets[i].Document,
			Birthdate: bets[i].Birthdate,
			Number:    bets[i].Number,
		})
	}

	return messageBets
}

func (c *Client) Close() {
	c.running = false
	if c.conn != nil {
		log.Infof("action: closed_client_socket | result: in_progress | client_id: %v", c.config.ID)
		c.conn.Close()
		log.Infof("action: closed_client_socket | result: success | client_id: %v", c.config.ID)
	}
	if c.reader != nil {
		log.Infof("action: closed_client_reader | result: in_progress | client_id: %v", c.config.ID)
		c.reader.Close()
		log.Infof("action: closed_client_reader | result: success | client_id: %v", c.config.ID)
	}
	
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(betFile string, maxBatchSize int) {
	// Create a channel to handle to shutdown when signal is received.
	sigs := make(chan os.Signal, 1)

	signal.Notify(sigs, syscall.SIGTERM)
	
	go func() {
		<-sigs
        log.Infof("action: shutdown_signal | result: in_progress | client_id: %v", c.config.ID)
		c.Close()
	}()
	
	c.createClientReader(betFile)

	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; c.running; msgID++ {

		bets, err := c.reader.ReadBets(maxBatchSize)
		if err != nil {
			log.Criticalf("action: read_bet_file | result: fail | client_id: %v | file: %v | error: %v",
				c.config.ID,
				betFile,
				err,
			)
			c.Close()
			return
		}

		if c.CloseIfNoMoreBets(bets) {
			return
		}

		log.Infof("action: read_bet_file | result: success | client_id: %v | file: %v | bets_read: %v",
			c.config.ID,
			betFile,
			len(bets),
		)

		// Create the connection the server in every loop iteration.
		c.createClientSocket()
		
		cp := protocol.NewCommunicationProtocol(c.conn)
		
		messageBets := c.PrepareBetsToBeSent(bets)
		err = cp.ProcessChunk(messageBets)
		if err != nil {
			log.Errorf("action: process_chunk | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			c.Close()
			return
		}
 
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v ",
			bets[0].Document,
			bets[0].Number,
		)
		
		// Code 4 means chunk failed to store.
		err, code := cp.ReceiveAck(bets[0].Number)
		c.conn.Close()

		if (err != nil || code == protocol.MessageChunkErrorType) {
			log.Errorf("action: receive_ack | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// // Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
