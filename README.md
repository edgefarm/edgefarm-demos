# train-simulation

[![train-simulation](https://github.com/edgefarm/train-simulation/actions/workflows/train-simulation.yaml/badge.svg)](https://github.com/edgefarm/train-simulation/actions/workflows/train-simulation.yaml)

The Train Simulator was developed to experience the complete data chain from the simulation of realistic train data, the recording in the edge device, the transfer to the cloud and the visualization in dashboards as well as the export to external data systems. The simulated data range from simple diagnostic data and train network messages to high-frequency measurement data. Furthermore the train simulator is able to interact with the device to transmit the current state of the simulation on request.

Therfore the repository contains the [train-simulator](./simulator/README.md) which generates the realistic train data. In addition to that there are demo use-cases contained that run demo-applications which run on edge devices or in edgefarm's cloud runtime, which use the generated data and interact with the train simulator. These demo applicatios are written in python3.

## Usage

* [Start the simulator](simulator/README.md)
* [Get the EdgeFarm CLI](https://github.com/edgefarm/edgefarm-cli/releases)
* [Deploy the basis manifest](basis/README.md)
* Select a use case and try it:
  * [usecase-1](usecase-1/README.md): Read temperature data published by the simulator and foward it to EdgeFarm.data
  * [usecase-2](usecase-2/README.md): Seat-reservation system simulation with monitoring
  * [usecase-3](usecase-3/README.md): Detect peaks in the vibration signal, map it to a GPS location and forward it to EdgeFarm.data

## Building yourself

**Note: this is tested with linux kernel >= 5.0.0 and is not guaranteed to work with a lesser kernel version!**

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
