# train-simulation

[![train-simulation](https://github.com/edgefarm/train-simulation/actions/workflows/train-simulation.yaml/badge.svg)](https://github.com/edgefarm/train-simulation/actions/workflows/train-simulation.yaml)

Fictitious demo environment to illustrate the possibilities of EdgeFarm with practical examples.

The environment has no ambition to build a train simulation as accurate as possible, but serves
much more as a playground for small POC's or easily comprehensible demo's.

The demos cover data acquisition, pre-processing, data transport and transmission to external systems.

## Usage

* [Start the simulator](simulator/README.md)
* [Get the EdgeFarm CLI](https://github.com/edgefarm/edgefarm-cli/releases)
* [Deploy the basis manifest](basis/README.md)
* Select a use case and try it:
  * [usecase-1](demo/usecase-1/README.md): Read temperature data published by the simulator and foward it to EdgeFarm.data
  * [usecase-2](demo/usecase-2/README.md): Seat-reservation system simulation with monitoring
  * [usecase-3](demo/usecase-3/README.md): Detect peaks in the vibration signal, map it to a GPS location and forward it to EdgeFarm.data
  * [usecase-4](demo/usecase-4/README.md): Train transmitts GPS coordinates to cloud to enable train position observation from Backoffice

## Building yourself

**Note: this is tested with linux kernel >= 5.0.0 and is not guaranteed to work with a lower kernel version!**

### Setup

In order to build the demo docker images, you need to have docker installed on your system.
You can modify the demos and build the docker image yourself using a tool called [dobi](https://github.com/dnephin/dobi).
There is no need to download `dobi` by manually. The wrapper script `dobi.sh` will handle everything for you.
To specify the location of the docker image, you can modify the variable `DOCKER_REGISTRY` in the file `default.env`.

Once you've changed you should run `docker login <your-registry>` to allow pushing to your registry.
If you are using docker hub, login with `docker login`.

### Building

To see a list of all build targets, run
```bash
./dobi.sh
```

To build the docker images run
```bash
./dobi.sh build-and-push-<application-name>
```

The build job registers `qemu-user-static` to run programs for foreign CPU architectures like `arm64` or `arm`.

Once the build has finished, your docker images are located at the speficied docker registry.

## Cleaning up

You can cleanup `qemu-user-static` using `./dobi.sh uninstall-qemu-user-static`.

To check if all qemu emulators have been removed successful, please run `./dobi.sh check-qemu-user-static`
