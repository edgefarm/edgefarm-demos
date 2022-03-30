module github.com/edgefarm/train-simulation/demo/usecase-4

go 1.18

replace github.com/edgefarm/train-simulation/demo/common/go => ../common/go

require (
	github.com/eclipse/paho.golang v0.10.0
	github.com/edgefarm/train-simulation/demo/common/go v0.0.0-00010101000000-000000000000
	github.com/nats-io/nats.go v1.13.1-0.20220308171302-2f2f6968e98d
)

require (
	github.com/klauspost/compress v1.15.1 // indirect
	github.com/minio/highwayhash v1.0.2 // indirect
	github.com/nats-io/jwt/v2 v2.2.0 // indirect
	github.com/nats-io/nkeys v0.3.0 // indirect
	github.com/nats-io/nuid v1.0.1 // indirect
	golang.org/x/crypto v0.0.0-20220112180741-5e0467b6c7ce // indirect
	golang.org/x/sync v0.0.0-20201207232520-09787c993a3a // indirect
	golang.org/x/time v0.0.0-20220224211638-0e9765cccd65 // indirect
)
