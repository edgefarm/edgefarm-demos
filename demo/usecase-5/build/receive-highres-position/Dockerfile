FROM golang:1.18 AS builder
WORKDIR /usecase
COPY common/go /common/go
COPY usecase-5 /usecase
RUN make

FROM alpine:3.14
COPY --from=builder /usecase/bin/receive-highres-position /receive-highres-position
CMD ["/receive-highres-position"]
