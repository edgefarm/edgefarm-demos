package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	edgefarm_network "github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	env "github.com/edgefarm/train-simulation/demo/common/go/pkg/env"
	eventlistener "github.com/edgefarm/train-simulation/demo/usecase-5/pkg/eventlistener"
	nats "github.com/nats-io/nats.go"
)

var (
	natsConn *edgefarm_network.NatsConnection
	mqttConn *edgefarm_network.MqttConnection
)

func handler(msg *nats.Msg) {
	err := mqttConn.Publish(msg.Subject, msg.Data)
	if err != nil {
		fmt.Println(err)
	}
}

func main() {
	var err error
	exit := make(chan bool)
	natsConn = edgefarm_network.NewNatsConnection()
	err = natsConn.Connect(10)
	if err != nil {
		fmt.Printf("Error connecting to nats: %s\n", err)
		os.Exit(1)
	}

	mqttConn = edgefarm_network.NewMqttConnection()
	err = mqttConn.Connect(10)
	if err != nil {
		fmt.Printf("Error connecting to mqtt: %s\n", err)
		os.Exit(1)
	}

	subs := []string{configure()}
	lis := eventlistener.NewListener(natsConn, subs, handler)

	// Listen on signal for termination
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sig
		lis.Close()
		exit <- true
		fmt.Println("signal received, exiting")
	}()
	<-exit
	os.Exit(0)
}

func configure() string {
	return env.GetEnvVar("SUBJECT", "site.register")
}
