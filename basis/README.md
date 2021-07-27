# base

This directory contains the basis deplyoment manifest, that deploys the EdgeFarm service modules required for all use cases.

Modify `<IP>` in the `MQTT_SERVER` variable to match the IP address of the MQTT broker of your simulator.

Deploy the manifest `basis.yaml` using the EdgeFarm CLI:
```bash
# Note: edgefarm login must be performed prior applying manifests
edgefarm applications apply -f basis.yaml
```
