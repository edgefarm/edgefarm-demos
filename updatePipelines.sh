#!/bin/bash

# For each concourse pipeline, create an entry in IMAGES and a corresponding entry in CONTEXTS
#  entry in IMAGES = the name of the docker image to build, without specifying the repository and tag.
#                    This also defines the name of the pipeline in concourse (demo-<image-name>)
#  entry in CONTEXTS = The docker build context (path to the directory within this repo)
#

IMAGES=(
  gps-to-ads-app
  train-simulator-edge-app
  fleet-seat-info-monitor
  train-seat-info-monitor
  seat-info-forwarder
  seat-info-proxy
  temperature-to-ads
  )

CONTEXTS=(
  GPS-demo/gps-to-ads-app/src
  train-simulation/edge/src
  train-simulation/monitoring/seat-reservation/fleet-seat-info-monitor
  train-simulation/monitoring/seat-reservation/train-seat-info-monitor
  train-simulation/passenger-info/seat-info-forwarder
  train-simulation/passenger-info/seat-info-proxy
  train-simulation/environment/temperature-to-ads
)

for i in "${!IMAGES[@]}"; do
  IMAGE_BASENAME=${IMAGES[i]}
  CONTEXT=${CONTEXTS[i]}
  echo "***********"
  echo "setting pipelines for ${IMAGE_BASENAME}, context=${CONTEXT}"
  echo "***********"

  fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
    -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

  fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
    -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

done
