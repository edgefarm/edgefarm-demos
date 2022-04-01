module github.com/edgefarm/train-simulation/demo/usecase-4

go 1.18

replace github.com/edgefarm/train-simulation/demo/common/go => ../common/go

require (
	github.com/eclipse/paho.mqtt.golang v1.3.5
	github.com/edgefarm/train-simulation/demo/common/go v0.0.0-00010101000000-000000000000
)

require (
	github.com/gorilla/websocket v1.4.2 // indirect
	github.com/klauspost/compress v1.15.1 // indirect
	github.com/minio/highwayhash v1.0.2 // indirect
	github.com/nats-io/jwt/v2 v2.2.0 // indirect
	github.com/nats-io/nats.go v1.13.1-0.20220308171302-2f2f6968e98d // indirect
	github.com/nats-io/nkeys v0.3.0 // indirect
	github.com/nats-io/nuid v1.0.1 // indirect
	golang.org/x/crypto v0.0.0-20220112180741-5e0467b6c7ce // indirect
	golang.org/x/net v0.0.0-20211112202133-69e39bad7dc2 // indirect
	golang.org/x/time v0.0.0-20220224211638-0e9765cccd65 // indirect
)
