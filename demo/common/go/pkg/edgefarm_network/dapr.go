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
	env "github.com/edgefarm/train-simulation/demo/common/go/pkg/env"
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

type Dapr struct {
	service        *common.Service
	client         *dapr.Client
	serviceAddress string
	subscriptions  []subscription
	serviceType    serviceType
	servicePort    string
	daprPort       string
}

type DaprOption func(*Dapr)

func WithSubscription(pubsubName string, topicName string, handler common.TopicEventHandler) DaprOption {
	return func(d *Dapr) {
		d.subscriptions = append(d.subscriptions, subscription{
			sub: &common.Subscription{
				PubsubName: pubsubName,
				Topic:      topicName,
			},
			handler: handler,
		})
	}
}

func WithServiceType(t serviceType) DaprOption {
	return func(d *Dapr) {
		d.serviceType = t
		if t == GRPC {
			d.servicePort = env.GetEnvVar("DAPR_GRPC_PORT", "3500")
		} else {
			d.servicePort = env.GetEnvVar("DAPR_HTTP_PORT", "3501")
		}
	}
}

func NewDapr(opts ...DaprOption) (*Dapr, error) {
	serviceAddress := env.GetEnvVar("DAPR_SERVER", "localhost")
	daprPort := env.GetEnvVar("DAPR_PORT", "50001")

	c := &Dapr{
		serviceAddress: serviceAddress,
		subscriptions:  []subscription{},
		serviceType:    GRPC,
		daprPort:       daprPort,
		servicePort:    "3500",
	}
	for _, opt := range opts {
		opt(c)
	}
	return c, nil
}

func (d *Dapr) Start() error {
	// instanciate client for publishing
	err := d.newClient()
	if err != nil {
		return fmt.Errorf("failed to start the dapr service: %v", err)
	}

	// starting service for receiving subscriptions
	var service common.Service
	addr := fmt.Sprintf("%s:%s", d.serviceAddress, d.daprPort)
	if d.serviceType == GRPC {
		service, err = daprd_grpc.NewService(addr)
	} else {
		service = daprd_http.NewService(addr)
	}
	if err != nil {
		return fmt.Errorf("failed to create the dapr service: %v", err)
	}
	d.service = &service
	for _, subscription := range d.subscriptions {
		fmt.Println("subscribing to: ", subscription.sub.Topic)
		err := service.AddTopicEventHandler(subscription.sub, subscription.handler)
		if err != nil {
			log.Printf("failed to subscribe to topic %s: %v", subscription.sub.Topic, err)
		}
	}
	go (*d.service).Start()

	return nil
}

func (d *Dapr) Publish(pubsubName, topicName string, data []byte) error {
	return (*d.client).PublishEvent(context.Background(), pubsubName, topicName, data)
}

func (d *Dapr) Close() {
	if d.client != nil {
		(*d.client).Close()
	}
	if d.service != nil {
		(*d.service).Stop()
	}
}

func (d *Dapr) newClient() error {
	daprConnection := make(chan dapr.Client)
	addr := fmt.Sprintf("%s:%s", d.serviceAddress, d.servicePort)
	go func() {
		for {
			log.Printf("\rConnecting to dapr server: %s\n", addr)

			client, err := dapr.NewClientWithAddress(addr)
			if err != nil {
				log.Printf("Connect failed to %s: %s\n", addr, err)
			} else {
				log.Printf("Connected to '%s'\n", addr)
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

	c := <-daprConnection
	d.client = &c
	return nil
}
