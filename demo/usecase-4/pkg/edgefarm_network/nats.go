package edgefarm_network

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/nats-io/nats.go"
)

// Implements EdgefarmNetworkIf for nats connections
type NatsConnection struct {
	client *nats.Conn
}

const (
	defaultNATSServer string = "nats://nats.nats:4222"
)

// Connect to NATS server. Server URL can be provided via NATS_SERVER environment variable.
// Provide NATS_CREDS_PATH if credentials shall be provided.
func (n *NatsConnection) Connect(connectTimeoutSeconds int) error {
	natsServer := defaultNATSServer
	if env := os.Getenv("NATS_SERVER"); len(env) > 0 {
		natsServer = env
	}
	creds := ""
	if env := os.Getenv("NATS_CREDS_PATH"); len(env) > 0 {
		creds = env
	}

	// Connect to nats server
	// Connect Options
	opts := []nats.Option{nats.Timeout(30 * time.Second)}
	if creds != "" {
		opts = append(opts, nats.UserCredentials(creds))
	}
	opts = setupConnOptions(opts)
	n.client = &nats.Conn{}
	var err error = nil
	for i := 0; i < connectTimeoutSeconds; i++ {
		n.client, err = nats.Connect(natsServer, opts...)
		if err != nil {
			log.Printf("Connect failed: %s\n", err)
		} else {
			return nil
		}
		time.Sleep(time.Second)
	}
	return fmt.Errorf("Cannot connect to NAS server.")
}

// Subscribe subscribe to topic, required handler function for message receive.
func (n *NatsConnection) Subscribe(topic string, handlerFunc interface{}) error {
	return fmt.Errorf("Subscribe not implemented")
}

// Publish publish message to topic provided
func (n *NatsConnection) Publish(topic string, message []byte) error {
	return n.client.Publish(topic, message)
}

// Close close nats connection
func (n *NatsConnection) Close() {
	if n.client != nil {
		n.client.Close()
	}
}

func setupConnOptions(opts []nats.Option) []nats.Option {
	totalWait := 10 * time.Minute
	reconnectDelay := time.Second

	opts = append(opts, nats.ReconnectWait(reconnectDelay))
	opts = append(opts, nats.MaxReconnects(int(totalWait/reconnectDelay)))
	opts = append(opts, nats.DisconnectErrHandler(func(nc *nats.Conn, err error) {
		log.Printf("Disconnected due to:%s, will attempt reconnects for %.0fm", err, totalWait.Minutes())
	}))
	opts = append(opts, nats.ReconnectHandler(func(nc *nats.Conn) {
		log.Printf("Reconnected [%s]", nc.ConnectedUrl())
	}))
	opts = append(opts, nats.ClosedHandler(func(nc *nats.Conn) {
		log.Fatalf("Exiting: %v", nc.LastError())
	}))
	return opts
}
