package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/eclipse/paho.golang/paho"
	"github.com/edgefarm/train-simulation/demo/usecase-4/receive-position/pkg/edgefarm_network"
)

const (
	recvTraceletTopic = "train.tracelet"
	recvGpsTopic      = "train.gps"
	// this is followed by the train id
	sendTopicStart = "position."
	// radius of the earth in kilometer required to calculate meter to coordinatess
	earth = 6378.137
)

var (
	natsConn              *edgefarm_network.NatsConnection
	connectTimeoutSeconds int = 30
	newGpsMessage         chan GpsMessage
	newTraceletMessage    chan TraceletMessage
)

type Coordinates struct {
	Lat float64 `json:"lat"`
	Lon float64 `json:"lon"`
}

type GpsMessage struct {
	ID          string      `json:"id"`
	Coordinates Coordinates `json:"coordinates"`
}

type TraceletMessage struct {
	X       int    `json:"x"`
	Y       int    `json:"y"`
	SiteID  string `json:"site_id"`
	TrainID string `json:"train-id"`
}

type Position struct {
	Lat  float64 `json:"lat"`
	Lon  float64 `json:"lon"`
	Hres bool    `json:"hres"`
}

type TrainPosition struct {
	ID       string   `json:"id"`
	Position Position `json:"position"`
}

type SiteConfig struct {
	ID   string      `json:"id"`
	Zero Coordinates `json:"zero"`
}

func positionMessageHandler(m *paho.Publish) {
	// Check which type of message is received
	switch m.Topic {
	case recvGpsTopic:
		fmt.Println("Received gps message:", string(m.Payload))
		// convert message to GpsMessage
		var gpsMsg GpsMessage
		err := json.Unmarshal([]byte(m.Payload), &gpsMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
		}
	case recvTraceletTopic:
		fmt.Println("Received tracelet message:", string(m.Payload))
		// convert message to TraceletMessage
		var traceletMsg TraceletMessage
		err := json.Unmarshal([]byte(m.Payload), &traceletMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
		}
	default:
		fmt.Printf("Unknown message received: %s", m.Topic)
	}
}

// convert GpsMessage to Position struct
func gpsToPositon(gpsData GpsMessage) Position {
	return Position{
		Lat:  gpsData.Coordinates.Lat,
		Lon:  gpsData.Coordinates.Lon,
		Hres: false,
	}
}

// convert TraceletMessage to Position struct
func tracetletToPosition(traceletData TraceletMessage) Position {
	// get zero point of tracelet id from database
	zero := getZeroPoint(traceletData.SiteID)
	// calculate position
	return Position{
		Lat:  zero.Lat + (float64(traceletData.Y)/earth)*(180/math.Pi),
		Lon:  zero.Lon + (float64(traceletData.Y)/earth)*(180/math.Pi)/math.Cos(zero.Lat*math.Pi/180),
		Hres: true,
	}
}

func getZeroPoint(siteId string) Coordinates {
	// currently return 0,0
	return Coordinates{0, 0}
}

func main() {

	// Connect to NATS server
	natsConn = &edgefarm_network.NatsConnection{}
	err := natsConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	log.Println("Connected to NATS server successfully")
	// Ensure connection closed on exit
	defer natsConn.Close()

	// Create channel for received messages
	newGpsMessage = make(chan GpsMessage, 100)
	newTraceletMessage = make(chan TraceletMessage, 100)

	// Subscribe to correct MQTT topics to get qps and tracelet data from simulations
	// Provide handler function `mqttHandler` which is entered on message receive
	err = natsConn.Subscribe(recvGpsTopic, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", recvGpsTopic)

	err = natsConn.Subscribe(recvTraceletTopic, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", recvGpsTopic)

	// Listen on signal for termination
	ic := make(chan os.Signal, 1)
	signal.Notify(ic, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-ic
		fmt.Println("signal received, exiting")
		os.Exit(0)
	}()

	for {
		// do a switch case on message channels with timeout
		select {
		case <-newGpsMessage:
			fmt.Println("Received gps message on channel")
		case <-newTraceletMessage:
			fmt.Println("Received tracelet message on channel")
		case <-time.After(time.Second * 2):
			fmt.Println("Timeout")
		}
	}
}
