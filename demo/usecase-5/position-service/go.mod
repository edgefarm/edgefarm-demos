module github.com/edgefarm/train-simulation/demo/usecase-5/position-service

go 1.18

require (
	github.com/eclipse/paho.golang v0.10.0
	github.com/edgefarm/train-simulation/demo/usecase-4/receive-position v0.0.0-00010101000000-000000000000
)

require (
	github.com/klauspost/compress v1.14.4 // indirect
	github.com/minio/highwayhash v1.0.2 // indirect
	github.com/nats-io/jwt/v2 v2.2.1-0.20220113022732-58e87895b296 // indirect
	github.com/nats-io/nats.go v1.13.1-0.20220308171302-2f2f6968e98d // indirect
	github.com/nats-io/nkeys v0.3.0 // indirect
	github.com/nats-io/nuid v1.0.1 // indirect
	golang.org/x/crypto v0.0.0-20220112180741-5e0467b6c7ce // indirect
	golang.org/x/sync v0.0.0-20201207232520-09787c993a3a // indirect
	golang.org/x/sys v0.0.0-20220111092808-5a964db01320 // indirect
	golang.org/x/time v0.0.0-20211116232009-f0f3c7e86c11 // indirect
)

replace github.com/edgefarm/train-simulation/demo/usecase-4/receive-position => ../../usecase-4/receive-position

replace github.com/edgefarm/train-simulation/demo/usecase-5/receive-highres-position => ../receive-highres-position
