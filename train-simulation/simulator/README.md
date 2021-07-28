# Simulator

This is the train-simulator for edgefarm. The simulation contains:
* Temperature simulation
* "Journey1" that replays data recorded on a regional train (location, acceleration, speed)
* "Seat reservation" provides a simulation of a passenger information system

The simulator publishes all its result to a MQTT `mosquitto` broker, that is started with the docker-compose command below, along with Node-Red.

## How to run

Clone this repository and run the simulation environment with docker-compose.

```bash
git clone https://github.com/edgefarm/edgefarm-demos.git
cd edgefarm-demos/train-simulation/simulator
docker-compose up -d
```

Next go to Node-Red's web UI [http://localhost:1880](http://localhost:1880) to start and modify the simulation.

You also can view the dashboard for the simulation [http://localhost:1880/ui](http://localhost:1880/ui)

> Note: Get latest version of docker-compose for ARM from [github](https://github.com/linuxserver/docker-docker-compose/releases).
