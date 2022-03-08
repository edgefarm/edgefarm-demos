# Local development environment

Local development environment for edgefarm train simulation.

## How to run

Clone this repository and run the simulation environment with docker-compose.

> Note: Get latest version of docker-compose for ARM from [github](https://github.com/linuxserver/docker-docker-compose/releases).

Start Train Simulation locally:
```bash
git clone https://github.com/edgefarm/train-simulation.git
cd train-simulation/simulator
docker-compose up -d
```

To startup EdgeFarm Service Modules it is required to copy `example.kafka.env` to `.kafka.env` and insert the values for `KAFKA_ADDRESS` and `KAFKA_PASSWORD`.

> Note: If using a Train Simulator running on another device, it is required to change `MQTT_SERVER=mosquitto:1883` in `docker-compose.yaml` to the IP adress of the device, e.g. `MQTT_SERVER=192.168.178.15:1883`.

Afterwarts, startup the Sevices using docker-compose:
```
cd ../dev
docker-compose up -d
```

### Start example application with docker
Build docker image:
```
cd ../usecase-1/push-temperature
docker build -t ci4rail/push-temperature --build-arg VERSION=main .
```

Run image:
```
docker run --network simulator_edgefarm-simulator ci4rail/push-temperature:latest
```

### Start example application with python
Install Python dependencies:
```
cd ../usecase-1/push-temperature
pip3 install -r requirements.txt
```

Start example application:
```
cd src
python3 main.py
```
