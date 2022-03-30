FROM golang:1.18 AS builder
WORKDIR /usecase
COPY common/go /common/go
COPY usecase-5 /usecase
RUN make

FROM alpine:3.14
COPY --from=builder /usecase/bin/position-service /position-service
CMD ["/position-service"]
