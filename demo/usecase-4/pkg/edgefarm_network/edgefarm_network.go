package edgefarm_network

// EdgefarmNetworkIf is an interface to handle the different sources of network connections
type EdgefarmNetworkIf interface {
	Connect(connectTimeoutSeconds int) error
	Subscribe(topic string, handlerFunc interface{}) error
	Publish(topic string, message []byte) error
	Close()
}
