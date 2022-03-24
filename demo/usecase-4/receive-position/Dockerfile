FROM golang:1.18 AS builder
WORKDIR /code
COPY . .
RUN make

FROM alpine:3.14
COPY --from=builder /code/bin/receive-position /receive-position
CMD ["/receive-position"]
