package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/eclipse/paho.golang/paho"
	"github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
)

const (
	mqttTopic = "environment/location/gps"
)

var (
	natsConn              *edgefarm_network.NatsConnection
	connectTimeoutSeconds int = 30
)

type RecMessage struct {
	Geojson struct {
		Type       string `json:"type"`
		Properties struct {
		} `json:"properties"`
		Geometry struct {
			Type        string    `json:"type"`
			Coordinates []float64 `json:"coordinates"`
		} `json:"geometry"`
	} `json:"geojson"`
	ID   string `json:"id"`
	Time int64  `json:"time"`
}

type Position struct {
	Lat  float64 `json:"lat"`
	Lon  float64 `json:"lon"`
	Hres bool    `json:"hres"`
}

type SendMessage struct {
	ID       string   `json:"id"`
	Position Position `json:"position"`
}

func mqttHandler(m *paho.Publish) {
	fmt.Println("Received message:", string(m.Payload))

	// Convert byte string to golang struct
	var recMsg RecMessage
	err := json.Unmarshal([]byte(m.Payload), &recMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Fill forwarding struct with content
	sendMsg := SendMessage{
		ID: recMsg.ID,
		Position: Position{
			Lat:  recMsg.Geojson.Geometry.Coordinates[1],
			Lon:  recMsg.Geojson.Geometry.Coordinates[0],
			Hres: false,
		},
	}

	// Convert golang struct to byte string
	stringMessage, err := json.Marshal(sendMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Forward data into the cloud
	topic := fmt.Sprintf("position.%s", recMsg.ID)
	err = natsConn.Publish(topic, stringMessage)
	if err != nil {
		fmt.Println(err)
	}

	fmt.Println("Successfully send to topic", topic, ", message:", string(stringMessage))
}

func main() {

	// Connect to local NATS server
	natsConn = edgefarm_network.NewNatsConnection()
	err := natsConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	log.Println("Connected to NATS server successfully")
	// Ensure connection closed on exit
	defer natsConn.Close()

	// Connect to train simulation MQTT server
	mqttConn := edgefarm_network.NewMqttConnection()
	err = mqttConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Println("Connected to MQTT Broker successfully")
	// Ensure connection closed on exit
	defer mqttConn.Close()

	// Subscribe to correct MQTT to get qps data from simulations
	// Provide handler function `mqttHandler` which is entered on message receive
	err = mqttConn.Subscribe(mqttTopic, mqttHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", mqttTopic)

	// Listen on signal for termination
	ic := make(chan os.Signal, 1)
	signal.Notify(ic, os.Interrupt, syscall.SIGTERM)
	// Wait for signal to teminate.
	<-ic
	fmt.Println("signal received, exiting")

	os.Exit(0)

}
