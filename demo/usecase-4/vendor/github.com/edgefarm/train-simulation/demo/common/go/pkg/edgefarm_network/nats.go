package edgefarm_network

import (
	"fmt"
	"log"
	"os"
	"time"

	nats "github.com/nats-io/nats.go"
)

// NatsConnection represents nats connection
type NatsConnection struct {
	client       *nats.Conn
	server       string
	creds        string
	subsciptions map[string]*nats.Subscription
}

const (
	defaultNATSServer string = "nats://nats.nats:4222"
)

// NewNatsConnection creates new nats client
func NewNatsConnection() *NatsConnection {
	natsServer := defaultNATSServer
	if env := os.Getenv("NATS_SERVER"); len(env) > 0 {
		natsServer = env
	}
	creds := ""
	if env := os.Getenv("NATS_CREDS_PATH"); len(env) > 0 {
		creds = env
	}
	return &NatsConnection{
		client:       &nats.Conn{},
		server:       natsServer,
		creds:        creds,
		subsciptions: make(map[string]*nats.Subscription),
	}
}

// Connect to NATS server. Server URL can be provided via NATS_SERVER environment variable.
// Provide NATS_CREDS_PATH if credentials shall be provided.
func (n *NatsConnection) Connect(connectTimeoutSeconds int) error {

	// Connect to nats server
	// Connect Options
	opts := []nats.Option{nats.Timeout(30 * time.Second)}
	if n.creds != "" {
		opts = append(opts, nats.UserCredentials(n.creds))
	}
	opts = setupConnOptions(opts)
	for i := 0; i < connectTimeoutSeconds; i++ {
		var err error
		n.client, err = nats.Connect(n.server, opts...)
		if err != nil {
			log.Printf("Connect failed: %s\n", err)
		} else {
			return nil
		}
		time.Sleep(time.Second)
	}
	return fmt.Errorf("Cannot connect to NAS server.")
}

// Subscribes to subject, required handler function for message receive.
func (n *NatsConnection) Subscribe(subject string, handlerFunc interface{}) error {
	// Check if passed function is of correct type
	if f, ok := handlerFunc.(func(*nats.Msg)); ok {
		// Subscribe to nats subject
		sub, err := n.client.Subscribe(subject, f)
		if err != nil {
			return err
		}
		n.subsciptions[subject] = sub
		return nil
	}
	return fmt.Errorf("Provided handlerFunc not of correct type")
}

// Publish publish message to topic provided
func (n *NatsConnection) Publish(topic string, message []byte) error {
	return n.client.Publish(topic, message)
}

// Close close nats connection
func (n *NatsConnection) Close() {
	if n.client != nil {
		for _, sub := range n.subsciptions {
			sub.Unsubscribe()
		}
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
