# usecase-1

This use case is located in the climate conditions section in the simulator. This one generates temperature data at a configurable interval.

The Edge application subscribes to the respective topic and sends the data unmodified into the cloud.

The data can be viewed in the cloud on a Grafana Dashboard. The temperature profile can be viewed in a panel.

## Usage

**Pre-Conditions:**
* [The simulator is up and running](../simulator/README.md)
* [EdgeFarm CLI installed](https://github.com/edgefarm/edgefarm-cli/releases)
* [Required EdgeFarm service modules deployed](../base/README.md)

**Deploy use case application:**

`hvac.yaml` is the deployment manifest of the use case. This contains a reference to the docker image of demo application. Modify the docker image's tag for the correct version of the application image.
You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.

Apply the application using the edgefarm cli. You must deploy the `basis` and at least one of the application manifests.

```bash
# Note: edgefarm login must be performed prior applying manifests
edgefarm applications apply -f hvac.yaml
```

Check status of deployment:
```bash
edgefarm applications get deployments -o wide -m
```
