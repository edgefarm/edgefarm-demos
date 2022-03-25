package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/eclipse/paho.golang/paho"
	"github.com/edgefarm/train-simulation/demo/usecase-4/receive-position/pkg/edgefarm_network"
)

const (
	gpsMqttTopic      = "environment/location/gps"
	gpsNatsTopic      = "train.gps"
	traceletMqttTopic = "environment/location/tracelet"
	traceletNatsTopic = "train.tracelet"
)

var (
	natsConn              *edgefarm_network.NatsConnection
	connectTimeoutSeconds int = 30
)

type RecvGpsMessage struct {
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

type RecvTraceletMessage struct {
	X       int    `json:"x"`
	Y       int    `json:"y"`
	SiteID  string `json:"site_id"`
	Time    int64  `json:"time"`
	TrainID string `json:"train-id"`
}

type Coordinates struct {
	Lat float64 `json:"lat"`
	Lon float64 `json:"lon"`
}

type SendGpsMessage struct {
	ID          string      `json:"id"`
	Coordinates Coordinates `json:"coordinates"`
}

type SendTraceletMessage struct {
	X       int    `json:"x"`
	Y       int    `json:"y"`
	SiteID  string `json:"site_id"`
	TrainID string `json:"train-id"`
}

func gpsHandler(m *paho.Publish) {
	fmt.Println("Received gps message:", string(m.Payload))

	// Convert byte string to golang struct
	var recMsg RecvGpsMessage
	err := json.Unmarshal([]byte(m.Payload), &recMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Fill forwarding struct with content
	sendMsg := SendGpsMessage{
		ID: recMsg.ID,
		Coordinates: Coordinates{
			Lat: recMsg.Geojson.Geometry.Coordinates[1],
			Lon: recMsg.Geojson.Geometry.Coordinates[0],
		},
	}

	// Convert golang struct to byte string
	stringMessage, err := json.Marshal(sendMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Forward data into the cloud
	err = natsConn.Publish(gpsNatsTopic, stringMessage)
	if err != nil {
		fmt.Println(err)
	}

	fmt.Println("Successfully send to topic", gpsNatsTopic, ", message:", string(stringMessage))
}

func traceletHandler(m *paho.Publish) {
	fmt.Println("Received tracelet message:", string(m.Payload))

	// Convert byte string to golang struct
	var recMsg RecvTraceletMessage
	err := json.Unmarshal([]byte(m.Payload), &recMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Fill forwarding struct with content
	sendMsg := SendTraceletMessage{
		X:       recMsg.X,
		Y:       recMsg.Y,
		SiteID:  recMsg.SiteID,
		TrainID: recMsg.TrainID,
	}

	// Convert golang struct to byte string
	stringMessage, err := json.Marshal(sendMsg)
	if err != nil {
		fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
	}

	// Forward data into the cloud
	err = natsConn.Publish(traceletNatsTopic, stringMessage)
	if err != nil {
		fmt.Println(err)
	}

	fmt.Println("Successfully send to topic", traceletNatsTopic, ", message:", string(stringMessage))
}

func main() {

	// Connect to local NATS server
	natsConn = &edgefarm_network.NatsConnection{}
	err := natsConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	log.Println("Connected to NATS server successfully")
	// Ensure connection closed on exit
	defer natsConn.Close()

	// Connect to train simulation MQTT server
	mqttConn := &edgefarm_network.MqttConnection{}
	err = mqttConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Println("Connected to MQTT Broker successfully")
	// Ensure connection closed on exit
	defer mqttConn.Close()

	// Subscribe to correct MQTT to get qps data from simulations
	// Provide handler function `mqttHandler` which is entered on message receive
	err = mqttConn.Subscribe(gpsMqttTopic, gpsHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", gpsMqttTopic)

	err = mqttConn.Subscribe(traceletMqttTopic, traceletHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", traceletMqttTopic)

	// Listen on signal for termination
	ic := make(chan os.Signal, 1)
	signal.Notify(ic, os.Interrupt, syscall.SIGTERM)
	// Wait for signal to teminate.
	<-ic
	fmt.Println("signal received, exiting")

	os.Exit(0)

}
