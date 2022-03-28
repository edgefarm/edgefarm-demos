package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/dapr/go-sdk/service/common"
	edgefarm_network "github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	env "github.com/edgefarm/train-simulation/demo/common/go/pkg/env"
	markdown "github.com/edgefarm/train-simulation/demo/usecase-5/pkg/markdown"
	siteevent "github.com/edgefarm/train-simulation/demo/usecase-5/pkg/siteevent"
)

var (
	m *markdown.Markdown
)

func handler(ctx context.Context, e *common.TopicEvent) (retry bool, err error) {
	event, err := siteevent.Unmarshal(e.RawData)
	if err != nil {
		fmt.Printf("Unmarshal failed: %s\n", err)
		return false, err
	}
	m.Add([]string{time.Now().Format("01-02-2006 15:04:05"), event.Site, event.Train, event.Event})
	log.Printf("Train %s, Site %s, Event %s\n", event.Train, event.Site, event.Event)

	err = m.Print()
	if err != nil {
		fmt.Printf("Print failed: %s\n", err)
		return false, err
	}
	return false, nil
}

func main() {
	var err error
	m, err = markdown.NewMarkdown("web/public/index.md")
	if err != nil {
		log.Fatalf("err: %s", err)
	}
	m.Print()
	pubsub := env.GetEnvVar("PUBSUB", "")
	if pubsub == "" {
		log.Fatalf("PUBSUB is not set")
	}

	exit := make(chan bool)
	opts := []edgefarm_network.DaprOption{}
	opts = append(opts, edgefarm_network.WithServiceType(edgefarm_network.GRPC))
	for _, site := range configure() {
		fmt.Printf("Subscribing to pubsub %s with topic %s\n", pubsub, site)
		opts = append(opts, edgefarm_network.WithSubscription(pubsub, site, handler))
	}

	network, err := edgefarm_network.NewDapr(opts...)
	if err != nil {
		log.Fatalf("err: %s", err)
	}

	err = network.Start()
	if err != nil {
		fmt.Printf("Error connecting to nats: %s\n", err)
		os.Exit(1)
	}

	// Listen on signal for termination
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sig
		exit <- true
		fmt.Println("signal received, exiting")
	}()
	<-exit
	return
}

// configure reads the environment variable SITE that is in the format <site1>,<site2>,<site3>,...
// and returns a slice of strings with the sites.
func configure() []string {
	sites := env.GetEnvVar("SITES", "")
	return strings.Split(sites, ",")
}
