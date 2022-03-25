package main

import (
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	edgefarm_network "github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	eventlistener "github.com/edgefarm/train-simulation/demo/usecase-6/pkg/eventlistener"
	nats "github.com/nats-io/nats.go"
)

func handler(msg *nats.Msg) {
	fmt.Printf("Received a message on subject %s: %s\n", msg.Subject, string(msg.Data))
}

func main() {
	exit := make(chan bool)
	network := edgefarm_network.NewNatsConnection()
	err := network.Connect(10)
	if err != nil {
		fmt.Printf("Error connecting to nats: %s\n", err)
		os.Exit(1)
	}
	lis := eventlistener.NewListener(network, configure(), handler)

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
	return
}

// configure reads the environment variable SITE that is in the format <site1>,<site2>,<site3>,...
// and returns a slice of strings with the sites.
func configure() []string {
	sites := ""
	if env := os.Getenv("SITES"); len(env) > 0 {
		sites = env
	}
	return strings.Split(sites, ",")
}
