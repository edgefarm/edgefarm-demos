# Train Simulation - Seat Info Forwarder

[![CI](https://concourse.ci4rail.com/api/v1/teams/edgefarm/pipelines/seat-info-forwarder/jobs/build-seat-info-forwarder/badge)](https://concourse.ci4rail.com/teams/edgefarm/pipelines/seat-info-forwarder)

This demo application is written in python3 and connects to `alm-mqtt-module` and subscribes to the MQTT topic `pis/req/seatRes`. The request is forwarded to the cloud module by transforming the message into avro schema and request reply the message to the nats subject `pis.seatRes`. The received data contains the reserved seats and is replied to the MQTT topic `pis/res/seatRes`.

## Usage
Modify the `../../deploy/base.yaml` to match the `MQTT_SERVER` for from where the simulation is reachable.
In `../../deploy/seat-info.yaml` modify the docker image's tag for the correct version of `seat-info-forwarder`.
You can either build your own docker image if you like to modify this demo. For this see the [building section](#building-yourself) of this Readme.

Apply the application using the edgefarm cli.

```bash
edgefarm login
edgefarm alm apply -f ../../deploy/base.yaml
edgefarm alm apply -f ../../deploy/seat-info.yaml
```

Log in to the device and wait until the application has been deployed.
You can see see events coming in using

```bash
ssh root@<device IP>
docker logs train-simulator-demo_seat-info-forwarder -f
```

## Building yourself

**Note: this is tested with linux kernel >= 5.0.0 and is not guaranteed to work with a lesser kernel version!**

### Setup

In order to build the demo docker image, you need to have docker installed on your system.
You can modify the demo located in `src/` and build the docker image yourself using a tool called [dobi](https://github.com/dnephin/dobi).
There is no need to download `dobi` by manually. The wrapper script `dobi.sh` will handle everything for you.
To specify the location of the docker image, you can modify the variable `DOCKER_REGISTRY` in the file `default.env`.

Once you've changed you should run `docker login <your-registry>` to allow pushing to your registry.
If you are using docker hub, login with `docker login`.

### Building

In order to build the docker images for several architectures simply run

```bash
./dobi.sh build-and-push-demo-image
```

The build job registers `qemu-user-static` to run programs for foreign CPU architectures like `arm64` or `arm`.

Once the build has finished, your docker images are located at the speficied docker registry.

*Note: the docker images are build for amd64 and arm64 architectures. If you need to build for another architecture, please adapt the job `build-and-push-demo-image` in `dobi.yaml`.*

## Cleaning up

You can cleanup `qemu-user-static` using `./dobi.sh uninstall-qemu-user-static`.

To check if all qemu emulators have been removed successful, please run `./dobi.sh check-qemu-user-static`
