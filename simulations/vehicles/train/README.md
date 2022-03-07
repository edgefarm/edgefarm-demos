# train simulation

This is a node-red based demo environment to simulate different parts of a train and a trains life.

## simulations

The simulation publishes all data to a MQTT `mosquitto` broker, that is started with the docker-compose command below, along with Node-Red.

### Train's Climate

Temperature simulation

### Journeys

"Journey1" that replays data recorded on a regional train (location, acceleration, speed)

### Passenger information system

"Seat reservation" provides a simulation of a passenger information system

## How to run

Clone this repository and run the simulation environment with docker-compose.

```bash
cd train-simulation/simulator
docker-compose up -d
```

Next go to Node-Red's web UI [http://localhost:1880](http://localhost:1880) to start and modify the simulation.

You also can view the dashboard for the simulation [http://localhost:1880/ui](http://localhost:1880/ui)

> Note: Get latest version of docker-compose for ARM from [github](https://github.com/linuxserver/docker-docker-compose/releases).
