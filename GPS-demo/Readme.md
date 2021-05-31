# GPS-demo

*Note: this demo is still WIP*

This demo demonstrates the complete stack from the sensor (GPS) on the device to data in the cloud.

It takes the data from the alm-location-module, converts it to ADS_DATA schema and pushe it towards ads-node module.

## Usage

Deploy the manifest to your edgefarm device using

```
# deploy
# Note: edgefarm login must be performed prior applying manifests
$ edgefarm alm apply -f deploy/base.yaml
$ edgefarm alm apply -f deploy/gps-demo.yaml
```
