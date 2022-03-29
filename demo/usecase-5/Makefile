BIN_DIR ?= bin
VERSION ?= $(shell git describe --match=NeVeRmAtCh --always --abbrev=8 --dirty)
GO_LDFLAGS = -tags 'netgo osusergo static_build'

all: tidy test build ## default target: tidy, test, build

tidy: ## ensures go dependencies are up to date
	go mod tidy
	go mod vendor

build: test
	GOOS=linux go build $(GO_LDFLAGS) -o ${BIN_DIR}/position-service cmd/position-service/main.go
	GOOS=linux go build $(GO_LDFLAGS) -o ${BIN_DIR}/receive-highres-position cmd/receive-highres-position/main.go
	GOOS=linux go build $(GO_LDFLAGS) -o ${BIN_DIR}/maintenance-hall cmd/maintenance-hall/main.go
	GOOS=linux go build $(GO_LDFLAGS) -o ${BIN_DIR}/nats-mqtt-proxy cmd/nats-mqtt-proxy/main.go

test: tidy ## run go tests
	go test ./...

clean: ## cleanup
	rm -rf ${BIN_DIR}/position-service

docker-amd64: position-service-docker-amd64 receive-highres-position-docker-amd64 maintenance-hall-docker-amd64 ## creates docker images for amd64 (prefix dev-)

position-service-docker-amd64: tidy test ## creates docker image of position-service for amd64 (prefix dev-)
	docker build -f build/position-service/Dockerfile -t ci4rail/dev-position-service:${VERSION} -t ci4rail/dev-position-service:latest .. 
	docker push ci4rail/dev-position-service:${VERSION}
	docker push ci4rail/dev-position-service:latest

receive-highres-position-docker-amd64: tidy test ## creates docker image of receive-highres-position for amd64 (prefix dev-)
	docker build -f build/receive-highres-position/Dockerfile -t ci4rail/dev-receive-highres-position:${VERSION} -t ci4rail/dev-receive-highres-position:latest ..
	docker push ci4rail/dev-receive-highres-position:${VERSION}
	docker push ci4rail/dev-receive-highres-position:latest

maintenance-hall-docker-amd64: tidy test ## creates docker images for amd64 (prefix dev-)
	docker build -f build/maintenance-hall/Dockerfile -t ci4rail/dev-maintenance-hall:${VERSION} -t ci4rail/dev-maintenance-hall:latest ../
	docker push ci4rail/dev-maintenance-hall:${VERSION}
	docker push ci4rail/dev-maintenance-hall:latest

nats-mqtt-proxy-docker-amd64: tidy test ## creates docker images for amd64 (prefix dev-)
	docker build -f build/nats-mqtt-proxy/Dockerfile -t ci4rail/dev-nats-mqtt-proxy:${VERSION} -t ci4rail/dev-nats-mqtt-proxy:latest ../
	docker push ci4rail/dev-nats-mqtt-proxy:${VERSION}
	docker push ci4rail/dev-nats-mqtt-proxy:latest


.PHONY: test clean build all tidy docker-amd64 position-service-docker-amd64 receive-highres-position-docker-amd64 maintenance-hall-docker-amd64 nats-mqtt-proxy-docker-amd64

help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make [target]\033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m\t %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
