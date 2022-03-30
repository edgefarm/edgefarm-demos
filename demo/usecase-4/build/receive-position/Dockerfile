FROM golang:1.18 AS builder
WORKDIR /usecase
COPY common/go /common/go
COPY usecase-4 /usecase
RUN make

FROM alpine:3.14
COPY --from=builder /usecase/bin/receive-position /receive-position
CMD ["/receive-position"]
