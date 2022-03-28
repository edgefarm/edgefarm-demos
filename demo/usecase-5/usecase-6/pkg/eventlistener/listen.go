package eventlistener

import (
	"log"

	edgefarm_network "github.com/edgefarm/train-simulation/demo/common/go/pkg/edgefarm_network"
	nats "github.com/nats-io/nats.go"
)

// Listener listens for events from the edgefarm network regarding to specific subjects
type Listener struct {
	NatsConn *edgefarm_network.NatsConnection
	Subjects []string
}

func NewListener(natsConn *edgefarm_network.NatsConnection, subjects []string, handler func(*nats.Msg)) *Listener {
	lis := &Listener{
		NatsConn: natsConn,
		Subjects: subjects,
	}
	for _, subject := range subjects {
		err := natsConn.Subscribe(subject, handler)
		if err != nil {
			log.Fatalf("err: %s", err)
		}
	}
	return lis
}

func (l *Listener) Close() {
	l.NatsConn.Close()
}
