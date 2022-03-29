FROM golang:1.18.0-alpine3.15 AS builder

RUN apk add make gcc musl-dev
COPY common /code/common
COPY usecase-5 /code/usecase-5
WORKDIR /code/usecase-5 
RUN make 

FROM alpine:3.14
COPY --from=builder /code/usecase-5/bin/nats-mqtt-proxy /nats-mqtt-proxy
CMD ["/nats-mqtt-proxy"]
