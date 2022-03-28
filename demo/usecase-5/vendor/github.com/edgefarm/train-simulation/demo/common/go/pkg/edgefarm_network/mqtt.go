package edgefarm_network

import (
	"context"
	"fmt"
	"net"
	"time"

	"github.com/eclipse/paho.golang/paho"
	env "github.com/edgefarm/train-simulation/demo/common/go/pkg/env"
)

// MqttConnection represents the MQTT connection
type MqttConnection struct {
	client *paho.Client
	server string
	port   string
}

const (
	defaultMQTTServer string = "mosquitto"
	defaultMQTTPort   string = "1883"
	qos               int    = 1
)

// NewMqttConnection creates new MQTT client
func NewMqttConnection() *MqttConnection {

	mqttServer := env.GetEnvVar("MQTT_SERVER", defaultMQTTServer)
	mqttPort := env.GetEnvVar("MQTT_PORT", defaultMQTTPort)

	return &MqttConnection{
		client: &paho.Client{},
		server: mqttServer,
		port:   mqttPort,
	}
}

// Connect to MQTT server. Server URL can be provided via MQTT_SERVER environment variable.
func (m *MqttConnection) Connect(connectTimeoutSeconds int) error {

	conn, err := net.Dial("tcp", fmt.Sprintf("%s:%s", m.server, m.port))
	if err != nil {
		return fmt.Errorf("Failed to connect to %s:%s: %s", m.server, m.port, err)
	}

	// From https://github.com/eclipse/paho.golang/blob/336f2adf08b8233199ac8132b8dd12cbb8c69eca/paho/client.go
	// client.Conn *MUST* be set to an already connected net.Conn before
	// Connect() is called.
	m.client = paho.NewClient(paho.ClientConfig{
		Conn: conn,
	})

	for i := 0; i < connectTimeoutSeconds; i++ {
		// Connect Client to MQTT Broker
		res, err := m.client.Connect(context.Background(), &paho.Connect{})
		if err != nil {
			fmt.Printf("Failed to connect to %s: %s", m.server, err.Error())
		} else if res.ReasonCode != 0 {
			fmt.Printf("Failed to connect with reason: %d - %s", res.ReasonCode, res.Properties.ReasonString)
		} else {
			return nil
		}
		time.Sleep(time.Second)
	}
	return fmt.Errorf("Cannot connect to MQTT broker.")
}

// Subscribe subscribe to topic, required handler function for message receive.
func (m *MqttConnection) Subscribe(topic string, handlerFunc interface{}) error {
	// Check if passed function is of correct type
	if f, ok := handlerFunc.(func(*paho.Publish)); ok {
		// Register handler for this topic
		m.client.Router.RegisterHandler(topic, f)
		// Subscribe to mqtt topics
		sa, err := m.client.Subscribe(context.Background(), &paho.Subscribe{
			Subscriptions: map[string]paho.SubscribeOptions{
				topic: {QoS: byte(qos)},
			},
		})
		if err != nil {
			return err
		}
		if sa.Reasons[0] != byte(qos) {
			return fmt.Errorf("Failed to subscribe to %s : %d", topic, sa.Reasons[0])
		}
		return nil
	}
	return fmt.Errorf("Provided handlerFunc not of correct type")
}

// Publish publish message to topic provided
func (m *MqttConnection) Publish(topic string, message []byte) error {
	return fmt.Errorf("Publish not implemented")
}

// Close close mqtt connection
func (m *MqttConnection) Close() {
	if m.client != nil {
		d := &paho.Disconnect{ReasonCode: 0}
		m.client.Disconnect(d)
	}
}
