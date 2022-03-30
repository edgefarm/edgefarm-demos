#!/bin/bash


# Just post some gps coordiantes to the service
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'


# Register two sides
nats pub -s nats://localhost:4222 site.register '{"id":"site1","zero":{"lat":49.55552758496568,"lng":11.079950588826692},"area":[{"lat":49.55552758496568,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.083815851373487},{"lat":49.55552758496568,"lng":11.083815851373487}]}'
nats pub -s nats://localhost:4222 site.register '{"id":"site2","area":[{"lat":49.40417984351719,"lng":11.034056694994286},{"lat":49.41067606108498,"lng":11.034056694994286},{"lat":49.41067606108498,"lng":11.059848222803144},{"lat":49.40417984351719,"lng":11.059848222803144}],"zero":{"lat":49.40417984351719,"lng":11.034056694994286}}'


# # Just post some gps coordiantes to the service
# nats pub -s nats://localhost:4222 test test_leaf2
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1

# now enter a site
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
nats pub -s nats://localhost:4222 train.tracelet '{"site-id":"site2","y":34,"x":34,"train-id":"train1"}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
nats pub -s nats://localhost:4222 train.tracelet '{"site-id":"site2","y":34,"x":34,"train-id":"train1"}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
nats pub -s nats://localhost:4222 train.tracelet '{"site-id":"site2","y":34,"x":34,"train-id":"train1"}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
nats pub -s nats://localhost:4222 train.tracelet '{"site-id":"site2","y":34,"x":34,"train-id":"train1"}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
nats pub -s nats://localhost:4222 train.tracelet '{"site-id":"site2","y":34,"x":34,"train-id":"train1"}'

# leave the site
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1
nats pub -s nats://localhost:4222 train.gps '{"id":"train1","coordinates":{"lat":11.082579671225771,"lng":49.444529778349235}}'
sleep 1