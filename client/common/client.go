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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(bet bet.Bet) {
	// Create a channel to handle to shutdown when signal is received.
	sigs := make(chan os.Signal, 1)

	signal.Notify(sigs, syscall.SIGTERM)
	
	go func() {
		<-sigs
        log.Infof("action: shutdown_signal | result: in_progress | client_id: %v", c.config.ID)
		c.running = false
		if c.conn != nil {
			log.Infof("action: closed_client_socket | result: in_progress | client_id: %v", c.config.ID)
			c.conn.Close()
			log.Infof("action: closed_client_socket | result: success | client_id: %v", c.config.ID)
		}
		log.Infof("action: shutdown_signal | result: success | client_id: %v", c.config.ID)
	}()
		
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; c.running && msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		cp := protocol.NewCommunicationProtocol(c.conn)

		// bytes := bet.ToBytes()
		// log.Infof("action: send_message | length: %v",
		// 	len(bytes),
		// )

		err := cp.SendBet(bet)
		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v | error: %v",
				bet.Document,
				bet.Number,
				err,
			)
		}

		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v ",
			bet.Document,
			bet.Number,
		)
			
		err = cp.ReceiveAck(bet.Number)
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_ack | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// log.Infof("action: receive_ack | result: success | client_id: %v | bet_number: %v | ack_number: %v",
		// 	c.config.ID,
		// 	bet.Number,
		// 	ackMessage.Number,
		// )

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
