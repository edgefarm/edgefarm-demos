package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	"github.com/edgefarm/train-simulation/demo/common/go/pkg/siteevent"
	"github.com/edgefarm/train-simulation/demo/usecase-5/pkg/position"
	"github.com/nats-io/nats.go"
)

const (
	// this is followed by the train id
	sendSubjectStart = "position."
)

var (
	mutex                    sync.Mutex
	natsConn                 *edgefarm_network.NatsConnection
	siteManager              *position.SiteManager
	connectTimeoutSeconds    int = 30
	newGpsMessage            chan position.GpsMessage
	newTraceletMessage       chan position.TraceletMessage
	trainIdMessageChannelMap map[string](chan position.TrainPosition)
)

func positionMessageHandler(msg *nats.Msg) {
	tp := position.TrainPosition{}
	// Check which type of message is received
	switch msg.Subject {
	case position.TraceletNatsSubject:
		fmt.Println("Received tracelet message:", string(msg.Data))
		// convert message to TraceletMessage
		var traceletMsg position.TraceletMessage
		err := json.Unmarshal(msg.Data, &traceletMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s\n", err.Error())
			return
		}
		// Convert TraceletMessage to TrainPosition
		tp, err = position.TraceletToTrainPosition(traceletMsg, siteManager)
		if err != nil {
			fmt.Printf("Error occured during converting. Error: %s\n", err.Error())
			return
		}
	case position.GpsNatsSubject:
		fmt.Println("Received gps message:", string(msg.Data))
		// convert message to GpsMessage
		var gpsMsg position.GpsMessage
		err := json.Unmarshal(msg.Data, &gpsMsg)
		if err != nil {
			fmt.Printf("Error occured during unmarshaling. Error: %s\n", err.Error())
			return
		}
		// Convert GpsMessage to TrainPosition
		tp = position.GpsToTrainPositon(gpsMsg)
	default:
		fmt.Printf("Unknown message received: %s\n", msg.Subject)
		return
	}

	// Check if message channel exists for this train id
	if _, ok := trainIdMessageChannelMap[tp.ID]; !ok {
		// Create new channel for this train id
		tpChan := make(chan position.TrainPosition, 200)
		mutex.Lock()
		trainIdMessageChannelMap[tp.ID] = tpChan
		mutex.Unlock()
		// Start a new goroutine to handle this train id
		go trainMessageHandler(tpChan)
	}
	mutex.Lock()
	trainIdMessageChannelMap[tp.ID] <- tp
	mutex.Unlock()
}

func publishTrainPosition(msg position.TrainPosition, lastSiteId string) string {
	// create message
	msgBytes, err := json.Marshal(msg)
	if err != nil {
		fmt.Printf("Error occured during marshaling. Error: %s\n", err.Error())
	}
	// publish message
	natsConn.Publish(sendSubjectStart+msg.ID, msgBytes)

	// Check if there is a site state change
	if msg.SiteID != lastSiteId {
		// Send site event "leave" to last site only if this is not ""
		if lastSiteId != "" {
			fmt.Printf("Train %s left site %s.\n", msg.ID, lastSiteId)
			siteEvent := siteevent.Event{
				Train: msg.ID,
				Event: "left",
				Site:  lastSiteId,
			}
			publishSiteEvent(siteEvent)
		}
		// Send site event "enter" to current site only if this is not ""
		if msg.SiteID != "" {
			fmt.Printf("Train %s entered site %s.\n", msg.ID, msg.SiteID)
			siteEvent := siteevent.Event{
				Train: msg.ID,
				Event: "entered",
				Site:  msg.SiteID,
			}
			publishSiteEvent(siteEvent)
		}

		return msg.SiteID

	}
	return lastSiteId
}

func publishSiteEvent(msg siteevent.Event) {
	// create message
	msgBytes, err := json.Marshal(msg)
	if err != nil {
		fmt.Printf("Error occured during marshaling. Error: %s\n", err.Error())
	}
	// publish message
	natsConn.Publish(siteevent.NatsSubject+"."+msg.Site, msgBytes)
}

func trainMessageHandler(msgChan chan position.TrainPosition) {
	lastMsg := position.TrainPosition{}
	lastSiteId := ""
	for {
		select {
		case msg := <-msgChan:
			// Check if last message is empty
			if lastMsg != (position.TrainPosition{}) {
				// If both messages are from the same message type, send the last message and update lastMsg
				if lastMsg.Position.Hres == msg.Position.Hres {
					fmt.Println("Sending last message:", lastMsg)
					lastSiteId = publishTrainPosition(lastMsg, lastSiteId)
					lastMsg = msg
				} else {
					// Entering this block means that both messages differ in message type
					// lastMessage = tracelet message && msg = gps message
					// lastMessage = gps message && msg = tracelet message
					// In case the types differ, send the tracelet message and clear lastMsg
					switch {
					case lastMsg.Position.Hres == true:
						fmt.Println("Sending tracelet message:", lastMsg)
						// lastMsg was tracelet message
						lastSiteId = publishTrainPosition(lastMsg, lastSiteId)
					case msg.Position.Hres == true:
						fmt.Println("Sending tracelet message:", msg)
						// msg is tracelet message
						lastSiteId = publishTrainPosition(msg, lastSiteId)
					}
					lastMsg = position.TrainPosition{}
				}

			} else {
				// store this message in lastMsg
				lastMsg = msg
			}

		case <-time.After(time.Second * 2):
			// if lastMessage is not empty, send it out
			if lastMsg != (position.TrainPosition{}) {
				fmt.Println("Send out remaining message")
				lastSiteId = publishTrainPosition(lastMsg, lastSiteId)
				lastMsg = position.TrainPosition{}
			}
		}
	}
}

func main() {

	// Connect to NATS server
	natsConn = edgefarm_network.NewNatsConnection()
	err := natsConn.Connect(connectTimeoutSeconds)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	log.Println("Connected to NATS server successfully")

	// Create a site manager
	siteManager, err = position.NewSiteManager()
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}

	// Register handler for register messages
	err = natsConn.Subscribe(position.RegisterSiteNatsTopic, siteManager.RegisterHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s\n", position.RegisterSiteNatsTopic)

	// Subscribe to correct MQTT topics to get qps and tracelet data from simulations
	// Provide handler function `mqttHandler` which is entered on message receive
	trainIdMessageChannelMap = make(map[string](chan position.TrainPosition))
	err = natsConn.Subscribe(position.GpsNatsSubject, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s\n", position.GpsNatsSubject)

	err = natsConn.Subscribe(position.TraceletNatsSubject, positionMessageHandler)
	if err != nil {
		log.Fatalf("Exiting: %v", err)
	}
	fmt.Printf("Subscribed to %s\n", position.TraceletNatsSubject)

	// Listen on signal for termination
	ic := make(chan os.Signal, 1)
	signal.Notify(ic, os.Interrupt, syscall.SIGTERM)
	<-ic
	fmt.Println("signal received, exiting")
	// Close nats connection
	natsConn.Close()
	os.Exit(0)
}
