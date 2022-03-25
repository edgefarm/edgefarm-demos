BIN_DIR ?= bin
VERSION ?= $(shell git describe --match=NeVeRmAtCh --always --abbrev=8 --dirty)
GO_LDFLAGS = -tags 'netgo osusergo static_build'
BINARY = maintenance-hall


all: tidy test build ## default target: tidy, test, build

tidy: ## ensures go dependencies are up to date
	go mod tidy
	go mod vendor

build: test ## build binary
	echo ${BINARY}
	GOOS=linux go build $(GO_LDFLAGS) -o ${BIN_DIR}/${BINARY} cmd/${BINARY}/main.go


test: tidy ## run go tests
	go test ./...

clean: ## cleanup
	rm -rf ${BIN_DIR}/${BINARY}

docker-amd64: tidy test ## creates docker images for amd64 (prefix dev-)
	docker build -f Dockerfile -t ci4rail/dev-${BINARY}:${VERSION} -t ci4rail/dev-${BINARY}:latest . 
	docker push ci4rail/dev-${BINARY}:${VERSION}
	docker push ci4rail/dev-${BINARY}:latest

.PHONY: test clean build all tidy docker-amd64

help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make [target]\033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m\t %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
