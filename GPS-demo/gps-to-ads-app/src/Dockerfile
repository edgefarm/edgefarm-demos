FROM python:3.9.4-slim-buster AS builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends make gcc curl build-essential
WORKDIR /app
COPY . /app
RUN make install_requirements

FROM python:3.9.4-slim-buster

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
CMD [ "python3", "-u", "./main.py" ]
