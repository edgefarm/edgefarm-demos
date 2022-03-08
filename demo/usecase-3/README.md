# usecase-3

This use case is located in the journey section in the simulator. This one generates vibration data in Z direction with irregular peaks every now and then. GPS positions linked to the vibratin data are also generated. The data is transmitted separately to the MQTT broker.

The Edge application subscribes to the respective topics and identifies the peaks, correlates peaks with GPS and time Information and sends these informations into the cloud.

The data can be viewed in the cloud on a Grafana Dashboard. The idetified peaks are displayed in a map and listed in a table.

## Usage

**Pre-Conditions:**
* [The simulator is up and running](../simulator/README.md)
* [EdgeFarm CLI installed](https://github.com/edgefarm/edgefarm-cli/releases)
* [Required EdgeFarm service modules deployed](../base/README.md)

**Deploy use case application:**

`vibration.yaml` is the deployment manifest of the use case. This contains a reference to the docker images of demo application. Modify the docker image's tag for the correct version of the application image.
You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.

Apply the application using the edgefarm cli. You must deploy the `basis` and at least one of the application manifests.

```bash
# Note: edgefarm login must be performed prior applying manifests
edgefarm applications apply -f vibration.yaml
```

Check status of deployment:
```bash
edgefarm applications get deployments -o wide -m
```
