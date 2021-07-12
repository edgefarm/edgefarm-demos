# edgefarm demo applications for train-simulator

This folder contains demo applications that work with the outputs of the [simulator](./simulator/README.md) to run on edge devices or in edgefarm's cloud
runtime.

* `environment/temperature-to-ads`: (edge) Read temperature data published by the simulator and foward it to edgefarm application data service (ADS).
* Seat-reservation system simulation with monitoring:
    * `passenger-info`:
        * `seat-info-proxy`: (cloud) Read seat reservations from database and provide it to `seat-info-forwarder` on request.
        * `seat-info-forwarder`: (edge) Forward seat-reservation requests from the simulator to the `seat-info-proxy` and return results to the simulator.
    * `monitoring`: Monitors the `seat-reservation` process.
        * `fleet-seat-info-monitor`: (cloud) Monitors the `seat-info-proxy` and the `train-seat-info-monitor` of each train and provides the status to ADS.
        * `train-seat-info-monitor`: (edge) Monitors the simulator passenger information system and reports the results to `fleet-seat-info-monitor`.

Those demo applicatios are written in python3.

## Usage

The `deploy` folder contains deployment manifests.

* `basis.yaml`: Manifest for the base modules `ads-node-module` and `alm-mqtt-module`.
    * Modify `<IP>` in the `MQTT_SERVER` variable to match the IP address of the MQTT broker of your simulator
* `temperature-to-ads.yaml`: Manifest for the `temperature-to-ads` module
* `seat-info-mon.yaml` and `seat-info.yaml`: Manifests for the seat-reservation edmo.

For the manifests containing the demo applications, modify the docker image's tag for the correct version of the application image.
You can either build your own docker image if you like to modify this demo. For this see the [building section](#building-yourself) of this Readme.

Apply the application using the edgefarm cli. You must deploy the `basis` and at least one of the application manifests.

```bash
edgefarm login
cd train-simulation/deploy
edgefarm alm apply -f basis.yaml
edgefarm alm apply -f <application>.yaml
```

Log in to the edge device and wait until the application has been deployed.
You can see see events coming in using

```bash
ssh root@<device IP>
docker logs <application-name><module-name> -f
```
