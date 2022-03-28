FROM golang:1.18.0-alpine3.15 AS builder

RUN go install github.com/mkaz/lanyon@latest

RUN apk add make gcc musl-dev
COPY common /code/common
COPY usecase-6 /code/usecase-6
WORKDIR /code/usecase-6 
RUN make

FROM alpine:3.14
RUN apk add bash
COPY --from=builder /code/usecase-6/web /web
COPY --from=builder /code/usecase-6/bin/maintenance-hall /maintenance-hall
COPY --from=builder /go/bin/lanyon /usr/local/bin/lanyon
COPY usecase-6/build/entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
