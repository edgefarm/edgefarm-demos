package edgefarm_network

import (
	"context"
	"fmt"
	"log"
	"time"

	dapr "github.com/dapr/go-sdk/client"
	common "github.com/dapr/go-sdk/service/common"
	daprd_grpc "github.com/dapr/go-sdk/service/grpc"
	daprd_http "github.com/dapr/go-sdk/service/http"
)

type subscription struct {
	sub     *common.Subscription
	handler common.TopicEventHandler
}

type serviceType int

const (
	GRPC serviceType = iota
	HTTP
)

const (
	connectTimeoutSeconds = 3
)

type DaprGrpc struct {
	service        *common.Service
	client         *dapr.Client
	serviceAddress string
	subscriptions  []subscription
	serviceType    serviceType
}

type daprGrpcOption func(*DaprGrpc)

func WithSubscription(pubsubName string, topicName string, handler common.TopicEventHandler) daprGrpcOption {
	return func(d *DaprGrpc) {
		d.subscriptions = append(d.subscriptions, subscription{
			sub: &common.Subscription{
				PubsubName: pubsubName,
				Topic:      topicName,
			},
			handler: handler,
		})
	}
}

func WithServiceType(t serviceType) daprGrpcOption {
	return func(d *DaprGrpc) {
		d.serviceType = t
	}
}

func NewDaprGrpc(opts ...daprGrpcOption) (*DaprGrpc, error) {
	serviceAddress := getEnvVar("DAPR_SERVER", "localhost:50001")
	c := &DaprGrpc{
		serviceAddress: serviceAddress,
		subscriptions:  []subscription{},
		serviceType:    GRPC,
	}
	for _, opt := range opts {
		opt(c)
	}
	return c, nil
}

func (d *DaprGrpc) Start() error {
	// instanciate client for publishing
	client, err := newClient(d.serviceAddress)
	if err != nil {
		return fmt.Errorf("failed to start the dapr service: %v", err)
	}
	d.client = client

	// starting service for receiving subscriptions
	var service common.Service
	if d.serviceType == GRPC {
		service, err = daprd_grpc.NewService(d.serviceAddress)
	} else {
		service = daprd_http.NewService(d.serviceAddress)
	}
	if err != nil {
		return fmt.Errorf("failed to create the dapr service: %v", err)
	}
	d.service = &service
	for _, subscription := range d.subscriptions {
		err := service.AddTopicEventHandler(subscription.sub, subscription.handler)
		if err != nil {
			log.Printf("failed to subscribe to topic %s: %v", subscription.sub.Topic, err)
		}
	}
	err = (*d.service).Start()
	if err != nil {
		return fmt.Errorf("failed to start the dapr service: %v", err)
	}
	return nil
}

func (d *DaprGrpc) Publish(pubsubName, topicName string, data []byte) error {
	return (*d.client).PublishEvent(context.Background(), pubsubName, topicName, data, nil)
}

func (d *DaprGrpc) Close() {
	if d.client != nil {
		(*d.client).Close()
	}
	if d.service != nil {
		(*d.service).Stop()
	}
}

func newClient(serviceAddress string) (*dapr.Client, error) {
	daprConnection := make(chan dapr.Client)

	go func() {
		for {
			log.Printf("\rConnecting to dapr server: %s\n", serviceAddress)
			client, err := dapr.NewClientWithAddress(serviceAddress)
			if err != nil {
				log.Printf("Connect failed to %s: %s\n", serviceAddress, err)
			} else {
				log.Printf("Connected to '%s'\n", serviceAddress)
				daprConnection <- client
				return
			}
			func() {
				for i := connectTimeoutSeconds; i >= 0; i-- {
					time.Sleep(time.Second)
					log.Printf("\rReconnecting in %2d seconds", i)
				}
				log.Println("")
			}()
		}
	}()

	client := <-daprConnection
	return &client, nil
}
