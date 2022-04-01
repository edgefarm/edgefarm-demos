package main

import (
	"fmt"
	"log"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
)

func main() {
	client := edgefarm_network.NewMqttConnection()
	err := client.Connect(time.Second * 10)
	if err != nil {
		log.Panic(err)
	}
	wait := make(chan interface{})
	err = client.Subscribe("test", func(m mqtt.Message) {
		fmt.Println(m.Topic(), string(m.Payload()))
		wait <- nil
	})
	if err != nil {
		log.Panic(err)
	}
	err = client.Publish("test", []byte("hello world"))
	if err != nil {
		log.Panic(err)
	}
	<-wait
}
