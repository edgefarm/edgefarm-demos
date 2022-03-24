# fleet-monitor
This is a node-red based demo backoffice to simulate an existing cloud endpoint on customers side for fleet-monitor visualization. 

## How to run

**Pre-Conditions:**
* [The usecase-4 application is up and running](../../../demo/usecase-4/README.md)

Get nats credentials required for data export.

```bash
kubectl get secret -n train-location -o yaml train-location.receive-position -o jsonpath='{.data.train-location-network\.creds}' | base64 --decode > creds/fleet-monitor.creds
```

Run the simulation environment with docker-compose.

```bash
cd simulations/vehicles/train
docker-compose up -d
```

Next go to Node-Red's web UI [http://localhost:1881](http://localhost:1881) to start and modify the simulation.

You also can view the dashboard for the simulation [http://localhost:1881/ui](http://localhost:1881/ui)

> Note: Get latest version of docker-compose for ARM from [github](https://github.com/linuxserver/docker-docker-compose/releases).