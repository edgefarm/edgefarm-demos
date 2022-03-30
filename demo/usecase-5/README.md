# usecase-4

This use case is located in the Journeys section in the train simulator. This one generates GPS data for a selected Track.

The Edge application subscribes to the respective topic and sends the data unmodified into the cloud.

The data can be viewed in the cloud simulation TrainSim - Fleet View. This shows the current position of the train and enables a watch on the position to track the movement.

## Usage

**Pre-Conditions:**
* [The train simulator is up and running](../simulations/vehicles/train/README.md)
* [kubectl is installed](https://kubernetes.io/docs/tasks/tools/#kubectl)

**Deploy use case application:**

`receive-position.yaml` is the deployment manifest of the use case. This contains a reference to the docker image of demo application. Modify the docker image's tag for the correct version of the application image. Change the `<IP>` in the `MQTT_SERVER` variable (Line 17) to match the IP address of the MQTT broker of your simulator.

You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.

Apply the application using kubectl.

```bash
kubectl apply -f demo/usecase-4/receive-position.yaml
```
Check the status of your application using the following command.

```bash
kubectl get pods -n train-location -o wide
```

The uploaded data can be visualized in [the backoffice simulator](../simulations/operations/fleet-monitor/README.md).