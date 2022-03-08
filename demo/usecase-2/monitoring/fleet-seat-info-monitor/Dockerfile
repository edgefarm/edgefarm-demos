FROM python:3.9.4-slim-buster AS builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends make gcc curl build-essential
WORKDIR /project
COPY . /project
RUN make install_requirements

FROM python:3.9.4-slim-buster

WORKDIR /app
COPY --from=builder /project/src /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

ARG VERSION
ADD https://raw.githubusercontent.com/edgefarm/train-simulation/${VERSION}/demo/usecase-2/schemas/system_event.avsc \
    https://raw.githubusercontent.com/edgefarm/train-simulation/${VERSION}/demo/usecase-2/schemas/system_status.avsc \
    https://raw.githubusercontent.com/edgefarm/train-simulation/${VERSION}/demo/usecase-2/schemas/timestamp.avsc \
    /app/schemas/

ENV SCHEMA_PATH=/app/schemas
CMD [ "python3", "-u", "./main.py" ]
