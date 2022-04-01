package edgefarm_network

import (
	"fmt"
	"os"
	"sync"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

// MqttConnection represents the MQTT connection
type MqttConnection struct {
	client                 mqtt.Client
	server                 string
	port                   string
	mutex                  sync.Mutex
	subscriptionHandlerMap map[string]func(mqtt.Message)
}

const (
	defaultMQTTServer string = "mosquitto"
	defaultMQTTPort   string = "1883"
	qos               int    = 1
)

// NewMqttConnection creates new MQTT client
func NewMqttConnection() *MqttConnection {
	mqttServer := defaultMQTTServer
	if env := os.Getenv("MQTT_SERVER"); len(env) > 0 {
		mqttServer = env
	}
	mqttPort := defaultMQTTPort
	if env := os.Getenv("MQTT_PORT"); len(env) > 0 {
		mqttPort = env
	}

	return &MqttConnection{
		client:                 nil,
		server:                 mqttServer,
		port:                   mqttPort,
		subscriptionHandlerMap: make(map[string]func(mqtt.Message)),
	}
}

// Connect to MQTT server. Server URL can be provided via MQTT_SERVER environment variable.
func (m *MqttConnection) Connect(connectTimeoutSeconds time.Duration) error {
	opts := mqtt.NewClientOptions().AddBroker(fmt.Sprintf("%s:%s", m.server, m.port))
	opts.SetConnectTimeout(0)
	opts.SetConnectRetry(true)
	opts.SetConnectRetryInterval(time.Second * 1)
	opts.SetPingTimeout(10 * time.Second)
	opts.SetKeepAlive(10 * time.Second)
	opts.SetAutoReconnect(true)
	opts.SetMaxReconnectInterval(connectTimeoutSeconds)
	opts.SetConnectionLostHandler(func(c mqtt.Client, err error) {
		fmt.Printf("mqtt connection lost error: %s\n" + err.Error())
	})
	opts.SetReconnectingHandler(func(c mqtt.Client, options *mqtt.ClientOptions) {
		fmt.Printf("mqtt reconnecting\n")
	})
	opts.SetOnConnectHandler(func(c mqtt.Client) {
		fmt.Printf("mqtt connected\n")
		for topic, handler := range m.subscriptionHandlerMap {
			err := m.Subscribe(topic, handler)
			if err != nil {
				fmt.Printf("mqtt subsctibing error: %s\n", err.Error())
			}
		}
	})
	m.client = mqtt.NewClient(opts)
	if token := m.client.Connect(); token.Wait() && token.Error() != nil {
		return token.Error()
	}
	return nil
}

func (m *MqttConnection) genericHandler(c mqtt.Client, msg mqtt.Message) {
	if m.subscriptionHandlerMap != nil {
		if _, ok := m.subscriptionHandlerMap[msg.Topic()]; ok {
			m.subscriptionHandlerMap[msg.Topic()](msg)
			return
		}
	}
}

// Subscribe to topic, required handler function for message receive.
func (m *MqttConnection) Subscribe(topic string, handlerFunc func(mqtt.Message)) error {
	if m.client == nil {
		return fmt.Errorf("mqtt client is not connected")
	}
	m.mutex.Lock()
	m.subscriptionHandlerMap[topic] = handlerFunc
	m.mutex.Unlock()
	token := m.client.Subscribe(topic, byte(qos), m.genericHandler)
	if token.Error() != nil {
		return token.Error()
	}
	return nil
}

// Publish message to topic provided
func (m *MqttConnection) Publish(topic string, message []byte) error {
	if m.client == nil {
		return fmt.Errorf("mqtt client is not connected")
	}
	token := m.client.Publish(topic, byte(qos), false, message)
	if token.Error() != nil {
		return token.Error()
	}
	return nil
}

// Close mqtt connection
func (m *MqttConnection) Close() {
	if m.client != nil {
		m.client.Disconnect(0)
	}
}
