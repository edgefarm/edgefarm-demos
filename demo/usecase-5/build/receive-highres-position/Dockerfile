FROM golang:1.18 AS builder
WORKDIR /code
COPY . .
RUN make

FROM alpine:3.14
COPY --from=builder /code/bin/receive-highres-position /receive-highres-position
CMD ["/receive-highres-position"]
