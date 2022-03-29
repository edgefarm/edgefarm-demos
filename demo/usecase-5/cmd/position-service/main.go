package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/eclipse/paho.golang/paho"
	"github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	"github.com/edgefarm/train-simulation/demo/usecase-5/pkg/position"
)

const (
	// this is followed by the train id
	sendTopicStart = "position."
)

var (
	natsConn                 *edgefarm_network.NatsConnection
	siteManager              *position.SiteManager
	connectTimeoutSeconds    int = 30
	newGpsMessage            chan position.GpsMessage
	newTraceletMessage       chan position.TraceletMessage
	trainIdMessageChannelMap map[string](chan position.TrainPosition)
)

func positionMessageHandler(m *paho.Publish) {
	tp := position.TrainPosition{}
	// Check which type of message is received
	switch m.Topic {
	case position.GpsNatsSubject:
		fmt.Println("Received gps message:", string(m.Payload))
		// convert message to GpsMessage
		var gpsMsg position.GpsMessage
		err := json.Unmarshal([]byte(m.Payload), &gpsMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
			return
		}
		// Convert GpsMessage to TrainPosition
		tp = position.GpsToTrainPositon(gpsMsg)
	case position.TraceletNatsSubject:
		fmt.Println("Received tracelet message:", string(m.Payload))
		// convert message to TraceletMessage
		var traceletMsg position.TraceletMessage
		err := json.Unmarshal([]byte(m.Payload), &traceletMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s", err.Error())
			return
		}
		// Convert TraceletMessage to TrainPosition
		tp, err = position.TraceletToTrainPosition(traceletMsg, siteManager)
		if err != nil {
			fmt.Printf("Error occured during converting. Error: %s", err.Error())
			return
		}
	default:
		fmt.Printf("Unknown message received: %s", m.Topic)
		return
	}

	// Check if message channel exists for this train id
	if _, ok := trainIdMessageChannelMap[tp.ID]; !ok {
		// Create new channel for this train id
		tpChan := make(chan position.TrainPosition)
		trainIdMessageChannelMap[tp.ID] = tpChan
		// Start a new goroutine to handle this train id
		go trainMessageHandler(tpChan)
	}

	// Send message to channel in a goroutine
	go func() {
		trainIdMessageChannelMap[tp.ID] <- tp
	}()
}

func publishTrainPosition(msg position.TrainPosition) {
	// create message
	msgBytes, err := json.Marshal(msg)
	if err != nil {
		fmt.Printf("Error occured during marshaling. Error: %s", err.Error())
	}
	// publish message
	natsConn.Publish(sendTopicStart+msg.ID, msgBytes)
}

func trainMessageHandler(msgChan chan position.TrainPosition) {
	lastMsg := position.TrainPosition{}
	for {
		select {
		case msg := <-msgChan:

			// Check if last message is empty
			if lastMsg != (position.TrainPosition{}) {

				// If both messages are from the same message type, send the last message and update lastMsg
				if lastMsg.Position.Hres == msg.Position.Hres {
					publishTrainPosition(lastMsg)
					lastMsg = msg

				} else {
					// Entering this block means that both messages differ in message type
					// lastMessage = tracelet message && msg = gps message
					// lastMessage = gps message && msg = tracelet message
					// In case the types differ, send the tracelet message and clear lastMsg
					switch {
					case lastMsg.Position.Hres == true:
						// lastMsg was tracelet message
						publishTrainPosition(lastMsg)
					case msg.Position.Hres == true:
						// msg is tracelet message
						publishTrainPosition(msg)
					}
					lastMsg = position.TrainPosition{}
				}

			} else {
				// store this message in lastMsg
				lastMsg = msg
			}

		case <-time.After(time.Second * 2):
			fmt.Println("Send out remaining message")
			// if lastMessage is not empty, send it out
			if lastMsg != (position.TrainPosition{}) {
				publishTrainPosition(lastMsg)
			}
		}
	}
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

	// Create a site manager
	siteManager, err := position.NewSiteManager()
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}

	// Register handler for register messages
	err = natsConn.Subscribe(position.RegisterSiteNatsTopic, siteManager.RegisterHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", position.RegisterSiteNatsTopic)

	// Subscribe to correct MQTT topics to get qps and tracelet data from simulations
	// Provide handler function `mqttHandler` which is entered on message receive
	err = natsConn.Subscribe(position.GpsNatsSubject, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", position.GpsNatsSubject)

	err = natsConn.Subscribe(position.TraceletNatsSubject, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s", position.TraceletNatsSubject)

	// Listen on signal for termination
	ic := make(chan os.Signal, 1)
	signal.Notify(ic, os.Interrupt, syscall.SIGTERM)
	<-ic
	fmt.Println("signal received, exiting")
	os.Exit(0)
}
