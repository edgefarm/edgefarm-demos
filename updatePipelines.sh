#!/bin/bash

IMAGE_BASENAME=gps-to-ads-app
CONTEXT=GPS-demo/gps-to-ads-app/src
fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}


IMAGE_BASENAME=train-simulator-edge-app
CONTEXT=train-simulation/edge/src
fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}
