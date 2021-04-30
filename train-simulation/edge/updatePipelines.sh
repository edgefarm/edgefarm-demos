#!/bin/bash
PROJECT=train-simulator-edge-demo
fly -t prod set-pipeline -p ${PROJECT} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml
